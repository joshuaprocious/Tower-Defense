import socket
import threading
import json

def listen_udp_messages(udp_sock):
    while True:
        try:
            data, _ = udp_sock.recvfrom(1024)
            decoded_data = json.loads(data.decode())
            print(f"\nUDP: {decoded_data['message']}\nEnter your message: ", end='', flush=True)
        except Exception as e:
            print(f"\nError receiving UDP message: {e}")
            break

def listen_tcp_messages(sock):
    while True:
        try:
            data = sock.recv(1024).decode()
            if not data:
                break
            decoded_data = json.loads(data)
            print(f"\nTCP: {decoded_data['message']}\nEnter your message: ", end='', flush=True)
        except Exception as e:
            print(f"\nError receiving TCP message: {e}")
            break

def send_tcp_message(sock, client_id, message):
    encoded_message = json.dumps({'client_id': client_id, 'message': message}).encode()
    sock.sendall(encoded_message)

def send_udp_message(udp_sock, host, udp_port, client_id, message):
    encoded_message = json.dumps({'client_id': client_id, 'message': message}).encode()
    udp_sock.sendto(encoded_message, (host, udp_port))

def init_udp_socket(udp_listen_port):
    udp_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    # Optionally bind the client UDP socket to a specific port if needed
    udp_sock.bind(('', udp_listen_port))  # Bind to the specific port
    return udp_sock

def client(host, tcp_port, udp_port, client_id, udp_sock):
    # TCP Setup
    tcp_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    tcp_sock.connect((host, tcp_port))
    tcp_sock.sendall(client_id.encode())  # Send client ID right after connecting

    # Start listening threads
    threading.Thread(target=listen_tcp_messages, args=(tcp_sock,), daemon=True).start()
    threading.Thread(target=listen_udp_messages, args=(udp_sock,), daemon=True).start()

    protocol = "TCP"  # Default protocol
    print("Connected via TCP. Use '/udp' to switch to UDP, '/tcp' to switch back to TCP.")

    while True:
        message = input(f"{protocol}> ")
        if message.lower() == "/udp":
            protocol = "UDP"
            print("Switched to UDP. Use '/tcp' to switch back to TCP.")
        elif message.lower() == "/tcp":
            protocol = "TCP"
            print("Switched to TCP. Use '/udp' to switch to UDP.")
        else:
            if protocol == "TCP":
                send_tcp_message(tcp_sock, client_id, message)
            else:
                send_udp_message(udp_sock, host, udp_port, client_id, message)

if __name__ == "__main__":
    HOST = 'localhost'
    TCP_PORT = 12345
    UDP_PORT = 12346
    UDP_LISTEN_PORT = 12348  # Example port, adjust as necessary for your setup

    client_id = input("Enter your client ID (1-4): ").strip()
    udp_sock = init_udp_socket(UDP_LISTEN_PORT)
    client(HOST, TCP_PORT, UDP_PORT, client_id, udp_sock)
