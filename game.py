# game.py
from client import NetworkClient
import time
import pygame


class Game:
    def __init__(self, host, tcp_port, udp_port, udp_listen_port, client_id):
        pygame.init()  # Ensure this is called
        self.running = True
        self.client_id = client_id
        self.network_client = NetworkClient(host, tcp_port, udp_port, udp_listen_port, client_id)
        self.network_client.set_tcp_message_callback(self.handle_tcp_message)
        self.network_client.set_udp_message_callback(self.handle_udp_message)
        self.network_client.start_listening()

        # Game setup
        self.running = True
        self.players = {}  # Local player state including other players
        self.player_color = {"1": (255, 0, 0), "2": (0, 0, 255), "3": (255, 255, 0), "4": (0, 255, 0)}  # Example player colors
        self.player_size = (10, 10)
        self.player_speed = 5
        
        self.screen = pygame.display.set_mode((900, 900))
        pygame.display.set_caption("Multiplayer Game")

        # Initial position
        self.player_pos = [450, 450]  # Start in the middle of the screen

    def handle_tcp_message(self, message):
        print("Received TCP message:", message)
        try:
             # Dive into the nested structure directly to the 'message' containing player positions
            if message.get('message', {}).get('type') == 'player_positions':
                player_positions_dict = message.get('message', {}).get('message', {})
                transformed_positions = {}
                for client_id, pos_dict in player_positions_dict.items():
                    # Extract 'x' and 'y' directly
                    x, y = pos_dict['x'], pos_dict['y']
                    transformed_positions[client_id] = (x, y)
                self.players = transformed_positions
                print(f"Updated player positions: {self.players}")
        except:
            print('could not process tcp message')
            pass
    
    def handle_udp_message(self, message):
        print("Received UDP message:", message)
        try:
             # Dive into the nested structure directly to the 'message' containing player positions
            if message.get('message', {}).get('type') == 'player_positions':
                player_positions_dict = message.get('message', {}).get('message', {})
                transformed_positions = {}
                for client_id, pos_dict in player_positions_dict.items():
                    # Extract 'x' and 'y' directly
                    x, y = pos_dict['x'], pos_dict['y']
                    transformed_positions[client_id] = (x, y)
                self.players = transformed_positions
                print(f"Updated player positions: {self.players}")
        except:
            print('could not process udp message')
            pass

    def send_player_position_tcp(self):
        # Send the current player position to the server
        message = {'client_id': self.client_id, 'type': 'player_pos_update', 'message': self.player_pos}
        self.network_client.send_tcp_message(message)
    
    def send_player_position_udp(self):
        # Send the current player position to the server
        message = {'client_id': self.client_id, 'type': 'player_pos_update', 'message': self.player_pos}
        self.network_client.send_udp_message(message)

    def game_loop(self):
        clock = pygame.time.Clock()
        #initialize connection messages
        self.network_client.send_tcp_message({'client_id': self.client_id, 'type': 'initialize', 'message': 'client id send'})
        self.network_client.send_udp_message({'client_id': self.client_id, 'type': 'initialize', 'message': 'Initialize UDP bind'})
        time.sleep(1)
        self.send_player_position_tcp()  # Send initial position to server
        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False

            # Handle movement
            keys = pygame.key.get_pressed()
            if keys[pygame.K_w]:
                self.player_pos[1] -= self.player_speed
            if keys[pygame.K_s]:
                self.player_pos[1] += self.player_speed
            if keys[pygame.K_a]:
                self.player_pos[0] -= self.player_speed
            if keys[pygame.K_d]:
                self.player_pos[0] += self.player_speed
            
            # Send updated position to the server
            self.send_player_position_udp()
            #print('post player send')
            # Render
            self.screen.fill((0, 0, 0))  # Clear screen
            #print('cleared the screen')
            for client_id, (x, y) in self.players.items():  # Unpack positions directly
                #print('passed for loop in render')
                color = self.player_color.get(client_id, (255, 255, 255))  # Default to white if ID not found
                #print('assigned color')
                pygame.draw.rect(self.screen, color, (x, y, *self.player_size))
                #print('drew rects')
            pygame.display.flip()
            
            clock.tick(60)  # Cap at 60 FPS

        pygame.quit()

# Initialize and run the game
if __name__ == "__main__":
    HOST = '127.0.0.1'
    TCP_PORT = 12345
    UDP_PORT = 12346
    UDP_LISTEN_PORT = 12347
    client_id = input("Enter your client ID (1-4): ").strip()
    game = Game(HOST, TCP_PORT, UDP_PORT, UDP_LISTEN_PORT, client_id)
    game.game_loop()   
    
    '''def run(self):
        print("Game loop starting. Listening for network messages...")
        protocol = "TCP"  # Default protocol
        #initialize connection messages
        self.network_client.send_tcp_message({'client_id': self.client_id, 'type': 'initialize', 'message': 'client id send'})
        self.network_client.send_udp_message({'client_id': self.client_id, 'type': 'initialize', 'message': 'Initialize UDP bind'})
        self.send_player_position_tcp()  # Send initial position to server
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
            elif message.lower() == "/sendplayerpos":
                self.send_player_position_tcp()
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
    UDP_LISTEN_PORT = 12347
    client_id = input("Enter your client ID (1-4): ").strip()
    game = Game(HOST, TCP_PORT, UDP_PORT, UDP_LISTEN_PORT, client_id)
    game.run()'''
