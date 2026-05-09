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
        if getattr(self, 'hit', False):
            self.explode_timer -= 1 / self.game.settings.fps
            if self.explode_timer <= 0:
                self.game.ufo_hit_sfx.play() # explosion.wav
                self.game.particle_system.create_explosion(self.rect.centerx, self.rect.top + self.settings.ufo_height//2, (255, 255, 255), 15)
                self.kill()
            return
            
        # Ufo will make two passes across the screen before disappearing
        self.rect.x += self.direction * self.settings.ufo_speed
        self.time_alive += 1 / self.game.settings.fps
        if self.rect.right < 0 or self.rect.left > self.settings.screen_width:
            self.kill()  # Remove UFO if it goes off screen after two passes
            
    def take_hit(self):
        if getattr(self, 'hit', False): return
        self.hit = True
        self.explode_timer = 1.0 # Wait 1 second before exploding
        self.showing_light = True
        self.direction = 0 # Stop moving
        
        # Combine UFO image and light image
        new_height = self.settings.ufo_height + self.settings.ufo_light_height
        new_image = pygame.Surface((self.settings.ufo_width, new_height), pygame.SRCALPHA)
        new_image.blit(self.image, (0, 0))
        # Draw light extending downwards
        new_image.blit(self.light_image, (self.settings.ufo_width//2 - self.settings.ufo_light_width//2, self.settings.ufo_height))
        self.image = new_image
        
        # Keep the top at the same position, so the light extends downwards
        old_centerx = self.rect.centerx
        old_top = self.rect.top
        self.rect = self.image.get_rect()
        self.rect.centerx = old_centerx
        self.rect.top = old_top
            
    def get_points(self):
        if self.time_alive < 2: return 200
        elif self.time_alive < 4: return 150
        elif self.time_alive < 6: return 100
        else: return 50
            
    def animate(self):
        pass