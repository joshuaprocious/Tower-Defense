import socket
import threading
import time
import datetime

# Global storage for TCP client connections and UDP client addresses
tcp_clients = {}
udp_clients = {}  # Use a set to store unique client addresses
lock = threading.Lock()

def broadcast_message(sender_id, message, is_udp=False, sender_addr=None):
    with lock:
        # Broadcast to TCP clients
        for client_id, conn in tcp_clients.items():
            if client_id != sender_id:  # Exclude the sender for TCP
                try:
                    conn.sendall(message.encode())
                except Exception as e:
                    print(f"Error broadcasting to TCP client {client_id}: {e}")
        
        # Broadcast to UDP clients, if the message comes from a UDP client
        if is_udp:
            for addr in udp_clients.keys():
                if addr != sender_addr:  # Exclude the sender for UDP
                    try:
                        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                        sock.sendto(message.encode(), addr)
                        sock.close()
                    except Exception as e:
                        print(f"Error broadcasting to UDP client {addr}: {e}")

def handle_tcp_client(conn, addr):
    client_id = conn.recv(1024).decode()
    with lock:
        tcp_clients[client_id] = conn
    print(f"TCP Client {client_id} connected from {addr}")
    try:
        while True:
            data = conn.recv(1024).decode()
            if not data:
                break
            broadcast_message(client_id, f"TCP: Client {client_id}: {data}")
    finally:
        with lock:
            del tcp_clients[client_id]
        conn.close()

def udp_server(host, udp_port):
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as udp_sock:
        udp_sock.bind((host, udp_port))
        print("UDP server listening...")
        while True:
            data, addr = udp_sock.recvfrom(1024)
            with lock:
                # Update or add the client with their last message timestamp
                udp_clients[addr] = {'last_message_time': datetime.datetime.now()}
            message = data.decode()
            print(f"Message from UDP Client {addr}: {message}")
            broadcast_message(None, f"UDP: {message}", is_udp=True, sender_addr=addr)

def tcp_server(host, tcp_port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as tcp_sock:
        tcp_sock.bind((host, tcp_port))
        tcp_sock.listen()
        print("TCP server listening...")
        while True:
            conn, addr = tcp_sock.accept()
            threading.Thread(target=handle_tcp_client, args=(conn, addr)).start()

if __name__ == "__main__":
    HOST = '127.0.0.1'
    TCP_PORT = 12345
    UDP_PORT = 12346
    threading.Thread(target=tcp_server, args=(HOST, TCP_PORT)).start()
    threading.Thread(target=udp_server, args=(HOST, UDP_PORT)).start()

    # Simple wait mechanism to prevent the script from exiting
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("Server is shutting down...")
