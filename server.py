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

    def update_player_position(self, player_id, position):
        with self.lock:
            player_number = self.player_numbers.get(player_id)
            if player_number and player_number in self.player_positions:
                self.player_positions[player_number] = position
                # Directly update broadcast_content here for simplicity
                self.broadcast_content['player_position'] = self.player_positions.copy()

class GameState:
    def __init__(self, server):
        self.clients = {}
        self.game_entities = GameEntities()
        self.server = server
        self.player_positions = self.game_entities.player_positions
        self.lock = threading.Lock()  # Initialize a lock

    def broadcast(self, message):
        for client_address in self.clients.values():
            try:
                self.server.sock.sendto(pickle.dumps(message), client_address)
            except Exception as e:
                print(f"Broadcast error: {e}")

    def update_and_broadcast(self):
        with self.lock:
            # Prepare the game state update message
            message = {'type': 'game_state_update', 'data': self.game_entities.broadcast_content, 'timestamp': time.time()}
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
            message = {'type': 'game_state_update', 'data': self.game_entities.broadcast_content, 'timestamp': time.time()}
            self.broadcast(message)
            print('game state update message: ' + str(message))

        

class Server:
    def __init__(self, host='0.0.0.0', port=12345):
        self.server_address = (host, port)
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind(self.server_address)
        self.game_state = GameState(self)
        print("Server started. Waiting for connections...")
    
    
    def listen(self):
        while True:
            data, client_address = self.sock.recvfrom(4096)
            if data:
                threading.Thread(target=self.handle_client, args=(data, client_address)).start()
    
    def handle_client(self, client, client_address):
        
        while True:
            try:
                #print('true is activated in handle_client')
                data, client_address = self.sock.recvfrom(4096)
                if not data:
                    break
                message = pickle.loads(data)
                player_id = None  # Define player_id outside of the conditional scopes
                message_data = message['data']
                message_type = message['type']
                print('received message from client: ' +str(client_address) + str(message))
                if message_type == 'request_player_join' and client_address not in self.game_state.clients.values():
                    print(f"New client connected: {client_address}")
                    print('game state on player join: ' + str(self.game_state))
                    player_id = uuid.uuid4().hex
                    self.game_state.clients[player_id] = client_address
                    player_number = self.game_state.game_entities.add_player(player_id)
                    confirmation_message = {
                        'type': 'player_number_confirmed',
                        'data': {'player_id': player_id, 'player_number': player_number, 'clients': self.game_state.clients},
                        'timestamp': time.time()
                    }
                    self.sock.sendto(pickle.dumps(confirmation_message), client_address)
                    print('clients: ' + str(self.game_state.clients))
                elif message_type == 'initialize_gameloop':
                    client_ack_message = {
                        'type': 'initialize_accepted',
                        'data': 'alright play on',
                        'timestamp': time.time()
                    }
                    self.sock.sendto(pickle.dumps(client_ack_message), client_address)
                    print('initilization done for client')
                    threading.Thread(target=self.game_state.update_loop).start() # starts the 60 FPS game state update loop
                    # Now listen for other messages from this client in a loop...
                elif message['type'] == 'update_player_position':
                    player_id = message['data']['player_id']  # Assuming the player_id is sent in the message
                    position = message['data']['position']
                    self.game_state.game_entities.update_player_position(player_id, position)
                    self.game_state.update_and_broadcast()
            except Exception as e:
                print(f"Error with client {client_address}: {e}")
                break

        #this code below sends responses for the UDP implementation
        #response_data = b"Your response here"
        #self.sock.sendto(response_data, client_address)
        #del self.game_state.clients[player_id]
        print(f"Client {client_address} disconnected")

    def start(self):
        #threading.Thread(target=self.game_state.update_loop).start() # starts the 60 FPS game state update loop
        server.listen()

if __name__ == "__main__":
    server = Server()
    server.start()
