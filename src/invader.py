import random
from pygame.sprite import Sprite
import pygame
from src.bullet import Bullet


class Invader(Sprite):
    def __init__(self, game, row, col):
        super().__init__()
        self.game = game
        self.screen = game.screen
        self.settings = game.settings
        self.image = pygame.Surface((40, 30))
        self.image.fill((0, 255, 255)) 
        self.rect = self.image.get_rect()
        self.rect.x = 40 + col * (self.rect.width + 10)
        self.rect.y = 30 + row * (self.rect.height + 10)
        
    
class InvaderFleet:
    def __init__(self, game):
        self.game = game
        self.invaders = pygame.sprite.Group()
        self.direction = self.game.settings.fleet_direction
        self.fleet_speed = self.game.settings.invader_speed
        self.fleet_drop_speed = self.game.settings.invader_drop_speed   
        self._create_fleet()
        
    def _create_fleet(self):
        rows = self.game.settings.fleet_rows
        cols = self.game.settings.fleet_cols
        for row in range(rows):
            for col in range(cols):
                invader = Invader(self.game, row, col)
                self.invaders.add(invader)
                
    def update(self):
        # check edges before moving
        if self._check_edges():
            self.direction *= -1
            for invader in self.invaders:
                invader.rect.y += self.fleet_drop_speed
        for invader in self.invaders:
            invader.rect.x += self.direction * self.fleet_speed
        remaining_invaders = len(self.invaders)
        total = self.game.settings.fleet_rows * self.game.settings.fleet_cols
        if remaining_invaders > 0:
            self.fleet_speed = self.game.settings.invader_speed * (total / remaining_invaders)
            
    def _check_edges(self):
        for invader in self.invaders:
            if invader.rect.right >= self.game.settings.screen_width or invader.rect.left <= 0:
                return True
        return False
    
    def _check_bottom(self):
        for invader in self.invaders:
            if invader.rect.bottom >= self.game.settings.screen_height:

                return True

        return False
    
    def shoot(self):
        shooter = random.choice(self.invaders.sprites())
        bullet = Bullet(self.game, shooter, direction=1)
        self.game.all_sprites.add(bullet)
        self.game.invader_bullets.add(bullet)