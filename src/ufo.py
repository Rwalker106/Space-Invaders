import random
import pygame
from pygame.sprite import Sprite


class UFO(Sprite):
    def __init__(self, game, image=None, light_image=None):
        super().__init__()
        self.game = game
        self.screen = game.screen
        self.settings = game.settings
        self.image = pygame.transform.scale(image, (self.settings.ufo_width, self.settings.ufo_height)) if image else pygame.Surface((self.settings.ufo_width, self.settings.ufo_height))
        self.light_image = pygame.transform.scale(light_image, (self.settings.ufo_light_width, self.settings.ufo_light_height)) if light_image else pygame.Surface((self.settings.ufo_light_width, self.settings.ufo_light_height))
        self.rect = self.image.get_rect()
        self.direction = random.choice([-1, 1])  # Randomly choose to start from left or right
        if self.direction == 1:
            self.rect.x = -self.rect.width  # Start just off the left edge
        else:
            self.rect.x = self.settings.screen_width  # Start just off the right edge
        self.rect.y = 50  # Fixed height for UFOs
        self.has_powerup = random.random() < 0.5  # 50% chance to have a power-up
        self.time_alive = 0
        self.showing_light = False
        self.light_timer = 0

        
    def update(self):
        # Ufo will make two passes across the screen before disappearing
        self.rect.x += self.direction * self.settings.ufo_speed
        self.time_alive += 1 / self.game.settings.fps
        if self.rect.right < 0 or self.rect.left > self.settings.screen_width:
            self.kill()  # Remove UFO if it goes off screen after two passes
            
    def get_points(self):
        if self.time_alive < 2: return 200
        elif self.time_alive < 4: return 150
        elif self.time_alive < 6: return 100
        else: return 50
            
    def animate(self):
        pass