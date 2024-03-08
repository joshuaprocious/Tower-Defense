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
        self.colors = [(0, 255, 0), (0, 0, 255), (255, 0, 0), (255, 255, 0)]
        threading.Thread(target=self.receive_data, daemon=True).start()
        self.request_player_number()

    def request_player_number(self):
        player_number = input("What player are you? (1, 2, 3, or 4): ")
        self.send_data(('request_player_number', int(player_number)))

    def send_data(self, data):
        try:
            self.client_socket.send(pickle.dumps(data))
        except socket.error as e:
            print(f"Error sending data: {e}")
            self.client_socket.close()
            sys.exit()

    def receive_data(self):
        while True:
            try:
                data = self.client_socket.recv(1024)
                if not data:
                    break
                received_data = pickle.loads(data)
                if isinstance(received_data, tuple):
                    message_type, message_content = received_data
                    if message_type == 'player_number_confirmed':
                        # Ensure player_id is treated as an integer
                        self.player_id = int(message_content)
                        print(f"Player number {self.player_id} confirmed by server.")
                    # Further handling based on message_type...
                elif isinstance(received_data, list):
                    self.game_state = received_data
                else:
                    print("Unexpected data format received:", received_data)
                
            except Exception as e:
                print(f"Error receiving data: {e}")
                break
        self.client_socket.close()

    def game_loop(self):
        pygame.init()
        screen = pygame.display.set_mode((500, 500))
        clock = pygame.time.Clock()
        
    
        while True:
            # Process only the quit event to close the game properly
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

            if self.game_state is not None and self.player_id is not None:
                keys = pygame.key.get_pressed()
                x, y = self.game_state[self.player_id - 1]

                # Initialize a variable to track if there's any change in position
                position_changed = False

                # Update the player's position based on key presses
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

                # Send the updated position to the server only if there was a change
                if position_changed:
                    try:
                        self.send_data(('update_position', (self.player_id, (x, y))))
                    except Exception as e:
                        print(f"Error sending update: {e}")

                screen.fill((0, 0, 0))
                # Draw all players based on the current game state
                for idx, pos in enumerate(self.game_state):
                    color = self.colors[idx % len(self.colors)]
                    pygame.draw.rect(screen, color, (*pos, 50, 50))

                pygame.display.flip()
                clock.tick(60)
            
if __name__ == "__main__":
    Client().game_loop()
