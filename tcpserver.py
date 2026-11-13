"""tcpserver.py —— 教材第 2 章 TCP 服务器

实验 2 / Part A2、S1~S3。
server 在 5201 端口 listen，accept 一个连接，收一行文字，转大写回送，然后关闭连接。

运行：python3 tcpserver.py [监听端口]
"""
from socket import *
import sys

serverPort = int(sys.argv[1]) if len(sys.argv) > 1 else 5201

# SOCK_STREAM = TCP（面向连接、可靠字节流）
serverSocket = socket(AF_INET, SOCK_STREAM)
serverSocket.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
serverSocket.bind(('', serverPort))
# listen：把主动套接字变成被动套接字，1 是等待 accept 的队列长度
serverSocket.listen(1)
print(f"The server is ready to receive on TCP port {serverPort}", flush=True)

while True:
    # 三次握手由内核在这里完成；accept 返回的是一个全新的“已连接套接字”
    connectionSocket, addr = serverSocket.accept()
    print(f"[server] connection established with {addr[0]}:{addr[1]}", flush=True)

    # 教材原版：一次 recv 读一行（客户端发一行就停）
    sentence = connectionSocket.recv(1024).decode()
    print(f"[server] received: {sentence}", flush=True)

    capitalizedSentence = sentence.upper()
    connectionSocket.send(capitalizedSentence.encode())

    # 主动关闭：先发 FIN，进入 FIN_WAIT，随后由内核完成四次挥手
    connectionSocket.close()
