import pygame
import math
from classes.bullet import Bullet

class DefenseTower(pygame.sprite.Sprite):
    def __init__(self, position):
        super().__init__()
        self.image = pygame.Surface((10, 10))  # Adjust size as needed
        self.image.fill((128, 128, 128))  # Grey color
        self.rect = self.image.get_rect(center=position)
        self.shoot_cooldown = 500  # Milliseconds between shots
        self.last_shot_time = pygame.time.get_ticks()

    def update(self, enemies, bullets):
        now = pygame.time.get_ticks()
        if now - self.last_shot_time > self.shoot_cooldown:
            closest_enemy = self.get_closest_enemy(enemies)
            if closest_enemy:
                self.shoot(closest_enemy, bullets)
                self.last_shot_time = now


    def get_closest_enemy(self, enemies):
        closest_enemy = None
        closest_dist_sq = 100**2  # Square of the max distance to consider (100 pixels)
        for enemy in enemies:
            # Calculate the squared distance to avoid sqrt for performance
            dx = self.rect.centerx - enemy.rect.centerx
            dy = self.rect.centery - enemy.rect.centery
            dist_sq = dx**2 + dy**2

            if dist_sq < closest_dist_sq:
                closest_dist_sq = dist_sq
                closest_enemy = enemy
        return closest_enemy


    def shoot(self, target, bullets):
        bullet = Bullet(self.rect.center, target.rect.center)  # Adjust as needed
        bullets.add(bullet)

    