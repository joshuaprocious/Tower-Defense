import socket
import threading
import pickle

class Server:
    def __init__(self, host='127.0.0.1', port=12345):
        self.clients = []
        self.addr = (host, port)
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind(self.addr)
        self.server_socket.listen()
        self.player_positions = [(50, 50), (450, 50), (50, 450), (450, 450)]  # Default positions for up to 4 players

    def broadcast(self, message):
        for client in self.clients:
            client.send(message)

    def handle_client(self, client, player_id):
        # Send initial player positions along with the client's player ID
        initial_data = [player_id] + [self.player_positions]  # Corrected to send as a list
        client.send(pickle.dumps(initial_data))
        
        while True:
            try:
                data = client.recv(1024)
                if not data:
                    break
                _, position_update = pickle.loads(data)  # Receive position update
                self.player_positions[player_id] = position_update  # Update specific player's position
                
                # Broadcast updated positions to all clients
                self.broadcast(pickle.dumps(self.player_positions))
            except:
                self.clients.remove(client)
                client.close()
                print(f"Player {player_id} disconnected.")
                break


    def start(self):
        print("Server started. Waiting for connections...")
        player_id = 0
        while True:
            client, _ = self.server_socket.accept()
            print(f"Player {player_id} connected.")
            self.clients.append(client)
            
            threading.Thread(target=self.handle_client, args=(client, player_id)).start()
            player_id += 1  # Increment player_id for the next connection

if __name__ == "__main__":
    server = Server()
    server.start()
