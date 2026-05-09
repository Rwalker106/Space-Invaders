from pygame.sprite import Sprite
import pygame
from src import game
from src.bullet import Bullet


class Player(Sprite):
    def __init__(self, game, image=None):

        super().__init__()
        self.game = game
        self.screen = game.screen
        self.settings = game.settings
        if image is None:
            self.image = pygame.Surface((50, 40))
            self.image.fill((0, 255, 0))
        else:
            self.image = image
        self.rect = self.image.get_rect()
        self.rect.centerx = self.screen.get_rect().centerx
        self.rect.bottom = self.screen.get_rect().bottom - 10
        self.shielded = False
        
    def update(self):
        keys = pygame.key.get_pressed()
        if (keys[pygame.K_LEFT] or keys[pygame.K_a]) and self.rect.left > 0:
            self.rect.x -= self.settings.player_speed
        if (keys[pygame.K_RIGHT] or keys[pygame.K_d]) and self.rect.right < self.settings.screen_width:
            self.rect.x += self.settings.player_speed
            
    def shoot(self):
        if getattr(self.game, 'laser_timer', 0) > 0:
            # Can only have 1 laser active to avoid breaking the game
            if not any(getattr(b, 'is_laser', False) for b in self.game.player_bullets):
                bullet = Bullet(self.game, self, direction=-1)
                # Modify bullet to be a laser
                bullet.image = pygame.Surface((15, self.settings.screen_height))
                bullet.image.fill((255, 50, 50))
                bullet.rect = bullet.image.get_rect()
                bullet.rect.centerx = self.rect.centerx
                bullet.rect.bottom = self.rect.top
                bullet.is_laser = True
                bullet.speed = self.settings.bullet_speed * 3
                bullet.dy = -bullet.speed
                
                self.game.all_sprites.add(bullet)
                self.game.player_bullets.add(bullet)
                return True
            return False
            
        if len(self.game.player_bullets) < self.settings.max_bullets:
            bullet = Bullet(self.game, self, direction=-1)
            self.game.all_sprites.add(bullet)
            self.game.player_bullets.add(bullet)
            return True
        return False