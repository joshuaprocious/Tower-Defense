import socket

def tcp_client(host, port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((host, port))
        client_id = input("Enter your client ID (1-4): ")
        s.sendall(client_id.encode())  # Send client ID immediately after connecting
        welcome_message = s.recv(1024).decode()
        print(welcome_message)
        if "already in use" in welcome_message:
            return
        while True:
            message = input("Enter your message: ")
            if message.lower() == 'exit':
                break
            s.sendall(message.encode())
            # Receive and display broadcast messages from the server
            data = s.recv(1024)
            print(data.decode())

def udp_client(host, port):
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
        client_id = input("Enter your client ID (1-4): ").strip()
        while True:
            message = input("Enter your message ('exit' to quit): ").strip()
            if message.lower() == 'exit':
                break
            full_message = f"{client_id}: {message}"
            s.sendto(full_message.encode(), (host, port))
            # Optionally, wait for a response if the server echoes messages back
            data, _ = s.recvfrom(1024)
            print(f"Server says: {data.decode()}")

if __name__ == "__main__":
    host = '127.0.0.1'
    tcp_port = 12345
    udp_port = 12346

    protocol = input("Choose your protocol (TCP/UDP): ").upper()
    if protocol == "TCP":
        tcp_client(host, tcp_port)
    elif protocol == "UDP":
        udp_client(host, udp_port)
    else:
        print("Unknown protocol. Please enter TCP or UDP.")
