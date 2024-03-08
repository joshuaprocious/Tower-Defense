import pygame
import math

# Screen dimensions
SCREEN_WIDTH, SCREEN_HEIGHT = 1080, 920
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

class Bullet(pygame.sprite.Sprite):
    def __init__(self, start_pos, target_pos, from_enemy=False):
        super().__init__()
        self.from_enemy = from_enemy
        self.surf = pygame.Surface((3, 3))
        self.surf.fill((255, 255, 255))  # White or any color you choose
        self.rect = self.surf.get_rect(center=start_pos)

        self.position = pygame.math.Vector2(start_pos)  # Use Vector2 for precise positioning
        self.speed = 10.0  # Maintain speed as a float

        # Calculate direction vector from start_pos to target_pos
        target_vector = pygame.math.Vector2(target_pos) - self.position
        if target_vector.length() > 0:  # Normalize only if vector is not zero
            self.direction = target_vector.normalize()
        else:
            self.direction = pygame.math.Vector2()

    def update(self):
        # Move bullet in the direction, multiplying by speed
        self.position += self.direction * self.speed
        # Update the rect for drawing and collision detection
        self.rect.center = (round(self.position.x), round(self.position.y))

        # Optionally, remove the bullet if it goes off-screen
        if (self.rect.right < 0 or self.rect.left > SCREEN_WIDTH or
                self.rect.top > SCREEN_HEIGHT or self.rect.bottom < 0):
            self.kill()

