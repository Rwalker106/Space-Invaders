from pygame.sprite import Sprite
import pygame


class Player(Sprite):
    def __init__(self, game):
        
        super().__init__()
        self.game = game
        self.screen = game.screen
        self.settings = game.settings
        # self.image = pygame.image.load("assests/images/player.png")
        self.image = pygame.Surface((50, 40))
        self.image.fill((0, 255, 0)) 
        self.rect = self.image.get_rect()
        self.rect.centerx = self.screen.get_rect().centerx
        self.rect.bottom = self.screen.get_rect().bottom - 10
        
    def update(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] and self.rect.left > 0:
            self.rect.x -= self.settings.player_speed
        if keys[pygame.K_RIGHT] and self.rect.right < self.settings.screen_width:
            self.rect.x += self.settings.player_speed