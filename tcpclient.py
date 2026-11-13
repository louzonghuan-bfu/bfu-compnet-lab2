"""tcpclient.py —— 教材第 2 章 TCP 客户端

实验 2 / Part A2、S2（顺序颠倒）、S3（强杀客户端）。
注意和 udpclient.py 的差别：这里必须 connect()，建立连接后才能 send/recv。

运行：python3 tcpclient.py <服务器IP> [端口] [要发送的文字]
"""
from socket import *
import sys

serverName = sys.argv[1] if len(sys.argv) > 1 else '192.168.28.131'
serverPort = int(sys.argv[2]) if len(sys.argv) > 2 else 5201
sentence = sys.argv[3] if len(sys.argv) > 3 else 'hello tcp from host'

clientSocket = socket(AF_INET, SOCK_STREAM)

# ★ 就是这一行：TCP 客户端必须先 connect()，它触发三次握手；
#   而 UDP 客户端没有这一步，直接把地址写在 sendto() 里。
clientSocket.connect((serverName, serverPort))

clientSocket.send(sentence.encode())

modifiedSentence = clientSocket.recv(1024)
print('From Server:', modifiedSentence.decode().strip())

clientSocket.close()
