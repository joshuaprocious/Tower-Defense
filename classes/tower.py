import pygame

class Tower(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.surf = pygame.Surface((50, 50))  # Size of the tower
        self.surf.fill((0, 128, 255))  # Color of the tower
        self.rect = self.surf.get_rect()
        self.health = 500  # Starting health
        self.max_health = 500  # Maximum health

    def draw_health_bar(self, surface, font):
        # Health bar position and size
        bar_position = (self.rect.x, self.rect.y - 10)
        bar_size = (self.rect.width, 5)
        health_percentage = self.health / self.max_health
        health_bar = (bar_position[0], bar_position[1], bar_size[0] * health_percentage, bar_size[1])

        # Draw background bar (grey)
        pygame.draw.rect(surface, (150, 150, 150), (*bar_position, *bar_size))
        # Draw health bar (green)
        pygame.draw.rect(surface, (0, 255, 0), health_bar)

        # Text rendering for current health
        health_text = font.render(str(self.health), True, (255, 255, 255))  # White text
        text_x = self.rect.x + 55 # Positioning the text right of the health bar
        text_y = self.rect.y
        surface.blit(health_text, (text_x, text_y))


        
