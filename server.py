import socket
import threading
import pickle
import uuid
import time

class GameEntities:
    def __init__(self):
        self.player_positions = {}  # Now using player number as key
        self.player_numbers = {}  # UUID as key and player number as value
        self.available_numbers = [1, 2, 3, 4]
        self.broadcast_content = {} #used as a reusable variable for game state content updates
        self.lock = threading.Lock()  # Initialize a lock

    def add_player(self, player_id):
        with self.lock:
            if self.available_numbers:
                player_number = self.available_numbers.pop(0)  # Assign the next available number
                self.player_numbers[player_id] = player_number
                # Define spawn positions for up to four players
                spawn_positions = {
                    1: {'x': 50, 'y': 50},   # Top-left corner
                    2: {'x': 450, 'y': 50},  # Top-right corner
                    3: {'x': 50, 'y': 450},  # Bottom-left corner
                    4: {'x': 450, 'y': 450}  # Bottom-right corner
                }
                
                # Use the player_number to get the corresponding spawn position
                spawn_position = spawn_positions.get(player_number, {'x': 250, 'y': 250})  # Default position if more than 4 players
                
                self.player_positions[player_number] = spawn_position
                self.broadcast_content['player_position'] = self.player_positions
                return player_number

            return None

    def update_player_position(self, player_number, position):
        with self.lock:
            if player_number in self.player_positions:
                self.player_positions[player_number] = position
                self.broadcast_content = {'player_position': self.player_positions}

class GameState:
    def __init__(self, server):
        self.clients = {}
        self.game_entities = GameEntities()
        self.server = server
        self.player_positions = self.game_entities.player_positions
        self.lock = threading.Lock()  # Initialize a lock

    def broadcast(self, message):
        for client in self.clients.values():
            try:
                client.send(pickle.dumps(message))
            except Exception as e:
                print(f"Broadcast error: {e}")

    def update_and_broadcast(self):
        with self.lock:
            # Prepare the game state update message
            message = {'type': 'game_state_update', 'data': self.game_entities.broadcast_content}
            print('broadcasting game_state_update: ' + str(message))
            self.broadcast(message)
            #self.game_entities.broadcast_content = None

    def update_loop(self):
        while True:
            self.update_game_state()
            time.sleep(1 / 60)  # Run the loop at approximately 60 frames per second

    def update_game_state(self):
        # Update game state, e.g., move bullets
        self.broadcast_game_state()
        #self.update_and_broadcast()

    def broadcast_game_state(self):
        with self.lock:
            # Broadcast updated game state to all clients
            message = {'type': 'game_state_update', 'data': self.game_entities.broadcast_content}
            self.broadcast(message)
            print('game state update message: ' + str(message))

        

class Server:
    def __init__(self, host='127.0.0.1', port=12345):
        self.addr = (host, port)
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind(self.addr)
        self.server_socket.listen()
        self.game_state = GameState(self)
        print("Server started. Waiting for connections...")

    def handle_client(self, client, addr):
        print(f"New client connected: {addr}")
        player_id = uuid.uuid4().hex
        self.game_state.clients[player_id] = client

        # Immediately confirm the player number back to the client
        player_number = self.game_state.game_entities.add_player(player_id)
        confirmation_message = {
            'type': 'player_number_confirmed',
            'data': {'player_id': player_id, 'player_number': player_number}
        }
        client.send(pickle.dumps(confirmation_message))
        self.game_state.update_and_broadcast()  # Make sure this sends the initial game state

        while True:
            try:
                data = client.recv(4096)
                if not data:
                    break
                message = pickle.loads(data)
                print('received message from client: ' + str(message))
                if message['type'] == 'update_player_position':
                    player_number = self.game_state.game_entities.player_numbers.get(player_id)
                    if player_number is not None:
                        self.game_state.game_entities.update_player_position(player_number, message['data']['position'])
                        self.game_state.update_and_broadcast()
            except Exception as e:
                print(f"Error with client {addr}: {e}")
                break

        client.close()
        del self.game_state.clients[player_id]
        print(f"Client {addr} disconnected")

    def start(self):
        threading.Thread(target=self.game_state.update_loop).start() # starts the 60 FPS game state update loop
        while True:
            client, addr = self.server_socket.accept()
            threading.Thread(target=self.handle_client, args=(client, addr)).start()

if __name__ == "__main__":
    server = Server()
    server.start()
