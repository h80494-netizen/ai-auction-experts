import socket

port = 8000
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
try:
    s.bind(("127.0.0.1", port))
    print(f"Port {port} is FREE! The backend server is NOT running!")
    s.close()
except socket.error as e:
    print(f"Port {port} is BUSY! The backend server is actively running! Error: {e}")
