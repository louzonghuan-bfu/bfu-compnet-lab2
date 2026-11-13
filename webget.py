#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""webget.py —— 实验 2 / Part D：手搓一个 HTTP 客户端（只允许使用标准库 socket）

用法：
    python3 webget.py <host> <path> [port]
例：
    python3 webget.py www.bjfu.edu.cn / 80
    python3 webget.py example.com /index.html 80

设计要点（对应报告 T1~T5）：
1. T1 recv 循环：recv 的返回值有两种“结束信号”，本程序两种都处理
   - 响应头里有 Content-Length：按长度收够为止（长度是 body 的字节数，不含头）；
   - 没有 Content-Length：只能收到对端关闭连接为止（recv 返回 b''），
     所以请求里必须带 "Connection: close"，否则服务器保持连接、recv 会一直等。
   同时 settimeout(10) 兜底，避免坏服务器把程序挂死。
2. T2 解析：以空行 "\\r\\n\\r\\n" 切开状态行+头 与 body；body 必须用二进制 "wb" 写文件，
   文本模式会按编码解码、替换非法字节，图片/压缩包这类二进制内容会被破坏。
3. T3 参数化：host、path、port 全部来自命令行，不在代码里写死。

GitHub 仓库：https://github.com/<你的用户名>/bfu-compnet-lab2
（提交前把上面这行改成你自己的公有仓库地址，课程要求仓库地址写进源码注释）
"""

import socket
import sys

TIMEOUT = 10          # T1：防止挂在坏服务器上
RECV_SIZE = 4096      # 每次 recv 的缓冲区大小


def usage_and_exit():
    """T3：参数不足时打印用法并退出。"""
    print("用法: python3 webget.py <host> <path> [port]")
    print("示例: python3 webget.py www.bjfu.edu.cn / 80")
    sys.exit(1)


def build_request(host, path, port):
    """构造一个最小但合法的 HTTP/1.1 请求。

    必须带 Connection: close —— 这样服务器在响应完就会关闭连接，
    我们才能在“没有 Content-Length”时靠 recv 返回 b'' 判断结束（T1 的第二种结束条件）。
    """
    if not path.startswith('/'):
        path = '/' + path
    lines = [
        f"GET {path} HTTP/1.1",
        f"Host: {host}",
        "User-Agent: webget-lab2/1.0",
        "Accept: */*",
        "Connection: close",      # ★ 关键：请求对端在响应后关闭连接
        "",
        "",
    ]
    return "\r\n".join(lines).encode("ascii")


def split_headers(buf):
    """把缓冲区按空行切成 (头部字节, body 字节)；头部还没收全时返回 (None, b'')。"""
    idx = buf.find(b"\r\n\r\n")
    if idx == -1:
        return None, b""
    return buf[:idx], buf[idx + 4:]


def parse_headers(header_bytes):
    """解析状态行和头部字段，返回 (状态行, 状态码, 头字典列表)。"""
    # 头部一律按 iso-8859-1 解码：HTTP 头是 ASCII 语义，这样不会因为个别字节报错
    text = header_bytes.decode("iso-8859-1")
    lines = text.split("\r\n")
    status_line = lines[0]
    parts = status_line.split(" ", 2)
    status_code = int(parts[1]) if len(parts) > 1 and parts[1].isdigit() else -1

    headers = []
    for line in lines[1:]:
        if not line:
            continue
        if ":" in line:
            name, value = line.split(":", 1)
            headers.append((name.strip(), value.strip()))
    return status_line, status_code, headers


def get_header(headers, name):
    """不区分大小写地取某个头部的值。"""
    lname = name.lower()
    for k, v in headers:
        if k.lower() == lname:
            return v
    return None


def main():
    if len(sys.argv) < 3:
        usage_and_exit()

    host = sys.argv[1]
    path = sys.argv[2]
    port = int(sys.argv[3]) if len(sys.argv) > 3 else 80

    request = build_request(host, path, port)

    # 只用标准库 socket：TCP 套接字
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(TIMEOUT)   # T1：10 秒超时，防止 recv 永久阻塞

    print(f"==> connect {host}:{port}")
    s.connect((host, port))
    print(f"==> request sent:\n{request.decode('ascii')}")

    s.sendall(request)      # sendall：保证整段请求全部发出去

    recv_count = 0          # T1 验收：recv 调用次数
    recv_sizes = []         # T1 验收：每次收到的字节数
    buf = bytearray()       # 已经收到的全部字节
    header_bytes = None     # 头部（收全后才有值）
    status_line = ""
    status_code = -1
    headers = []
    content_length = None   # 响应头里的 Content-Length（如果有）

    # ---------------- T1：recv 循环 ----------------
    # 结束条件只有两种：
    #   (a) 已收到 "头部 + Content-Length 字节的 body"  → break
    #   (b) 对端关闭连接，recv 返回 b''                  → break
    # 另外用 settimeout 兜住“服务器既不关连接、也没有 Content-Length”的坏情况。
    while True:
        # 先判断是否已经收够（针对有 Content-Length 的情况）
        if header_bytes is not None and content_length is not None:
            if len(buf) - len(header_bytes) - 4 >= content_length:
                break

        try:
            data = s.recv(RECV_SIZE)     # ★ recv 必须带缓冲区大小参数（附录 B 常见坑 1）
        except socket.timeout:
            print(f"!! recv 超时（>{TIMEOUT}s），按“对端不再发送数据”处理，退出循环")
            break

        if not data:
            # 结束条件 (b)：对端关闭连接，TCP 收到 FIN，recv 返回空字节串
            print("-- 收到 b''（对端关闭连接），recv 循环结束")
            break

        recv_count += 1
        recv_sizes.append(len(data))
        buf.extend(data)
        print(f"-- recv #{recv_count}: {len(data)} bytes")

        if header_bytes is None:
            header_bytes, _ = split_headers(bytes(buf))
            if header_bytes is not None:
                status_line, status_code, headers = parse_headers(header_bytes)
                cl = get_header(headers, "Content-Length")
                if cl is not None and cl.isdigit():
                    content_length = int(cl)
                    print(f"-- headers complete: status {status_code}, Content-Length={content_length}")
                else:
                    print(f"-- 头部收全：状态码 {status_code}，无 Content-Length，"
                          f"只能收到对端关闭为止")

    s.close()

    # ---------------- T2：拆分状态行 / 头 / body ----------------
    header_bytes, body = split_headers(bytes(buf))
    if header_bytes is None:
        print("!! no complete HTTP response header (connection reset?)")
        print(bytes(buf[:200]))
        return

    status_line, status_code, headers = parse_headers(header_bytes)
    if content_length is not None:
        body = body[:content_length]     # 只保留 Content-Length 指定的字节

    print("\n================ response ================")
    print(f"status line: {status_line}")
    print(f"status code: {status_code}")
    print("headers:")
    for k, v in headers:
        print(f"  {k}: {v}")

    # body 用二进制模式写文件：文本模式会按编码解码，二进制内容（图片等）会被破坏
    out_name = "webget_body.bin"
    with open(out_name, "wb") as f:
        f.write(body)
    print(f"body size: {len(body)} bytes, written to {out_name} (binary mode wb)")

    # ---------------- T1 验收：recv 统计 ----------------
    print("\n================ recv stats ================")
    print(f"recv calls: {recv_count}")
    print(f"bytes per call: {recv_sizes}")
    print(f"total: {sum(recv_sizes)} bytes")


if __name__ == "__main__":
    main()

