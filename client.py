import pygame
import socket
import pickle
import sys
import threading
import time

'''def get_local_ip():
    try:
        # Attempt to connect to an external address (does not need to be reachable)
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        local_ip = s.getsockname()[0]  # Get the IP address of the socket's local endpoint
        s.close()
        return local_ip
    except Exception as e:
        print(f"Error obtaining local IP: {e}")
        return None

# Example usage
local_ip = get_local_ip()
if local_ip:
    print(f"Local IP Address: {local_ip}")
else:
    print("Could not obtain local IP address.")

get_local_ip()'''

class Player(pygame.sprite.Sprite):
    def __init__(self, color, initial_position):
        super().__init__()
        self.image = pygame.Surface((10, 10))
        self.image.fill(color)
        self.rect = self.image.get_rect(topleft=initial_position)
        # For interpolation
        self.previous_position = initial_position
        self.current_position = initial_position
        self.previous_time = time.time()
        self.current_time = time.time()

    def update(self, new_position):
        # Update positions for interpolation
        self.previous_position = self.current_position
        self.current_position = new_position
        self.previous_time = self.current_time
        self.current_time = time.time()

    def interpolate(self, alpha):
        # Linear interpolation between previous and current position - smoother client rendering
        new_x = self.previous_position[0] + (self.current_position[0] - self.previous_position[0]) * alpha
        new_y = self.previous_position[1] + (self.current_position[1] - self.previous_position[1]) * alpha
        self.rect.topleft = (new_x, new_y)

class Client:
    def __init__(self, server_address='127.0.0.1', port=12345):
        self.server_address = (server_address, port)
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.client_socket.bind(('0.0.0.0', 0))
        self.player_id = None  # This will now store the unique player ID sent by the server
        self.game_state_content = []  
        self.is_shooting = False
        self.colors = [(0, 255, 0), (0, 0, 255), (255, 0, 0), (255, 255, 0)]
        threading.Thread(target=self.receive_data, daemon=True).start()
        self.lock = threading.Lock()  # Initialize a lock
        self.players = pygame.sprite.Group()  # This will hold all player sprites
        self.player_sprites = {}  # Maps player numbers to their sprite objects
        self.state = 'requesting_to_join'  # Track the client's state
        self.initialize_connection()
        print('client init complete')

   
    def initialize_connection(self):
        # Send the first message and wait for an acknowledgment
        while self.state == 'requesting_to_join':
            self.send_message('request_player_join', {'data': 'requesting access to join game'})
            time.sleep(0.2)
        
        # Wait for the state to change from "initializing"
        while self.state == "initializing":
            self.send_message('initialize_gameloop', 'start me up')
            time.sleep(0.2)
    
    def send_message(self, message_type, data):
        with self.lock:
            message = {'type': message_type, 'data': data, 'timestamp': time.time()}
            try:
                self.client_socket.sendto(pickle.dumps(message), self.server_address)
            except socket.error as e:
                print(f"Error sending message: {e}")
                self.client_socket.close()
                sys.exit()


    def receive_data(self):
        while True:
            try:
                data, _ = self.client_socket.recvfrom(4096)
                print('receiving data from server: ' + str(data))
                if not data:
                    break
                try:
                    message = pickle.loads(data)
                except: 
                    print('data is bad. skipping.')
                print('received message from server: ' + str(message))
                if isinstance(message, dict):
                    self.process_message(message)
            except Exception as e:
                print(f"Error receiving data: {e}")
                break
        self.client_socket.close()

    def process_message(self, message):
        self.state
        with self.lock:
            message_type = message['type']
            message_data = message['data']
            if message_type == 'player_number_confirmed':
                self.player_id = message_data['player_id']  # UUID
                self.player_number = message_data['player_number']  # Player number
                self.state = 'initializing'
                print(f"Player ID {self.player_id} and Number {self.player_number} confirmed by server.")
            elif message_type == 'initialize_accepted':
                print('initialize accepted received')
                self.state = 'game loop'
            elif message_type == 'game_state_update' and self.state == 'game loop':
                self.game_state_content = message_data # message_data is the variable which contains type and related data (ie. {'player_position': {1: {'x': 250, 'y': 250}}})
                self.update_player_sprites()  # Update player sprites based on game state
                print('Game state content:', self.game_state_content)
            else:
                print("Unexpected message type received:", message_type)

    def update_player_sprites(self):
        for player_number, pos in self.game_state_content['player_position'].items():
            if player_number not in self.player_sprites:
                # Create a new player sprite if it doesn't exist
                color = self.colors[(player_number - 1) % len(self.colors)]
                player_sprite = Player(color, (pos['x'], pos['y']))
                self.players.add(player_sprite)
                self.player_sprites[player_number] = player_sprite
            else:
                # Update existing sprite position
                self.player_sprites[player_number].update((pos['x'], pos['y']))

    def game_loop(self):
        self.state = self.state
        pygame.init()
        screen = pygame.display.set_mode((1080, 920))
        clock = pygame.time.Clock()
        
        print('initial game loop messages sent')

        input_sample_rate = 1 / 60  # Target input handling rate: 60 times per second
        next_input_time = time.time() + input_sample_rate


        while True and self.state == 'game loop':
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

            screen.fill((0, 0, 0))  # Ensure this is at the start of the loop to clear the screen each frame
            current_time = time.time()
            if current_time >= next_input_time:
                if self.game_state_content and self.player_id is not None:
                    for player_sprite in self.player_sprites.values():
                        time_since_update = current_time - player_sprite.current_time
                        # Assuming updates come roughly every 1/60 seconds; adjust as necessary
                        alpha = min(time_since_update * 60, 1)
                        player_sprite.interpolate(alpha)
                    #print('message data: ' + str(self.game_state_content) + ' player id: '+ str(self.player_id) + ' player number: ' + str(self.player_number))
                    keys = pygame.key.get_pressed()
                    # Initialize x and y with current player's position to maintain it if no key is pressed
                    current_player_pos = self.game_state_content['player_position'][self.player_number]
                    x, y = current_player_pos['x'], current_player_pos['y']

                    position_changed = False

                    # Define the base speed
                    base_speed = 3

                    # Check if the Shift key is pressed (either left or right)
                    shift_pressed = keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT]

                    # Calculate the movement speed based on whether Shift is pressed
                    movement_speed = base_speed + 5 if shift_pressed else base_speed

                    # Apply the movement speed to the movement logic
                    if keys[pygame.K_LEFT]:
                        x -= movement_speed
                        position_changed = True
                    if keys[pygame.K_RIGHT]:
                        x += movement_speed
                        position_changed = True
                    if keys[pygame.K_UP]:
                        y -= movement_speed
                        position_changed = True
                    if keys[pygame.K_DOWN]:
                        y += movement_speed
                        position_changed = True
                    next_input_time += input_sample_rate


                    if position_changed:
                        position_dict = {'x': x, 'y': y}  # Update with new position
                        self.send_message('update_player_position', {'player_id': self.player_id, 'position': position_dict})
                        # Update the local game state for immediate feedback
                        self.game_state_content['player_position'][self.player_number] = position_dict

                # Draw all players
                self.players.draw(screen)  # Draw all player sprites in the group
                #the commented code was before addition of sprite groups for player
                '''for player_number, pos in self.game_state_content['player_position'].items():
                    color = self.colors[(player_number - 1) % len(self.colors)]  # Adjust color based on player number
                    pygame.draw.rect(screen, color, (pos['x'], pos['y'], 10, 10))'''
                if next_input_time < time.time() - input_sample_rate:
                    next_input_time = time.time() + input_sample_rate    
            pygame.display.flip()
            clock.tick(60)

if __name__ == "__main__":
    client = Client()
    client.game_loop()
