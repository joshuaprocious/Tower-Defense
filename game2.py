# game.py
from client import NetworkClient
import time

class Game:
    def __init__(self, host, tcp_port, udp_port, udp_listen_port, client_id):
        self.running = True
        self.client_id = client_id
        self.network_client = NetworkClient(host, tcp_port, udp_port, udp_listen_port, client_id)
        self.network_client.set_tcp_message_callback(self.handle_tcp_message)
        self.network_client.set_udp_message_callback(self.handle_udp_message)
        self.network_client.start_listening()

    def handle_tcp_message(self, message):
        print("Received TCP message:", message)

    def handle_udp_message(self, message):
        print("Received UDP message:", message)

    def run(self):
        print("Game loop starting. Listening for network messages...")
        protocol = "TCP"  # Default protocol
        #initialize connection messages
        self.network_client.send_tcp_message({'client_id': self.client_id, 'message': 'client id send'})
        self.network_client.send_udp_message({'client_id': self.client_id, 'message': 'Initialize UDP bind'})
        while self.running:
            # In a more complex game, update game state and render here
            # For this example, we'll just sleep to simulate the game loop
            #time.sleep(1)  # Sleep to prevent this loop from consuming too much CPU

            # Implement a condition to break the loop and end the game if necessary
            # e.g., self.running = False when a certain message is received or command entered
            message = input("> ")
            if message.lower() == "/udp":
                protocol = "UDP"
                print("Switched to UDP. Use '/tcp' to switch back to TCP.")
            elif message.lower() == "/tcp":
                protocol = "TCP"
                print("Switched to TCP. Use '/udp' to switch to UDP.")
            else:
                if protocol == "TCP":
                    self.network_client.send_tcp_message({'client_id': self.client_id, 'message': message})
                else:
                    self.network_client.send_udp_message({'client_id': self.client_id, 'message': message})
        print("Game loop ended. Cleaning up...")

if __name__ == "__main__":
    HOST = 'localhost'
    TCP_PORT = 12345
    UDP_PORT = 12346
    UDP_LISTEN_PORT = 12348
    client_id = input("Enter your client ID (1-4): ").strip()
    game = Game(HOST, TCP_PORT, UDP_PORT, UDP_LISTEN_PORT, client_id)
    game.run()
