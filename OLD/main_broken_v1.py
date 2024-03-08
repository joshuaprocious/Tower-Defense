import pygame
import sys
import random
import math

# Initialize Pygame
pygame.init()

# Set up the screen
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Tower Defense Game")

# Define colors
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
GREY = (128, 128, 128)
BLACK = (0, 0, 0)

# Define constants
TOWER_SIZE = 50
TOWER_COLOR = GREY
TOWER_MAX_HEALTH = 100
ENEMY_SPAWN_RATE = 2000  # Spawn every 2000 milliseconds
ENEMY_SPEED = 50
ENEMY_DAMAGE = 1
ENEMY_SIZE = 10
ENEMY_MAX_HEALTH = 1

# Define font
font = pygame.font.Font(None, 24)

class Tower(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.Surface((TOWER_SIZE, TOWER_SIZE))
        self.image.fill(TOWER_COLOR)
        self.rect = self.image.get_rect(center=(WIDTH // 2, HEIGHT // 2))
        self.max_health = TOWER_MAX_HEALTH
        self.health = self.max_health

    def draw_health_bar(self, screen):
        # Calculate width of health bar based on current health
        health_bar_width = int(self.rect.width * (self.health / self.max_health))
        health_bar_surface = pygame.Surface((health_bar_width, 5))
        health_bar_surface.fill(GREEN)
        # Position the health bar above the tower
        screen.blit(health_bar_surface, (self.rect.x, self.rect.y - 10))

    def update(self):
        pass  # Updated health bar drawing is handled in the game loop now

class Enemy(pygame.sprite.Sprite):
    def __init__(self, tower):
        super().__init__()
        self.image = pygame.Surface((ENEMY_SIZE, ENEMY_SIZE))
        self.image.fill(RED)
        self.rect = self.image.get_rect()
        self.spawn_side = random.choice(["left", "right", "top", "bottom"])
        self.speed = ENEMY_SPEED / 100.0  # Convert to a decimal scale for movement
        self.health = ENEMY_MAX_HEALTH
        self.tower = tower
        self.set_initial_position()  # Set the initial position based on spawn side

    def set_initial_position(self):
        # Set initial position based on spawn side
        if self.spawn_side == "left":
            self.rect.x = -ENEMY_SIZE
            self.rect.y = random.randrange(HEIGHT)
        elif self.spawn_side == "right":
            self.rect.x = WIDTH
            self.rect.y = random.randrange(HEIGHT)
        elif self.spawn_side == "top":
            self.rect.x = random.randrange(WIDTH)
            self.rect.y = -ENEMY_SIZE
        elif self.spawn_side == "bottom":
            self.rect.x = random.randrange(WIDTH)
            self.rect.y = HEIGHT

    def update(self):
        dx = self.tower.rect.centerx - self.rect.centerx
        dy = self.tower.rect.centery - self.rect.centery
        distance = math.sqrt(dx ** 2 + dy ** 2)
        if distance != 0:
            dx /= distance
            dy /= distance
            # Apply scaled speed to movement
            self.rect.x += dx * (self.speed * 0.5)  # Adjust multiplier for fine control
            self.rect.y += dy * (self.speed * 0.5)


    def check_collision(self):
        if pygame.sprite.collide_rect(self, self.tower):
            self.tower.health -= ENEMY_DAMAGE
            self.kill()

def game_loop():
    all_sprites = pygame.sprite.Group()
    tower = Tower()
    all_sprites.add(tower)
    enemies = pygame.sprite.Group()
    last_spawn_time = pygame.time.get_ticks()

    running = True
    while running:
        current_time = pygame.time.get_ticks()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # Spawn new enemies based on timer
        if current_time - last_spawn_time > ENEMY_SPAWN_RATE:
            enemy = Enemy(tower)
            all_sprites.add(enemy)
            enemies.add(enemy)
            last_spawn_time = current_time
            print("Enemy spawned")  # Debug print to confirm enemy spawning

        all_sprites.update()

        for enemy in enemies:
            enemy.check_collision()

        screen.fill(WHITE)

        # Draw all sprites
        all_sprites.draw(screen)

        # Draw the health bar for the tower
        tower.draw_health_bar(screen)

        # Check for game over
        if tower.health <= 0:
            print("Game Over")
            running = False

        pygame.display.flip()

    pygame.quit()
    sys.exit()

game_loop()
