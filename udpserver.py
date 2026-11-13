"""udpserver.py —— 教材 Kurose & Ross《计算机网络：自顶向下方法》第 2 章 UDP 服务器

实验 2 / Part A1：监听端口由 12000 改为 5201。
server 收到 client 发来的一行小写英文，转成大写回送，并把收到的内容打印出来。

运行：python3 udpserver.py [监听端口]
"""
from socket import *

# A1 要求：端口从教材的 12000 改成 5201
serverPort = 5201
if len(__import__("sys").argv) > 1:
    serverPort = int(__import__("sys").argv[1])

serverSocket = socket(AF_INET, SOCK_DGRAM)
# 绑定本机所有网卡的 5201 端口（'' 表示 INADDR_ANY）
serverSocket.bind(('', serverPort))
print(f"The server is ready to receive on UDP port {serverPort}")

while True:
    # recvfrom 一次收一个数据报，同时拿到对端的 (IP, 端口)
    message, clientAddress = serverSocket.recvfrom(2048)
    text = message.decode()
    print(f"[server] received from {clientAddress[0]}:{clientAddress[1]}: {text}")
    modifiedMessage = text.upper()
    # UDP 是无连接的：回送时直接用刚才拿到的 clientAddress，不需要 accept/connect
    serverSocket.sendto(modifiedMessage.encode(), clientAddress)
