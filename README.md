# 实验 2：HTTP 客户端与 TCP、UDP 协议分析 —— 代码说明

学号：251006111　姓名：娄宗欢

## 文件说明

| 文件 | 说明 |
|---|---|
| `webget.py` | 自己实现的 HTTP 客户端（Part D）。只用标准库 socket，支持 `python3 webget.py <host> <path> [port]`，循环 recv 直到收完，解析状态行/响应头/body，body 以二进制写文件，并统计 recv 次数与每次字节数 |
| `udpserver.py` | 教材第 2 章 UDP 服务器，监听端口改为 5201，把收到的一行转大写回送 |
| `udpclient.py` | 教材第 2 章 UDP 客户端（无 connect，直接 sendto） |
| `tcpserver.py` | 教材第 2 章 TCP 服务器（accept 后 recv 一次，转大写回送，close） |
| `tcpclient.py` | 教材第 2 章 TCP 客户端（必须 connect） |

## 运行方法

```bash
# UDP
python3 udpserver.py 5201
python3 udpclient.py 127.0.0.1 5201 "hello udp"

# TCP
python3 tcpserver.py 5201
python3 tcpclient.py 127.0.0.1 5201 "hello tcp"

# HTTP 客户端
python3 webget.py www.bjfu.edu.cn / 80
```

## 抓包

`tcpdump -i lo -w x.pcap "tcp port 5201"`（或 Wireshark 抓 loopback）。
非知名端口请用端口过滤（`tcp.port == 5201` / `udp.port == 5201`），不要直接用 `tcp`/`udp` 过滤，
否则协议可能被识别为 LLC 而漏包。

## GitHub 仓库

https://github.com/<你的用户名>/bfu-compnet-lab2
（提交前把这里和 `webget.py` 文件头部注释里的地址改成你自己的公有仓库地址）
