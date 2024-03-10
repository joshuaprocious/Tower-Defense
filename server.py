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
        print("Server started. Waiting for connections...")

    def broadcast(self, message):
        for client in self.clients[:]:  # Iterate over a copy to avoid modification errors
            client.send(message)

    def handle_client(self, client, addr):
        print(f"New client connected: {addr}")
        self.clients.append(client)
        while True:
            try:
                data = client.recv(4096)
                if not data:
                    break
                message = pickle.loads(data)
                self.process_message(message, client)
            except Exception as e:
                print(f"Error with client {addr}: {e}")
                break
        client.close()
        self.clients.remove(client)
        print(f"Client {addr} disconnected")

    def process_message(self, message, client):
        message_type = message['type']
        message_data = message['data']
        print('process_message function data message_type: ' + str(message_type) + ' message_data: ' + str(message_data))
        if message_type == 'request_player_number':
            if message_data in self.available_players:
                self.available_players.remove(message_data)
                message = {'type': 'player_number_confirmed', 'data': message_data}
                print('message data from server: ' + str(message))
                client.send(pickle.dumps(message))

                # Broadcast updated game state to all clients
                message = {'type': 'game_state_update', 'data': self.player_positions}
                self.broadcast(pickle.dumps(message))
            else:
                error_message = {'type': 'error', 'data': 'Unavailable'}
                client.send(pickle.dumps(error_message))

        elif message_type == 'player_number_confirmed':
            print('confirmed player: '+ str(message_data))
            pass
        elif message_type == 'update_position':
            # Extract player_id and the new_position dictionary from the message data
            player_id = message_data['player_id']
            new_position_dict = message_data['position']
            
            # Extract 'x' and 'y' from the new_position dictionary
            x = new_position_dict['x']
            y = new_position_dict['y']
            
            # Update the specific player's position in the list with a tuple of (x, y)
            self.player_positions[player_id - 1] = (x, y)
            
            # Prepare a message with the updated game state to broadcast
            message = {'type': 'game_state_update', 'data': self.player_positions}
            
            # Broadcast the updated game state to all clients
            self.broadcast(pickle.dumps(message))

        else:
            print('Not a valid message type')
            pass    

    def start(self):
        while True:
            client, addr = self.server_socket.accept()
            threading.Thread(target=self.handle_client, args=(client, addr)).start()

if __name__ == "__main__":
    server = Server()
    server.start()
