# echo_server.py
import socket

host = '192.168.251.18'        # Symbolic name meaning all available interfaces
port = 11114 # Arbitrary non-privileged port
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind((host, port))
s.listen(1)
conn, addr = s.accept()
print('Connected by', addr)
data = conn.recv(1024).decode()
print("hello",data)
#while True:
       
    #if not data: break
    #conn.sendall(data)
conn.close()

