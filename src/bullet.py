from pygame.sprite import Sprite
import pygame


class Bullet(Sprite):
    def __init__(self, game, owner, direction=-1):
        super().__init__()
        self.game = game
        self.screen = game.screen
        self.settings = game.settings
        self.image = pygame.Surface((self.settings.bullet_width, self.settings.bullet_height))
        self.image.fill(self.settings.bullet_color)
        self.rect = self.image.get_rect()
        self.rect.centerx = owner.rect.centerx
        if direction == -1:  # player bullet
            self.rect.bottom = owner.rect.top
        else:  # invader bullet
            self.rect.top = owner.rect.bottom

        self.speed = self.settings.bullet_speed
        self.direction = direction  # -1 for up, 1 for down (invader bullets)
        
    def update(self):
        self.rect.y += self.direction * self.speed
        if self.rect.bottom < 0 or self.rect.top > self.settings.screen_height:
            self.kill()
            
