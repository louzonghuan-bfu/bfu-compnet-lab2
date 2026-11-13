"""udpclient.py —— 教材第 2 章 UDP 客户端

实验 2 / Part A1：和 udpserver.py（端口 5201）互发一句话。
注意：这里没有 connect()，sendto 时把 (服务器地址, 端口) 直接写在参数里。

运行：python3 udpclient.py <服务器IP> [端口] [要发送的文字]
"""
from socket import *
import sys

serverName = sys.argv[1] if len(sys.argv) > 1 else '192.168.28.131'
serverPort = int(sys.argv[2]) if len(sys.argv) > 2 else 5201
message = sys.argv[3] if len(sys.argv) > 3 else 'hello udp from host'

# 只创建套接字，不 connect —— 这就是和 TCP 客户端的第一个差别
clientSocket = socket(AF_INET, SOCK_DGRAM)

# 发送：地址和端口在 sendto 里给出（每次都可以发给不同目标）
clientSocket.sendto(message.encode(), (serverName, serverPort))
print(f"[client] sent to {serverName}:{serverPort}: {message}")

# 接收回送：recvfrom 同时返回数据和对端地址
modifiedMessage, serverAddress = clientSocket.recvfrom(2048)
print(f"[client] received from {serverAddress[0]}:{serverAddress[1]}: {modifiedMessage.decode()}")

clientSocket.close()
