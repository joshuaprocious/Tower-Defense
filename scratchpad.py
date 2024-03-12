import socket
import threading
import pickle
import uuid
import time

class Server:
    def __init__(self, host='127.0.0.1', port=12345):
        self.clients = []
        self.addr = (host, port)
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind(self.addr)
        self.server_socket.listen()
        self.player_positions = [(50, 50), (450, 50), (50, 450), (450, 450)]
        self.available_players = [1, 2, 3, 4]
        self.bullets = []  # Store bullets as a list of dictionaries
        print("Server started. Waiting for connections...")

    def generate_unique_id(self):
        return uuid.uuid4().hex  # Generates a random unique ID
    
    def broadcast(self, message):
        for client in self.clients[:]:  # Iterate over a copy to avoid modification errors
            try:
                client.send(pickle.dumps(message))  # Corrected to send pickled message
            except Exception as e:
                print(f"Broadcast error: {e}")
                self.clients.remove(client)
                client.close()

    def spawn_bullet(self, data):
        player_id = data['player_id']
        position = data['position']
        direction = data['direction']  # Now includes direction

        bullet_id = self.generate_unique_id()
        bullet_speed = 5  # You can adjust this speed
        velocity = (direction[0] * bullet_speed, direction[1] * bullet_speed)

        bullet = {'id': bullet_id, 'player_id': player_id, 'position': position, 'velocity': velocity}
        self.bullets.append(bullet)
        print(f"Bullet spawned: {bullet_id}")
        print('full bullet dictionary: ' + str(bullet))
        self.update_game_state()

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
                self.broadcast(message)
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
            self.broadcast(message)
        elif message['type'] == 'shoot_bullet':
            print('sending message to spawn_bullet')
            self.spawn_bullet(message_data)

        else:
            print('Not a valid message type: ' + str(message_type))
            pass    

    def start(self):
        # Start the update loop in its own thread
        #threading.Thread(target=self.update_loop).start()
        while True:
            client, addr = self.server_socket.accept()
            threading.Thread(target=self.handle_client, args=(client, addr)).start()

    def update_loop(self):
        while True:
            self.update_game_state()
            time.sleep(1 / 60)  # Run the loop at approximately 60 frames per second

    def update_game_state(self):
        # Update game state, e.g., move bullets
        self.move_bullets()
        self.broadcast_game_state()

    def move_bullets(self):
        # Move each bullet according to its velocity
        for bullet in self.bullets:
            bullet['position'] = (
                bullet['position'][0] + bullet['velocity'][0], 
                bullet['position'][1] + bullet['velocity'][1]
            )

    def broadcast_game_state(self):
        # Broadcast updated game state to all clients
        message = {'type': 'game_state_update', 'data': {'players': self.player_positions, 'bullets': self.bullets}}
        print('game state update message: ' + str(message))
        self.broadcast(pickle.dumps(message))

if __name__ == "__main__":
    server = Server()
    server.start()




import pygame
import socket
import pickle
import sys
import threading

class Client:
    def __init__(self, address='127.0.0.1', port=12345):
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client_socket.connect((address, port))
        self.player_id = None
        self.game_state = None
        self.is_shooting = False
        self.colors = [(0, 255, 0), (0, 0, 255), (255, 0, 0), (255, 255, 0)]
        threading.Thread(target=self.receive_data, daemon=True).start()
        self.request_player_number_first = True
        if self.request_player_number_first == True:
            self.request_player_number()

    def request_player_number(self):
        # This initiates the player number request process.
        player_number = input("What player are you? (1, 2, 3, or 4): ")
        self.send_message('request_player_number', int(player_number))
        self.request_player_number_first = False

    def send_message(self, message_type, data):
        # This generalizes sending messages to use a structured format.
        message = {'type': message_type, 'data': data}
        try:
            self.client_socket.send(pickle.dumps(message))
        except socket.error as e:
            print(f"Error sending message: {e}")
            self.client_socket.close()
            sys.exit()

    def receive_data(self):
        while True:
            try:
                data = self.client_socket.recv(4096)
                if not data:
                    break
                message = pickle.loads(data)
                print('message after unpickling in receive_data function: '+ str(message))
                # Ensure message is a dictionary before proceeding
                if isinstance(message, dict):
                    self.process_message(message)
                else:
                    print("Received data is not in the expected format:", message)
            except Exception as e:
                print(f"Error receiving data: {e}")
                break
        self.client_socket.close()

    def process_message(self, message):
        message_type = message['type']
        message_data = message['data']
        # Process incoming messages based on their type.
        if message_type == 'player_number_confirmed':
            self.player_id = message_data
            print(f"Player number {self.player_id} confirmed by server.")
        elif message_type == 'game_state_update':
            self.game_state = message_data
            print('game state as processed: ' + str(self.game_state))
        else:
            print("Unexpected message type received:", message_type)

    def shoot_bullet(self):
        # Assume player's position is at the center of the screen for this example
        player_pos = (250, 250)  # Replace with dynamic player position if needed
        mouse_pos = pygame.mouse.get_pos()

        # Calculate direction vector
        direction = (mouse_pos[0] - player_pos[0], mouse_pos[1] - player_pos[1])
        normalized_direction = self.normalize_vector(direction)

        # Send shoot message with direction
        self.send_message('shoot_bullet', {'player_id': self.player_id, 'position': player_pos, 'direction': normalized_direction})

    def normalize_vector(self, vector):
        # Normalize the vector to unit length
        x, y = vector
        magnitude = (x**2 + y**2)**0.5
        if magnitude == 0:
            return (0, 0)
        return (x / magnitude, y / magnitude)
        
    def game_loop(self):
        pygame.init()
        screen = pygame.display.set_mode((500, 500))
        clock = pygame.time.Clock()

        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

            if self.game_state is not None and self.player_id is not None:
                keys = pygame.key.get_pressed()
                x, y = self.game_state[self.player_id - 1]

                position_changed = False

                if keys[pygame.K_LEFT]:
                    x -= 5
                    position_changed = True
                if keys[pygame.K_RIGHT]:
                    x += 5
                    position_changed = True
                if keys[pygame.K_UP]:
                    y -= 5
                    position_changed = True
                if keys[pygame.K_DOWN]:
                    y += 5
                    position_changed = True

                if position_changed:
                    position_dict = {'x': x, 'y': y}  # Construct a dictionary with x and y as keys
                    self.send_message('update_position', {'player_id': self.player_id, 'position': position_dict})

                # Handle Shooting input
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:  # Left mouse button
                        self.is_shooting = True
                elif event.type == pygame.MOUSEBUTTONUP:
                    if event.button == 1:  # Left mouse button
                        self.is_shooting = False
                
                if self.is_shooting:
                    self.shoot_bullet()

                screen.fill((0, 0, 0))
                for idx, pos in enumerate(self.game_state):
                    color = self.colors[idx % len(self.colors)]
                    pygame.draw.rect(screen, color, (*pos, 50, 50))
                
                
                '''
                bullets = self.game_state.get('bullets', [])
                for bullet in bullets:
                    bullet_pos = bullet['position']
                    pygame.draw.rect(screen, (128, 128, 128), (*bullet_pos, 3, 3))
                '''
                pygame.display.flip()
                clock.tick(60)

if __name__ == "__main__":
    Client().game_loop()
