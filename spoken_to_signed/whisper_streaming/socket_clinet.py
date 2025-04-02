import socket

# 设置监听 IP 和端口
HOST = "0.0.0.0"  # 监听所有连接
PORT = 43008  # 监听的端口

# 创建 socket
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind((HOST, PORT))
server_socket.listen(1)

print(f"🚀 Listening for Pose Data on Port {PORT}...")

conn, addr = server_socket.accept()
print(f"✅ Connected to {addr}")

while True:
    data = conn.recv(1024)  # 接收 Pose 数据
    if not data:
        break  # 连接关闭时退出
    print("📨 Received Pose Data:", data.decode("utf-8"))

conn.close()
server_socket.close()


