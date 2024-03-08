import pygame
import math
import random


class DamageNumber(pygame.sprite.Sprite):
    def __init__(self, position, damage, font):
        super().__init__()
        self.image = font.render(str(damage), True, (255, 0, 0))  # Red color for visibility
        self.rect = self.image.get_rect(center=position)
        self.y = float(self.rect.y)
        self.x = float(self.rect.x)
        
        # Set the movement direction
        angle_degrees = random.uniform(90 -15, 90 + 15)  # Half of 30 degrees to each side
        angle_radians = math.radians(angle_degrees)
        
        # Movement speed
        self.speed = 2  # Adjust as needed
        
        # Calculate movement vector
        self.dx = self.speed * math.cos(angle_radians)
        self.dy = -self.speed * math.sin(angle_radians)  # Negative because y increases downwards
        
        self.counter = 30  # Display time

    def update(self):
        # Apply movement vector
        self.x += self.dx
        self.y += self.dy
        
        # Update rect position
        self.rect.x = int(self.x)
        self.rect.y = int(self.y)
        
        self.counter -= 1
        if self.counter <= 0:
            self.kill()  # Remove after time expires

