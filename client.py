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
                #print('message after unpickling in receive_data function: '+ str(message))
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
        else:
            print("Unexpected message type received:", message_type)

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

                screen.fill((0, 0, 0))
                for idx, pos in enumerate(self.game_state):
                    color = self.colors[idx % len(self.colors)]
                    pygame.draw.rect(screen, color, (*pos, 50, 50))

                pygame.display.flip()
                clock.tick(60)

if __name__ == "__main__":
    Client().game_loop()
