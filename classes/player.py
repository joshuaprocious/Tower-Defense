import pygame
import sys


# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

# Screen dimensions
SCREEN_WIDTH, SCREEN_HEIGHT = 1080, 920
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
clock = pygame.time.Clock()
class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.collected_debris = 0
        self.surf = pygame.Surface((25, 25))
        self.surf.fill((255, 255, 255))  # White square
        self.rect = self.surf.get_rect()
        self.speed = 4 # Set speed to a decimal value
        self.position = pygame.math.Vector2(self.rect.topleft)  # Use a Vector2 for precise positioning

    def update(self, pressed_keys):
        movement = pygame.math.Vector2(0, 0)
        
        if pressed_keys[pygame.K_w]:
            movement.y -= self.speed
        if pressed_keys[pygame.K_s]:
            movement.y += self.speed
        if pressed_keys[pygame.K_a]:
            movement.x -= self.speed
        if pressed_keys[pygame.K_d]:
            movement.x += self.speed

        # Update the position with the precise movement
        self.position += movement

        # Update the rect position using the rounded position to keep it in integer values
        self.rect.topleft = round(self.position.x), round(self.position.y)

        # Keep the player within the screen boundaries
        self.rect.clamp_ip(pygame.Rect(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT))