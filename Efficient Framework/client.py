import socket
import threading
import json

def receive_messages(sock):
    while True:
        try:
            data = sock.recv(1024).decode()  # Decode bytes to string
            if not data:
                break
            decoded_data = json.loads(data)  # Parse JSON string to Python dictionary
            message = decoded_data['message']  # Access the message key
            print(f"\n{message}\nEnter your message: ", end='', flush=True)
        except Exception as e:
            print(f"An error occurred: {e}")
            break  # Exit if the server closed the connection or an error occurred

def send_tcp_message(sock, message):
    # send regular encoded data
    '''sock.sendall(message.encode())'''
    # send json encoded
    encoded_message = json.dumps({'client_id': client_id, 'message': message}).encode()
    sock.sendall(encoded_message)

def send_udp_message(host, udp_port, message):
    # send regular encoded data    
    '''with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as udp_sock:
        udp_sock.sendto(message.encode(), (host, udp_port))'''
    # send json encoded
    encoded_message = json.dumps({'client_id': client_id, 'message': message}).encode()
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as udp_sock:
        udp_sock.sendto(encoded_message, (host, udp_port))

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
