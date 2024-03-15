import socket
import threading

# Dictionary to hold connected TCP clients: {client_id: conn}
tcp_clients = {}
lock = threading.Lock()

def broadcast_message(sender_id, message):
    with lock:
        for client_id, conn in tcp_clients.items():
            if client_id != sender_id:
                try:
                    conn.sendall(message.encode())
                except Exception as e:
                    print(f"Error sending message to {client_id}: {e}")

def tcp_client_handler(conn, addr, client_id):
    print(f"TCP Connection from {addr} as Client {client_id}")
    try:
        with conn:
            while True:
                data = conn.recv(1024).decode()
                if not data:
                    break
                print(f"Received from Client {client_id}: {data}")
                broadcast_message(client_id, f"Client {client_id}: {data}")
    finally:
        with lock:
            del tcp_clients[client_id]
        print(f"TCP Connection with Client {client_id} closed")

def tcp_server(host, port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as tcp_sock:
        tcp_sock.bind((host, port))
        tcp_sock.listen()
        print(f"TCP server listening on {host}:{port}")
        while True:
            conn, addr = tcp_sock.accept()
            client_id = conn.recv(1024).decode()  # Expect the client to send their ID as the first message
            if client_id in tcp_clients:
                conn.sendall("ID already in use.".encode())
                conn.close()
                continue
            tcp_clients[client_id] = conn
            conn.sendall("Connected to the chat.".encode())
            tcp_thread = threading.Thread(target=tcp_client_handler, args=(conn, addr, client_id))
            tcp_thread.start()

def udp_server(host, port):
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as udp_sock:
        udp_sock.bind((host, port))
        print(f"UDP server listening on {host}:{port}")
        while True:
            data, addr = udp_sock.recvfrom(1024)
            print(f"UDP message from {addr}: {data.decode()}")
            udp_sock.sendto(data, addr)  # Echo back the received data

if __name__ == "__main__":
    host = '127.0.0.1'
    tcp_port = 12345
    udp_port = 12346

    # Starting TCP and UDP servers in separate threads
    tcp_thread = threading.Thread(target=tcp_server, args=(host, tcp_port))
    udp_thread = threading.Thread(target=udp_server, args=(host, udp_port))

    tcp_thread.start()
    udp_thread.start()

    tcp_thread.join()
    udp_thread.join()
