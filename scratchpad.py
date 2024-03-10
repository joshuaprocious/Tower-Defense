
to build game into .exe: pyinstaller --onefile game.py

hit_enemies = pygame.sprite.spritecollide(bullet, enemies, False)  # Changed dokill to False
        for enemy in hit_enemies:
            damage_pos = enemy.rect.midtop  # Position to display the damage number
            damage_number = DamageNumber(damage_pos, damage_amount, health_font)
            damage_numbers.add(damage_number)
            enemy.take_damage(25)  # Example damage value
            bullet.kill()  # Remove the bullet after collision