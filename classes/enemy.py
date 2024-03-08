import pygame
import random
import math
from pygame.math import Vector2
from classes.bullet import Bullet


SCREEN_WIDTH, SCREEN_HEIGHT = 1080, 920
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

class Enemy(pygame.sprite.Sprite):
    def __init__(self, destination):
        super().__init__()
        self.surf = pygame.Surface((20, 20))  # Size of the enemy
        self.surf.fill((255, 0, 0))  # Enemy color
        
        # Adjusted initial position to ensure spawning off-screen
        edge = random.choice(["top", "bottom", "left", "right"])
        if edge == "top":
            x = random.randint(0, SCREEN_WIDTH)
            y = -self.surf.get_height()
        elif edge == "bottom":
            x = random.randint(0, SCREEN_WIDTH)
            y = SCREEN_HEIGHT + self.surf.get_height()
        elif edge == "left":
            x = -self.surf.get_width()
            y = random.randint(0, SCREEN_HEIGHT)
        else:  # "right"
            x = SCREEN_WIDTH + self.surf.get_width()
            y = random.randint(0, SCREEN_HEIGHT)

        self.position = pygame.math.Vector2(x, y)
        self.rect = self.surf.get_rect(center=(self.position.x, self.position.y))

        self.speed = random.uniform(0.5, 1)  # Adjusted speed for demonstration
        self.destination = destination
        self.health = 100  # Starting health
        self.max_health = 100  # Maximum health

    def update(self):
        direction = pygame.math.Vector2(self.destination.rect.centerx - self.position.x, 
                                        self.destination.rect.centery - self.position.y)
        if direction.length() != 0:
            direction = direction.normalize()
        
        # Move the enemy towards the tower, using the position Vector2 for sub-pixel movement
        self.position += direction * self.speed
        # Update rect position
        self.rect.center = self.position
    
    def draw_health_bar(self, surface, font):
        # Constants for the health bar's size and offset
        BAR_WIDTH = 20
        BAR_HEIGHT = 5
        OFFSET_Y = 10  # Distance above the enemy sprite
        
        # Calculate the health bar's position (centered above the enemy sprite)
        bar_x = self.rect.centerx - BAR_WIDTH // 2
        bar_y = self.rect.top - OFFSET_Y
        
        # Calculate the width of the health bar's filled portion
        fill_width = int(BAR_WIDTH * (self.health / self.max_health))
        
        # Ensure fill_width does not exceed BAR_WIDTH
        fill_width = min(fill_width, BAR_WIDTH)
        
        # Draw the background of the health bar (empty part)
        background_rect = pygame.Rect(bar_x, bar_y, BAR_WIDTH, BAR_HEIGHT)
        pygame.draw.rect(surface, (128, 128, 128), background_rect)
        
        # Draw the filled portion of the health bar
        filled_rect = pygame.Rect(bar_x, bar_y, fill_width, BAR_HEIGHT)
        pygame.draw.rect(surface, (0, 255, 0), filled_rect)

        # Text rendering for current health
        health_text = font.render(str(self.health), True, (255, 255, 255))  # White text
        text_x = bar_x + BAR_WIDTH + 5  # Positioning the text right of the health bar
        text_y = bar_y
        surface.blit(health_text, (text_x, text_y))




    def take_damage(self, amount):
        """Reduce enemy health by the specified amount."""
        self.health -= amount
        if self.health <= 0:
            self.kill()  # Remove enemy if health is depleted



class ShootingEnemy(Enemy):
    def __init__(self, destination, bullets_group, *args, **kwargs):
        super().__init__(destination, *args, **kwargs)
        self.surf.fill((255, 255, 0))  # Enemy color
        self.shoot_cooldown = 1000  # Time between shots in milliseconds
        self.last_shot_time = pygame.time.get_ticks()
        self.bullets_group = bullets_group
        self.circle_radius = 300  # Distance from tower to start circling
        self.circling_speed = 0.05  # Speed of circling around the tower
        self.angle = 0  # Initial angle for circling

    def update(self):
        direction = pygame.math.Vector2(self.destination.rect.centerx - self.position.x, 
                                        self.destination.rect.centery - self.position.y)
        if direction.length() != 0:
            direction = direction.normalize()
        
        # Move the enemy towards the tower, using the position Vector2 for sub-pixel movement
        self.position += direction * self.speed
        # Update rect position
        self.rect.center = self.position

        # Shooting logic remains the same
        current_time = pygame.time.get_ticks()
        if current_time - self.last_shot_time >= self.shoot_cooldown:
            self.shoot()
            self.last_shot_time = current_time

    def circle_around_tower(self, tower_center):
        # Increment angle to move in a circle
        self.angle += self.circling_speed
        if self.angle > 2 * math.pi:
            self.angle -= 2 * math.pi  # Reset angle to keep it within 0 to 2π

        # Calculate new position around the tower
        circle_x = tower_center.x + self.circle_radius * math.cos(self.angle)
        circle_y = tower_center.y + self.circle_radius * math.sin(self.angle)

        # Update enemy position
        self.rect.center = (circle_x, circle_y)

    def shoot(self):
        new_bullet = Bullet(self.rect.center, self.destination.rect.center, from_enemy=True)
        self.bullets_group.add(new_bullet)