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
        self.player_positions = [(50, 50), (450, 50), (50, 450), (450, 450)]
        self.available_players = [1, 2, 3, 4]

    def broadcast(self, message):
        for client in self.clients[:]:  # Iterate over a copy to avoid modification errors
            try:
                client.send(message)
            except Exception as e:  # Catch any exception to avoid server crash
                print(f"Broadcast error: {e}")
                client.close()
                self.clients.remove(client)

    def handle_client(self, client):
        try:
            while True:
                data = client.recv(1024)
                if not data:
                    break
                message_type, message_content = pickle.loads(data)
                
                # Process player number requests and position updates
                if message_type == 'request_player_number':
                    if message_content in self.available_players:
                        self.available_players.remove(message_content)
                        client.send(pickle.dumps(('player_number_confirmed', message_content)))
                        # Broadcast updated game state to all clients
                        self.broadcast(pickle.dumps(self.player_positions))
                    else:
                        client.send(pickle.dumps(('player_number_error', 'Unavailable')))
                elif message_type == 'update_position':
                    # Update the specific player's position
                    player_id, new_position = message_content
                    self.player_positions[player_id - 1] = new_position
                    # Broadcast the updated game state
                    self.broadcast(pickle.dumps(self.player_positions))

                # Broadcast the updated game state after processing
                self.broadcast(pickle.dumps(self.player_positions))
        except Exception as e:
            print(f"Client error: {e}")
        finally:
            client.close()
            if client in self.clients:  # Safely remove the client
                self.clients.remove(client)

    def start(self):
        print("Server started. Waiting for connections...")
        while True:
            client, _ = self.server_socket.accept()
            self.clients.append(client)
            threading.Thread(target=self.handle_client, args=(client,)).start()

if __name__ == "__main__":
    server = Server()
    server.start()
