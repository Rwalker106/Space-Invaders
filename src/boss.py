import pygame
import random
from src.bullet import Bullet

class Boss(pygame.sprite.Sprite):
    def __init__(self, game, level):
        super().__init__()
        self.game = game
        self.settings = game.settings
        self.level = level
        
        # Scale boss health and speed based on the current level
        self.max_health = 20 + (level * 2)
        self.health = self.max_health
        self.speed = 2 + (level * 0.1)
        self.direction = 1
        
        # Load boss image based on level
        boss_index = ((level // 5) - 1) % 6 + 1
        image_path = f"assets/images/boss_{boss_index}.png"
        try:
            loaded_image = pygame.image.load(image_path).convert_alpha()
            # Scale it to a reasonable boss size if needed
            self.image = pygame.transform.scale(loaded_image, (150, 100))
        except:
            # Fallback just in case
            self.image = pygame.Surface((150, 100), pygame.SRCALPHA)
            self.image.fill((200, 0, 50))
        
        self.rect = self.image.get_rect()
        self.rect.centerx = self.settings.screen_width // 2
        self.rect.top = 50
        
        self.shoot_timer = 0
        self.shoot_interval = max(0.5, 2.0 - (level * 0.05)) # Boss shoots faster at higher levels

    def update(self):
        # Move side to side
        self.rect.x += self.speed * self.direction
        
        # Bounce off edges
        if self.rect.right >= self.settings.screen_width:
            self.direction = -1
        elif self.rect.left <= 0:
            self.direction = 1
            
        # Shooting logic
        self.shoot_timer -= 1 / self.settings.fps
        if self.shoot_timer <= 0:
            self.shoot()
            self.shoot_timer = self.shoot_interval
            
    def shoot(self):
        self.game.invader_shoot_sfx.play()
        # Boss shoots 3 bullets at once
        offsets = [-40, 0, 40]
        for offset in offsets:
            if offset == 0 and hasattr(self.game, 'player') and self.game.player:
                # Smart targeting for the middle bullet
                import math
                dx = self.game.player.rect.centerx - (self.rect.centerx + offset)
                dy = self.game.player.rect.centery - self.rect.bottom
                dist = math.hypot(dx, dy)
                if dist != 0:
                    speed = self.settings.bullet_speed * 1.5
                    b_dx = (dx / dist) * speed
                    b_dy = (dy / dist) * speed
                    bullet = Bullet(self.game, self, direction=1, dx=b_dx, dy=b_dy)
                else:
                    bullet = Bullet(self.game, self, direction=1)
            else:
                bullet = Bullet(self.game, self, direction=1)
                
            bullet.rect.centerx = self.rect.centerx + offset
            bullet.rect.top = self.rect.bottom
            self.game.all_sprites.add(bullet)
            self.game.invader_bullets.add(bullet)

    def take_damage(self):
        self.health -= 1
        if self.health <= 0:
            self.game.invader_killed_sfx.play()
            self.kill()
