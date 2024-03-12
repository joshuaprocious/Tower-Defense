import pygame
import sys
import random
import math
from classes.player import Player
from classes.tower import Tower
from classes.enemy import Enemy, ShootingEnemy
from classes.bullet import Bullet
from classes.perks import Perk
from classes.debris import Debris
from classes.damage_number import DamageNumber
from classes.defense_tower import DefenseTower

# Initialize Pygame
pygame.init()
pygame.font.init()

# Screen dimensions
SCREEN_WIDTH, SCREEN_HEIGHT = 1440, 1080
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

# Colors and Fonts
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
score_font = pygame.font.SysFont('Arial', 30)
debris_font = pygame.font.SysFont('Arial', 20)
health_font = pygame.font.SysFont('Arial', 14)

# Game States
class GameState:
    MAIN_MENU = 1
    GAMEPLAY = 2
    GAME_OVER = 3

# Current game state
current_state = GameState.MAIN_MENU

# Game Entities
player = Player()
tower = Tower()
tower.rect.center = (SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2)

# Game Variables
perk_active = False
mouse_button_down = False
last_shot_time = 0
shot_cooldown = 100
score = 0
current_wave = 1
enemy_health_increment = 40
enemy_count_increment = 1
enemies_per_wave = 25
center_position = tower.rect.center  # Assuming 'tower' is your main tower instance
radius = 200
num_towers = 10



# Sprite Groups
enemies = pygame.sprite.Group()
bullets = pygame.sprite.Group()
perks = pygame.sprite.Group()
debris_group = pygame.sprite.Group()
damage_numbers = pygame.sprite.Group()
defense_towers = pygame.sprite.Group()

# Functions (adapt existing functions here, unchanged)

def spawn_debris(debris_group, position):
    for _ in range(random.randint(2, 4)):
        debris_piece = Debris(position)
        debris_group.add(debris_piece)

def initial_spawn_defense_towers(center_position, tower_radius, num_towers, defense_towers_group):
        centerX, centerY = center_position
        for i in range(num_towers):
            angle = (2 * math.pi / num_towers) * i  # Divide the circle into num_towers parts
            x = centerX + tower_radius * math.cos(angle)
            y = centerY + tower_radius * math.sin(angle)

            # Assuming DefenseTower class has an __init__ that takes position as a tuple
            new_tower = DefenseTower((x, y))
            defense_towers_group.add(new_tower)

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

def handle_mouse_input(event, player, bullets, perk_active, last_shot_time, shot_cooldown, defense_towers):
    global mouse_button_down
    if event.type == pygame.MOUSEBUTTONDOWN:
        mouse_button_down = True
        if not perk_active:
            shoot_bullet(player, bullets)
    elif event.type == pygame.MOUSEBUTTONUP:
        mouse_button_down = False
    elif event.type == pygame.KEYDOWN:
        if event.key == pygame.K_1:  # Press "1" to spawn a defense tower
            new_tower = DefenseTower(player.rect.center)
            defense_towers.add(new_tower)
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
    defense_towers.update(enemies, bullets)
    debris_group.update()

def handle_collisions(player, enemies, bullets, tower, debris_group, perks, update_score):
    global perk_active
    damage_amount = 25
    # Check bullet-enemy collisions using rect-based collision detection
    for bullet in bullets.sprites():
        # The third argument 'True' tells Pygame to remove the collided enemies from the group
        if bullet.from_enemy and pygame.sprite.collide_rect(bullet, tower):
            tower_damaged_basic_bullet = 1
            tower.health -= 1  # Adjust the damage as needed
            # Create and add damage number
            damage_pos = (tower.rect.centerx, tower.rect.top)  # Position above the tower
            damage_number = DamageNumber(damage_pos, tower_damaged_basic_bullet, health_font)
            damage_numbers.add(damage_number)
            bullet.kill()
        if not bullet.from_enemy:  # This ensures the bullet is from the player
            hit_enemies = pygame.sprite.spritecollide(bullet, enemies, False)
            for enemy in hit_enemies:
                enemy.take_damage(damage_amount)
                damage_pos = enemy.rect.midtop  # Position to display the damage number
                damage_number = DamageNumber(damage_pos, damage_amount, health_font)
                damage_numbers.add(damage_number)
                bullet.kill()
                if enemy.health <= 0:
                    update_score(1)  # Update the score for killing an enemy
                    spawn_debris(debris_group, enemy.rect.center)  # Spawn debris here, inside the health check
                    enemy.kill()  # Now remove the enemy since it's health is 0 or below
        if pygame.sprite.collide_rect(bullet, tower) and not bullet.from_enemy:
            tower_damaged_basic_bullet = 1
            tower.health -= 1  # Adjust damage as needed
            # Create and add damage number
            
            bullet.kill()
    # Check each enemy for collision with the tower
    for enemy in enemies.sprites():
        if pygame.sprite.collide_rect(enemy, tower):
            tower_damaged_basic_evemy_impact = 10
            tower.health -= 10  # Example damage value to the tower
            damage_pos = (tower.rect.centerx, tower.rect.top)  # Position above the tower
            damage_number = DamageNumber(damage_pos, tower_damaged_basic_evemy_impact, health_font)
            damage_numbers.add(damage_number)
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
            # Calculate the health needed to fully restore the tower
            health_needed = tower.max_health - tower.health
            # Calculate how many debris points are required to restore that health
            debris_required = math.ceil(health_needed / 5)  # Assuming each debris point restores 5 health
            
            # Use only as many debris points as needed or available, whichever is less
            debris_used = min(debris_required, player.collected_debris)
            
            # Calculate the actual health restoration
            health_restoration = debris_used * 5
            # Increase the tower's health by this amount, up to its maximum
            tower.health += health_restoration
            # Ensure the tower's health does not exceed its maximum
            tower.health = min(tower.health, tower.max_health)
            
            # Decrease the player's collected debris by the amount used
            player.collected_debris -= debris_used
   
def spawn_enemies(enemies, wave):
    global enemies_per_wave, enemy_health_increment
    for _ in range(enemies_per_wave + (wave - 1) * enemy_count_increment):
        new_enemy = Enemy(tower) 
        new_enemy.health += (wave - 1) * enemy_health_increment
        enemies.add(new_enemy)
    for _ in range(wave):
        shooting_enemy = ShootingEnemy(tower, bullets)
        enemies.add(shooting_enemy)

def draw_game_elements(screen, entities, score, player):
    # Fill the screen with a background color
    screen.fill(BLACK)
    tower.draw_health_bar(screen, health_font)
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
    if current_wave == 1:
        initial_spawn_defense_towers(center_position, radius, num_towers, defense_towers)
    if not enemies:  # If all enemies are defeated
        current_wave += 1
        spawn_enemies(enemies, current_wave)

def display_wave_info(screen, wave):
    font = pygame.font.SysFont("arial", 30)
    wave_surface = font.render(f"Wave: {wave}", True, (255, 255, 255))
    wave_rect = wave_surface.get_rect(topright=(SCREEN_WIDTH - 20, 50))
    screen.blit(wave_surface, wave_rect)

# Handle Main Menu
def handle_main_menu(events):
    for event in events:
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN:  # Start the game when Enter is pressed
                global current_state
                current_state = GameState.GAMEPLAY

    screen.fill(BLACK)
    menu_text = score_font.render('Press Enter to Start', True, WHITE)
    text_rect = menu_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
    screen.blit(menu_text, text_rect)

# Handle Gameplay
def handle_gameplay(events):
    global current_state, score, perk_active, last_shot_time, mouse_button_down, automatic_shoot_last_time, automatic_shooting_enabled
    for event in events:
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            current_state = GameState.MAIN_MENU
        handle_mouse_input(event, player, bullets, perk_active, last_shot_time, shot_cooldown, defense_towers)
    
    pressed_keys = pygame.key.get_pressed()
    update_game_state(enemies, bullets, player, pressed_keys, damage_numbers)
    handle_collisions(player, enemies, bullets, tower, debris_group, perks, update_score)

    if perk_active and not automatic_shooting_enabled:
        automatic_shooting_enabled = True
        automatic_shoot_last_time = pygame.time.get_ticks()

    if automatic_shooting_enabled and mouse_button_down:
        current_time = pygame.time.get_ticks()
        if current_time - automatic_shoot_last_time > shot_cooldown:
            shoot_bullet(player, bullets)
            automatic_shoot_last_time = current_time

    screen.fill(BLACK)
    draw_game_elements(screen, [*enemies, *bullets, player, tower, *debris_group, *perks, *damage_numbers, *defense_towers], score, player)
    display_wave_info(screen, current_wave)
    check_wave_completion(enemies)

    if tower.health <= 0:
        current_state = GameState.GAME_OVER

# Handle Game Over
def handle_game_over(events):
    global current_state, score, perk_active, last_shot_time, mouse_button_down, automatic_shoot_last_time, automatic_shooting_enabled, current_wave
    for event in events:
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_r:  # Restart the game
                setup_game()
                current_state = GameState.GAMEPLAY
               
                

    screen.fill(BLACK)
    game_over_text = score_font.render('Game Over - Press R to Restart', True, WHITE)
    text_rect = game_over_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
    screen.blit(game_over_text, text_rect)

#this initializes game variables on start or restart
def setup_game():
    global player, tower, enemies, bullets, perks, debris_group, damage_numbers, score, current_wave, perk_active, automatic_shooting_enabled, automatic_shoot_last_time
    player = Player()
    tower = Tower()
    tower.rect.center = (SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2)
    enemies = pygame.sprite.Group()
    bullets = pygame.sprite.Group()
    perks = pygame.sprite.Group()
    debris_group = pygame.sprite.Group()
    damage_numbers = pygame.sprite.Group()
    score = 0
    current_wave = 1
    perk_active = False
    enemies.empty()
    bullets.empty()
    perks.empty()
    debris_group.empty()
    damage_numbers.empty()
    defense_towers.empty()
    automatic_shooting_enabled = True
    automatic_shoot_last_time = 0
        # Example usage
    center_position = tower.rect.center  # Assuming 'tower' is your main tower instance
    radius = 200
    num_towers = 10
    initial_spawn_defense_towers(center_position, radius, num_towers, defense_towers)

clock = pygame.time.Clock()
def main():
    running = True
    dt = clock.tick(60) / 1000  # Convert milliseconds to seconds
    while running:
        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT:
                running = False

        if current_state == GameState.MAIN_MENU:
            handle_main_menu(events)
        elif current_state == GameState.GAMEPLAY:
            handle_gameplay(events)
        elif current_state == GameState.GAME_OVER:
            handle_game_over(events)

        pygame.display.flip()
        clock.tick(60)

if __name__ == "__main__":
    setup_game()
    main()
    pygame.quit()
    sys.exit()
