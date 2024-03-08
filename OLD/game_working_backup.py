import pygame
import sys
import random
from classes.player import Player
from classes.tower import Tower
from classes.enemy import Enemy
from classes.bullet import Bullet
from classes.perks import Perk
from classes.debris import Debris

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

#GROUPS---------------------------------------------------------------

# Enemy management
enemies = pygame.sprite.Group()
ENEMY_SPAWN = pygame.USEREVENT + 1
pygame.time.set_timer(ENEMY_SPAWN, 1000)  # Adjust spawn rate as needed
# Assuming you have a 'bullets' pygame.sprite.Group to manage bullets
bullets = pygame.sprite.Group()
# Perk group for easier management
perks = pygame.sprite.Group()
#debris group
debris_group = pygame.sprite.Group()

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
score = 0  # Initialize score

# Game loop flag
running = True

while running:
    current_time = pygame.time.get_ticks()  # Get current time
    if tower.health <= 0:
        running = False
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:  # Check if a key is pressed
            if event.key == pygame.K_ESCAPE:  # Check if the key is the Escape key
                running = False  # Set running to False to exit the game loop
        # Enemy spawn event
        if event.type == ENEMY_SPAWN:
            new_enemy = Enemy(tower)  # Pass the tower as the destination
            enemies.add(new_enemy)
        elif event.type == pygame.MOUSEBUTTONDOWN:
            mouse_button_down = True  # Mouse button is pressed down
            # Shoot a bullet immediately on click, even if perk is not active
            if not perk_active:
                target_pos = pygame.mouse.get_pos()
                new_bullet = Bullet(player.rect.center, target_pos)
                bullets.add(new_bullet)
        elif event.type == pygame.MOUSEBUTTONUP:
            mouse_button_down = False  # Mouse button is released

    # Automatic shooting when perk is active and mouse button is down
    if perk_active and mouse_button_down:
        # Check if enough time has passed since the last shot
        if current_time - last_shot_time >= shot_cooldown:
            target_pos = pygame.mouse.get_pos()
            new_bullet = Bullet(player.rect.center, target_pos)
            bullets.add(new_bullet)
            last_shot_time = current_time  # Update the time of the last shot
    
    # Update enemy positions
    enemies.update()
    # Update player position based on input
    pressed_keys = pygame.key.get_pressed()
    player.update(pressed_keys)


    # Drawing
    
    screen.fill(BLACK)
    #draw scoreboard
    score_text = score_font.render(f'Score: {score}', True, (255, 255, 255))  # Render the score text to a surface
    score_rect = score_text.get_rect(topright=(SCREEN_WIDTH - 20, 10))  # Position the score at the top right
    screen.blit(score_text, score_rect)  # Draw the score text to the screen
    # draw debris counter
    debris_text = debris_font.render(f'Debris Collected: {player.collected_debris}', True, (255, 255, 255))
    # Choose a position for the debris counter, e.g., top left
    debris_rect = debris_text.get_rect(topleft=(20, 10))
    # Draw the debris counter text to the screen
    screen.blit(debris_text, debris_rect)
    #draw tower
    screen.blit(tower.surf, tower.rect)
    #draw player
    screen.blit(player.surf, player.rect)
    tower.draw_health_bar(screen)
    #Update and draw enemies
    for enemy in enemies:
        screen.blit(enemy.surf, enemy.rect)
    # Update and draw bullets
    bullets.update()
    for bullet in bullets:
        screen.blit(bullet.surf, bullet.rect)
    #Update and draw perks
    for perk in perks:
        screen.blit(perk.surf, perk.rect)
    #spawn perks for player
    if len(perks) == 0 and random.randint(1, 500) == 1:  # Adjust spawn rate as needed
        new_perk = Perk()
        perks.add(new_perk)
    for debris in debris_group:
        screen.blit(debris.surf, debris.rect)

    # Collision detection
    
    for enemy in enemies:
        screen.blit(enemy.surf, enemy.rect)
        enemy.draw_health_bar(screen)
        if tower.rect.colliderect(enemy.rect):
            tower.health -= 10  # Adjust damage as needed
            enemies.remove(enemy)  # Remove enemy on collision
    
    for bullet in bullets:
        # Using spritecollide to check for collisions with enemies
        hit_enemies = pygame.sprite.spritecollide(bullet, enemies, False)  # Last arg is do_kill, set to False to not auto-remove
        for enemy in hit_enemies:
            enemy.health -= 25  # Adjust damage
            bullet.kill()  # Remove the bullet
            if enemy.health <= 0:
                enemy.kill()
                score += 1  # Remove the enemy if health is depleted      
                for _ in range(random.randint(2, 4)):  # Spawn 2 to 4 pieces
                    debris_piece = Debris(enemy.rect.center)
                    debris_group.add(debris_piece)

    # Check for collision with the perk
    if pygame.sprite.spritecollideany(player, perks):
        perk_active = True
        # Remove the perk once collected
        for perk in perks:
            perk.kill()
    # Check for player picking up debris
    collected_debris = pygame.sprite.spritecollide(player, debris_group, dokill=True)  # dokill=True removes the debris
    if collected_debris:
        # Assume player has an attribute to store collected debris count
        player.collected_debris += len(collected_debris)
        pygame.display.flip()
    # Check for player colliding with the tower
    if pygame.sprite.collide_rect(player, tower):
        if player.collected_debris > 0:
            tower.health += player.collected_debris * 5  # Example: restore 5 health per debris
            player.collected_debris = 0  # Reset collected debris
            if tower.health > tower.max_health:
                tower.health = tower.max_health

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
