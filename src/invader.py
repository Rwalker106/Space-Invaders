import random
from pygame.sprite import Sprite
import pygame
from src.bullet import Bullet
import math


class Invader(Sprite):
    def __init__(self, game, row, col, frames: tuple, point_value=None):
        super().__init__()
        self.game = game
        self.screen = game.screen
        self.settings = game.settings
        self.frames = frames
        self.point_value = point_value    
        self.current_frame = 0
        self.image = self.frames[self.current_frame]
        self.rect = self.image.get_rect()
        self.rect.x = 40 + col * (self.rect.width + 10)
        self.rect.y = 30 + row * (self.rect.height + 10)
        
        
    def animate(self):
        self.current_frame = 1 - self.current_frame
        self.image = self.frames[self.current_frame]
        
    
class InvaderFleet:
    def __init__(self, game, frames: list | None = None) -> None:
        self.game = game
        self.invaders = pygame.sprite.Group()
        self.direction = self.game.settings.fleet_direction
        self.fleet_speed = self.game.settings.invader_speed
        self.fleet_drop_speed = self.game.settings.invader_drop_speed
        self.animation_interval = 0.5  # Randomize animation speed for visual interest
        self.animation_timer = self.animation_interval  # Randomize animation speed for visual interest
        self.frames = frames
        self._create_fleet()
        
    def _create_fleet(self):
        if self.frames is None:
            return
        rows = self.game.settings.fleet_rows
        cols = self.game.settings.fleet_cols
        row_to_type = {0: 3, 1: 2, 2: 1, 3: 1, 4: 0}
        point_index = {0: 10, 1: 20, 2: 30, 3: 40}
        for row in range(rows):
            for col in range(cols):
                frame_idx = row_to_type.get(row, 0)
                invader = Invader(self.game, row, col, frames=self.frames[frame_idx], point_value=point_index.get(frame_idx))
                self.invaders.add(invader)
                
    def update(self):
        for invader in self.invaders:
            invader.rect.x += self.direction * self.fleet_speed
        self.animation_timer -= 1 / self.game.settings.fps
        if self.animation_timer <= 0:
            self.animation_timer = self.animation_interval
            for invader in self.invaders:
                invader.animate()
        if self._check_edges():
            self.direction *= -1
            sprites = self.invaders.sprites()
            max_right = max(s.rect.right for s in sprites)
            min_left = min(s.rect.left for s in sprites)
            if max_right > self.game.settings.screen_width:
                correction = max_right - self.game.settings.screen_width
                for invader in self.invaders:
                    invader.rect.x -= correction
            elif min_left < 0:
                for invader in self.invaders:
                    invader.rect.x -= min_left
            for invader in self.invaders:
                invader.rect.y += self.fleet_drop_speed
        remaining_invaders = len(self.invaders)
        total = self.game.settings.fleet_rows * self.game.settings.fleet_cols
        if remaining_invaders > 0:
            speed_increase = min(math.sqrt(total / remaining_invaders), self.game.settings.speed_cap)
            self.fleet_speed = self.game.settings.invader_speed + speed_increase
            
                    
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
        
