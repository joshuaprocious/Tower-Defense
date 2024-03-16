import socket
import threading
import json

class NetworkClient:
    def __init__(self, host, tcp_port, udp_port, udp_listen_port, client_id):
        self.host = host
        self.tcp_port = tcp_port
        self.udp_port = udp_port
        self.client_id = client_id
        self.udp_sock = self.init_udp_socket(udp_listen_port)
        self.tcp_sock = self.init_tcp_connection()
        self.tcp_message_callback = None
        self.udp_message_callback = None

        # Immediately after initializing, send initial messages
        #self.send_tcp_message({'client_id': self.client_id, 'message': 'client id send'})
        #self.send_udp_message({'client_id': self.client_id, 'message': 'Initialize UDP bind'})

    def init_tcp_connection(self):
        tcp_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        tcp_sock.connect((self.host, self.tcp_port))
        return tcp_sock

    def send_tcp_message(self, message):
        encoded_message = json.dumps(message).encode()
        self.tcp_sock.sendall(encoded_message)

    def listen_tcp_messages(self):
        while True:
            try:
                data = self.tcp_sock.recv(1024).decode()
                if not data:
                    break
                decoded_data = json.loads(data)
                if self.tcp_message_callback:  # Check if the callback is not None
                    self.tcp_message_callback(decoded_data)
                #print(f"\nTCP: {decoded_data['message']}\nEnter your message: ", end='', flush=True)
            except Exception as e:
                print(f"\nError receiving TCP message: {e}")
                break

    def set_tcp_message_callback(self, callback):
        self.tcp_message_callback = callback

    def init_udp_socket(self, udp_listen_port):
        udp_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        udp_sock.bind(('', udp_listen_port))  # Bind to the specific port for listening
        return udp_sock
    
    def send_udp_message(self, message):
        encoded_message = json.dumps(message).encode()
        self.udp_sock.sendto(encoded_message, (self.host, self.udp_port))
    
    def listen_udp_messages(self):
        while True:
            try:
                data, _ = self.udp_sock.recvfrom(1024)
                decoded_data = json.loads(data.decode())
                if self.udp_message_callback:  # Check if the callback is not None
                    self.udp_message_callback(decoded_data)  # Call the callback if it's set
                #print(f"\nUDP: {decoded_data['message']}\nEnter your message: ", end='', flush=True)
            except Exception as e:
                print(f"\nError receiving UDP message: {e}")
                break

    def set_udp_message_callback(self, callback):
        self.udp_message_callback = callback

    def start_listening(self):
        threading.Thread(target=self.listen_tcp_messages, daemon=True).start()
        threading.Thread(target=self.listen_udp_messages, daemon=True).start()

    
    def run_client(self):
        self.start_listening()
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
                    self.send_tcp_message({'client_id': self.client_id, 'message': message})
                else:
                    self.send_udp_message({'client_id': self.client_id, 'message': message})

'''if __name__ == "__main__":
    HOST = 'localhost'
    TCP_PORT = 12345
    UDP_PORT = 12346
    UDP_LISTEN_PORT = 12347  # Example port, adjust as necessary for your setup
    client_id = input("Enter your client ID (1-4): ").strip()
    network_client = NetworkClient(HOST, TCP_PORT, UDP_PORT, UDP_LISTEN_PORT, client_id)
    network_client.run_client()'''
