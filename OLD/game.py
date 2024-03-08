import pygame
import sys
import random
from classes.player import Player
from classes.tower import Tower
from classes.enemy import Enemy
from classes.bullet import Bullet
from classes.perks import Perk
from classes.debris import Debris
from classes.damage_number import DamageNumber

# Initialize 
pygame.init()
pygame.font.init()



#VARIABLES AND SCREEN------------------------------------------------


# Screen dimensions
SCREEN_WIDTH, SCREEN_HEIGHT = 1080, 920
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

score_font = pygame.font.SysFont('Arial', 30)
debris_font = pygame.font.SysFont('Arial', 20)
health_font = pygame.font.SysFont('Arial', 14)

#Functions--------------------------------------------------------------

def spawn_debris(debris_group, position):
    for _ in range(random.randint(2, 4)):
        debris_piece = Debris(position)
        debris_group.add(debris_piece)

def display_score_and_debris(screen, score, collected_debris):
    font = pygame.font.SysFont("arial", 20)
    score_surface = font.render(f"Score: {score}", True, (255, 255, 255))
    debris_surface = font.render(f"Debris Collected: {collected_debris}", True, (255, 255, 255))

    score_rect = score_surface.get_rect(topright=(SCREEN_WIDTH - 20, 10))
    debris_rect = debris_surface.get_rect(topleft=(20, 10))

    screen.blit(score_surface, score_rect)
    screen.blit(debris_surface, debris_rect)

def display_game_over(screen):
    font = pygame.font.SysFont("arial", 64)
    text_surface = font.render("Game Over", True, (255, 0, 0))
    text_rect = text_surface.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
    screen.blit(text_surface, text_rect)
    pygame.display.flip()
    pygame.time.wait(2000)  # Wait for 2 seconds before continuing or closing

def update_score(amount):
    global score
    score += amount

def handle_mouse_input(event, player, bullets, perk_active, last_shot_time, shot_cooldown):
    global mouse_button_down
    if event.type == pygame.MOUSEBUTTONDOWN:
        mouse_button_down = True
        if not perk_active:
            shoot_bullet(player, bullets)
    elif event.type == pygame.MOUSEBUTTONUP:
        mouse_button_down = False
    return last_shot_time

def shoot_bullet(player, bullets):
    target_pos = pygame.mouse.get_pos()
    new_bullet = Bullet(player.rect.center, target_pos)
    bullets.add(new_bullet)

def update_game_state(enemies, bullets, player, pressed_keys, damage_numbers):
    enemies.update()
    bullets.update()  # Assuming bullets have an update method to move them
    player.update(pressed_keys)  # Assuming player has an update method
    damage_numbers.update()
def handle_collisions(player, enemies, bullets, tower, debris_group, perks, update_score):
    global perk_active
    damage_amount = 25
    # Check bullet-enemy collisions using rect-based collision detection
    for bullet in bullets.sprites():
        # The third argument 'True' tells Pygame to remove the collided enemies from the group
        hit_enemies = pygame.sprite.spritecollide(bullet, enemies, False)  # Changed dokill to False
        for enemy in hit_enemies:
            damage_pos = enemy.rect.midtop  # Position to display the damage number
            damage_number = DamageNumber(damage_pos, damage_amount, health_font)
            damage_numbers.add(damage_number)
            enemy.take_damage(25)  # Example damage value
            bullet.kill()  # Remove the bullet after collision
            if enemy.health <= 0:
                update_score(1)  # Update the score for killing an enemy
                spawn_debris(debris_group, enemy.rect.center)  # Spawn debris here, inside the health check
                enemy.kill()  # Now remove the enemy since it's health is 0 or below
    
    # Check each enemy for collision with the tower
    for enemy in enemies.sprites():
        if pygame.sprite.collide_rect(enemy, tower):
            tower.health -= 10  # Example damage value to the tower
            enemy.kill()  # Assuming you want to remove the enemy upon collision
            # You might want to spawn debris or trigger some effect here as well

    
    # Example implementation of checking for player-perk collision
    if pygame.sprite.spritecollideany(player, perks):
        # Activate perk effect here, assuming perks are removed on collision
        perk_active = True
        # Remove the perk once collected
        for perk in perks:
            perk.kill()
        
        pass
    # Check for player-debris collisions
    collected_debris = pygame.sprite.spritecollide(player, debris_group, dokill=True)  # dokill=True to remove debris on collision
    if collected_debris:
        player.collected_debris += len(collected_debris)  # Increment player's collected debris count
    
    # Check for player-tower collision and apply debris effect
    if pygame.sprite.collide_rect(player, tower):
        # If the player is carrying debris, apply effects (like restoring health to the tower)
        if player.collected_debris > 0:
            tower.health += player.collected_debris * 5  # Example health restoration
            player.collected_debris = 0  # Reset collected debris count
            if tower.health > tower.max_health:  # Clamp tower health to its max value
                tower.health = tower.max_health
    
def spawn_enemies(enemies, wave):
    global enemies_per_wave, enemy_health_increment
    for _ in range(enemies_per_wave + (wave - 1) * enemy_count_increment):
        new_enemy = Enemy(tower) 
        new_enemy.health += (wave - 1) * enemy_health_increment
        enemies.add(new_enemy)

def draw_game_elements(screen, entities, score, player):
    # Fill the screen with a background color
    screen.fill(BLACK)
    tower.draw_health_bar(screen)
    # Draw each entity in the list
    for entity in entities:
        if hasattr(entity, 'image'):
            screen.blit(entity.image, entity.rect)
        # If not, check for a 'surf' attribute and use that
        elif hasattr(entity, 'surf'):
            screen.blit(entity.surf, entity.rect)
        else:
            # Log an error or raise an exception if neither attribute is found
            print(f"Error: Entity {entity} does not have an 'image' or 'surf' attribute.")
    for enemy in enemies:
        screen.blit(enemy.surf, enemy.rect)
        enemy.draw_health_bar(screen, health_font)  # Draw the health bar for each enemy
    #Update and draw perks
    for perk in perks:
        screen.blit(perk.surf, perk.rect)
    #spawn perks for player
    if len(perks) == 0 and random.randint(1, 500) == 1:  # Adjust spawn rate as needed
        new_perk = Perk()
        perks.add(new_perk)
    for debris in debris_group:
        screen.blit(debris.surf, debris.rect)
    #draw damage numbers
    for damage_number in damage_numbers:
        screen.blit(damage_number.image, damage_number.rect)
    # Draw the score
    score_text = score_font.render(f'Score: {score}', True, (255, 255, 255))
    score_rect = score_text.get_rect(topright=(SCREEN_WIDTH - 20, 10))
    screen.blit(score_text, score_rect)

    # Draw the player's collected debris count
    debris_text = debris_font.render(f'Debris Collected: {player.collected_debris}', True, (255, 255, 255))
    debris_rect = debris_text.get_rect(topleft=(20, 10))
    screen.blit(debris_text, debris_rect)

def check_wave_completion(enemies):
    global current_wave
    if not enemies:  # If all enemies are defeated
        current_wave += 1
        spawn_enemies(enemies, current_wave)

def display_wave_info(screen, wave):
    font = pygame.font.SysFont("arial", 20)
    wave_surface = font.render(f"Wave: {wave}", True, (255, 255, 255))
    wave_rect = wave_surface.get_rect(topleft=(SCREEN_WIDTH - 200, 10))
    screen.blit(wave_surface, wave_rect)

#GROUPS---------------------------------------------------------------

# Enemy management
enemies = pygame.sprite.Group()
#ENEMY_SPAWN = pygame.USEREVENT + 1
#pygame.time.set_timer(ENEMY_SPAWN, 500)  # Adjust spawn rate as needed
# Assuming you have a 'bullets' pygame.sprite.Group to manage bullets
bullets = pygame.sprite.Group()
# Perk group for easier management
perks = pygame.sprite.Group()
#debris group
debris_group = pygame.sprite.Group()
#damage number group
damage_numbers = pygame.sprite.Group()

#CREATE GAME ENTITIES--------------------------------------------------

# Create a player instance
player = Player()
# Create a tower instance
tower = Tower()
tower.rect.center = (SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2)  # Positioning the tower
# Option to track if the perk is active
perk_active = False
# Tracking mouse button state
mouse_button_down = False
last_shot_time = 0
shot_cooldown = 100  # Cooldown time in milliseconds (0.5 seconds for example)
automatic_shooting_enabled = False
automatic_shoot_last_time = 0
score = 0  # Initialize score
current_wave = 0
enemy_health_increment = 20  # Increase in health per wave
enemy_count_increment = 2  # Increase in enemy count per wave
enemies_per_wave = 5  # Starting number of enemies


# Game loop
running = True

while running:
    current_time = pygame.time.get_ticks()
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            running = False
        elif tower.health <= 0:
            display_game_over(screen)  # Assumes implementation
            running = False
        '''elif event.type == ENEMY_SPAWN:
            new_enemy = Enemy(tower)  # Make sure Enemy initialization is correct
            enemies.add(new_enemy)  # Confirm enemies is a pygame.sprite.Group'''
        handle_mouse_input(event, player, bullets, perk_active, last_shot_time, shot_cooldown)
    

    pressed_keys = pygame.key.get_pressed()
    update_game_state(enemies, bullets, player, pressed_keys, damage_numbers)
    handle_collisions(player, enemies, bullets, tower, debris_group, perks, update_score)

    all_entities = [*enemies, *bullets, player, tower, *debris_group, *perks, *damage_numbers]  # Aggregate all drawable entities
    draw_game_elements(screen, all_entities, score, player)
    if perk_active and not automatic_shooting_enabled:
        automatic_shooting_enabled = True
        automatic_shoot_last_time = pygame.time.get_ticks()

    if automatic_shooting_enabled and mouse_button_down:
        current_time = pygame.time.get_ticks()
        if current_time - automatic_shoot_last_time > shot_cooldown:
            shoot_bullet(player, bullets)
            automatic_shoot_last_time = current_time
    
    check_wave_completion(enemies)
    display_wave_info(screen, current_wave)

    pygame.display.flip()
    
    


game_over_font = pygame.font.SysFont("Arial", 72)
game_over_surface = game_over_font.render("Game Over", True, (255, 0, 0))
game_over_rect = game_over_surface.get_rect(center=(SCREEN_WIDTH/2, SCREEN_HEIGHT/2))
screen.fill((0, 0, 0))
screen.blit(game_over_surface, game_over_rect)
pygame.display.flip()
pygame.time.wait(3000)

# Quit Pygame
pygame.quit()
sys.exit()
