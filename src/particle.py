import pygame
import random
import math

class Particle(pygame.sprite.Sprite):
    def __init__(self, x, y, color, game):
        super().__init__()
        self.game = game
        self.settings = game.settings
        
        # Randomize particle size, speed, and angle
        size = random.randint(2, 6)
        self.image = pygame.Surface((size, size))
        self.image.fill(color)
        self.rect = self.image.get_rect(center=(x, y))
        
        angle = random.uniform(0, 2 * math.pi)
        speed = random.uniform(50, 200) # pixels per second
        self.vx = math.cos(angle) * speed
        self.vy = math.sin(angle) * speed
        
        self.lifetime = random.uniform(0.2, 0.6) # seconds
        self.timer = self.lifetime
        self.original_color = color
        
        # Sub-pixel precise tracking
        self.x = float(self.rect.x)
        self.y = float(self.rect.y)
        
    def update(self):
        dt = 1 / self.settings.fps
        self.x += self.vx * dt
        self.y += self.vy * dt
        self.rect.x = int(self.x)
        self.rect.y = int(self.y)
        
        self.timer -= dt
        if self.timer <= 0:
            self.kill()
        else:
            # Fade out
            alpha = int((self.timer / self.lifetime) * 255)
            self.image.set_alpha(alpha)

class ParticleSystem:
    def __init__(self, game):
        self.game = game
        self.particles = pygame.sprite.Group()
        
    def create_explosion(self, x, y, color, count=15):
        for _ in range(count):
            p = Particle(x, y, color, self.game)
            self.particles.add(p)
            self.game.all_sprites.add(p)
            
    def update(self):
        self.particles.update()
