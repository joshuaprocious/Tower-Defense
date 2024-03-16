import socket
import threading
import time
import datetime
import json

# Global storage for TCP client connections and UDP client addresses
tcp_clients = {}
udp_clients = {}  # Use a set to store unique client addresses
chat_history = {}
lock = threading.Lock()

def broadcast_message(sender_id, message, is_udp=False, sender_addr=None):
    with lock:
        # Prepare the message as a JSON string
        json_message = json.dumps({'client_id': sender_id, 'message': message})
        if is_udp == False:
            # Broadcast to TCP clients
            for client_id, conn in tcp_clients.items():
                if client_id != sender_id:  # Exclude the sender for TCP
                    try:
                        conn.sendall(json_message.encode())  # Encode JSON string to bytes before sending
                    except Exception as e:
                        print(f"Error broadcasting to TCP client {client_id}: {e}")
        
        # Broadcast to UDP clients, if the message comes from a UDP client
        if is_udp:
            for addr in udp_clients.keys():
                if addr != sender_addr:  # Exclude the sender for UDP
                    try:
                        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                        sock.sendto(json_message.encode(), addr)  # Encode JSON string to bytes before sending
                        sock.close()
                    except Exception as e:
                        print(f"Error broadcasting to UDP client {addr}: {e}")
        # add chat to chat_history dictionary
        protocol = "UDP" if is_udp else "TCP"
        client_key = sender_addr if is_udp else sender_id
        if client_key not in chat_history:
            chat_history[client_key] = []
        timestamp_ns = time.time_ns()
        chat_history[client_key].append((timestamp_ns, f"{protocol}: {message}"))

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
            # decode json message
            decoded_message = json.loads(data)  # Decode message from JSON
            client_id = decoded_message['client_id']
            message = decoded_message['message']
            print(f"Message from TCP Client {client_id}: {message}")
            broadcast_message(client_id, f"TCP: Client {client_id}: {message}")
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
            # decode json message
            decoded_message = json.loads(data.decode())  # Decode message from JSON
            message = f"{decoded_message['client_id']}: {decoded_message['message']}"
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

def server_commands():
    while True:
        cmd = input("Server command: ")
        if cmd == "print chat":
            with lock:
                for client, messages in chat_history.items():
                    print(f"Chat history for {client}:")
                    for timestamp_ns, message in messages:
                        time_str = datetime.datetime.fromtimestamp(timestamp_ns / 1e9).strftime('%Y-%m-%d %H:%M:%S.%f')
                        print(f"  {time_str} - {message}")
                    print("----------")

if __name__ == "__main__":
    HOST = '127.0.0.1'
    TCP_PORT = 12345
    UDP_PORT = 12346
    threading.Thread(target=tcp_server, args=(HOST, TCP_PORT)).start()
    threading.Thread(target=udp_server, args=(HOST, UDP_PORT)).start()
    threading.Thread(target=server_commands).start()

    # Simple wait mechanism to prevent the script from exiting
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("Server is shutting down...")
