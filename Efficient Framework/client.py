import socket
import threading

def receive_messages(sock):
    while True:
        try:
            message = sock.recv(1024).decode()
            print(f"\n{message}\nEnter your message: ", end='', flush=True)
        except:
            print("\nDisconnected from server.")
            break  # Exit if the server closed the connection or an error occurred

def send_tcp_message(sock, message):
    sock.sendall(message.encode())

def send_udp_message(host, udp_port, message):
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as udp_sock:
        udp_sock.sendto(message.encode(), (host, udp_port))

def client(host, tcp_port, udp_port, client_id):
    protocol = "TCP"  # Default protocol
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as tcp_sock:
        tcp_sock.connect((host, tcp_port))
        tcp_sock.sendall(client_id.encode())
        threading.Thread(target=receive_messages, args=(tcp_sock,), daemon=True).start()

        print("Connected via TCP. Use '/udp' to switch to UDP, '/tcp' to switch back to TCP.")
        while True:
            if protocol == "TCP":
                message = input("TCP> ")
                if message.lower() == "/udp":
                    protocol = "UDP"
                    print("Switched to UDP. Use '/tcp' to switch back to TCP.")
                else:
                    send_tcp_message(tcp_sock, message)
            elif protocol == "UDP":
                message = input("UDP> ")
                if message.lower() == "/tcp":
                    protocol = "TCP"
                    print("Switched to TCP. Use '/udp' to switch to UDP.")
                else:
                    send_udp_message(host, udp_port, f"{client_id}: {message}")

if __name__ == "__main__":
    HOST = '127.0.0.1'
    TCP_PORT = 12345
    UDP_PORT = 12346
    client_id = input("Enter your client ID (1-4): ").strip()
    client(HOST, TCP_PORT, UDP_PORT, client_id)
