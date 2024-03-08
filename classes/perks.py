import pygame
import random
import math

SCREEN_WIDTH, SCREEN_HEIGHT = 1080, 920
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

class Perk(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.surf = pygame.Surface((20, 20))  # Size of the perk
        self.surf.fill((0, 255, 0))  # Green color or any color you choose
        self.rect = self.surf.get_rect(
            center=(random.randint(20, SCREEN_WIDTH-20), random.randint(20, SCREEN_HEIGHT-20))
        )
