import socket

def handle_client(conn):
    with conn:
        print('Connected by', addr)
        while True:
            data = conn.recv(1024)
            if not data:
                break
            conn.sendall(data)

host = '127.0.0.1'
port = 65432
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.bind((host, port))
    s.listen()
    print(f"TCP server listening on {host}:{port}")
    conn, addr = s.accept()
    handle_client(conn)
