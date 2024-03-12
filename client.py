import pygame
import socket
import pickle
import sys
import threading
import time

class Client:
    def __init__(self, address='127.0.0.1', port=12345):
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client_socket.connect((address, port))
        self.player_id = None  # This will now store the unique player ID sent by the server
        self.game_state_content = []  
        self.is_shooting = False
        self.colors = [(0, 255, 0), (0, 0, 255), (255, 0, 0), (255, 255, 0)]
        threading.Thread(target=self.receive_data, daemon=True).start()
        self.lock = threading.Lock()  # Initialize a lock

    def send_message(self, message_type, data):
        with self.lock:
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
        with self.lock:
            message_type = message['type']
            message_data = message['data']
            if message_type == 'player_number_confirmed':
                self.player_id = message_data['player_id']  # UUID
                self.player_number = message_data['player_number']  # Player number
                print(f"Player ID {self.player_id} and Number {self.player_number} confirmed by server.")
            elif message_type == 'game_state_update':
                self.game_state_content = message_data # message_data is the variable which contains type and related data (ie. {'player_position': {1: {'x': 250, 'y': 250}}})
                print('Game state message:', self.game_state_content)
            else:
                print("Unexpected message type received:", message_type)

    def game_loop(self):
        pygame.init()
        screen = pygame.display.set_mode((1080, 920))
        clock = pygame.time.Clock()

        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

            screen.fill((0, 0, 0))  # Ensure this is at the start of the loop to clear the screen each frame
            
            if self.game_state_content and self.player_id is not None:
                
                #print('message data: ' + str(self.game_state_content) + ' player id: '+ str(self.player_id) + ' player number: ' + str(self.player_number))
                keys = pygame.key.get_pressed()
                # Initialize x and y with current player's position to maintain it if no key is pressed
                current_player_pos = self.game_state_content['player_position'][self.player_number]
                x, y = current_player_pos['x'], current_player_pos['y']

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
                    position_dict = {'x': x, 'y': y}  # Update with new position
                    self.send_message('update_player_position', {'player_id': self.player_id, 'position': position_dict})
                    # Update the local game state for immediate feedback
                    self.game_state_content['player_position'][self.player_number] = position_dict

                # Draw all players
                for player_number, pos in self.game_state_content['player_position'].items():
                    color = self.colors[(player_number - 1) % len(self.colors)]  # Adjust color based on player number
                    pygame.draw.rect(screen, color, (pos['x'], pos['y'], 50, 50))
                    
            pygame.display.flip()
            clock.tick(60)

if __name__ == "__main__":
    client = Client()
    client.game_loop()
