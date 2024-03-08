import pygame
import random

class Debris(pygame.sprite.Sprite):
    def __init__(self, position):
        super().__init__()
        self.surf = pygame.Surface((2, 2))  # Make debris smaller
        self.surf.fill((255, 255, 0))  # Example: yellow color
        # Adjust position to spread out debris
        offset_x = random.randint(-10, 10)  # Spread out horizontally
        offset_y = random.randint(-10, 10)  # Spread out vertically
        self.rect = self.surf.get_rect(center=(position[0] + offset_x, position[1] + offset_y))
        self.creation_time = pygame.time.get_ticks()  # Record the creation time
        
    def update(self):
        current_time = pygame.time.get_ticks()
        if current_time - self.creation_time > 10000:  # 10000 milliseconds = 10 seconds
            self.kill()  # Remove this debris instance
