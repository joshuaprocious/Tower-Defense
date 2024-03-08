import pygame
import socket
import pickle
import sys
import threading

class Client:
    def __init__(self, address='127.0.0.1', port=12345):
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client_socket.connect((address, port))
        self.player_id = None  # Player ID will be set upon receiving initial data
        self.game_state = None  # Initial state will be received from the server
        self.colors = [(0, 255, 0), (0, 0, 255), (255, 0, 0), (255, 255, 0)]  # Green, Blue, Red, Yellow

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
                received_data = pickle.loads(data)

                if self.player_id is None:
                    self.player_id, self.game_state = received_data[0], received_data[1]
                else:
                    self.game_state = received_data
            except Exception as e:
                print(f"Error receiving data: {e}")
                self.client_socket.close()
                sys.exit()

    def game_loop(self):
        pygame.init()
        screen = pygame.display.set_mode((500, 500))
        clock = pygame.time.Clock()
        
        threading.Thread(target=self.receive_data, daemon=True).start()
        
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
            
            if self.game_state is not None and self.player_id is not None:
                keys = pygame.key.get_pressed()
                x, y = self.game_state[self.player_id]

                if keys[pygame.K_LEFT]:
                    x -= 5
                if keys[pygame.K_RIGHT]:
                    x += 5
                if keys[pygame.K_UP]:
                    y -= 5
                if keys[pygame.K_DOWN]:
                    y += 5

                self.send_data((self.player_id, (x, y)))  # Send only the updated position
                
                screen.fill((0, 0, 0))
                for idx, pos in enumerate(self.game_state):
                    color = self.colors[idx % len(self.colors)]
                    pygame.draw.rect(screen, color, (*pos, 50, 50))

                pygame.display.flip()
                clock.tick(60)



if __name__ == "__main__":
    Client().game_loop()
