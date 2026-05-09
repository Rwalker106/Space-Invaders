# pyrefly: ignore [missing-import]
import pygame
import random

class Starfield:
    def __init__(self, screen_width, screen_height, num_stars=150):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.stars = []
        for _ in range(num_stars):
            speed = random.uniform(0.2, 2.5)
            # Far stars are dim/slow/small, near stars are bright/fast/large
            size = 1 if speed < 1.0 else 2
            
            # Slight color tint
            tint = random.choice([
                (255, 255, 255), # White
                (200, 200, 255), # Blueish
                (255, 200, 200), # Reddish
                (255, 255, 200)  # Yellowish
            ])
            
            # Reduce brightness based on speed
            r = int(tint[0] * (speed / 2.5))
            g = int(tint[1] * (speed / 2.5))
            b = int(tint[2] * (speed / 2.5))
            color = (max(30, r), max(30, g), max(30, b))
            
            self.stars.append({
                'x': random.randint(0, screen_width),
                'y': random.randint(0, screen_height),
                'speed': speed,
                'size': size,
                'color': color
            })
    
    def update(self):
        for star in self.stars:
            star['y'] += star['speed']
            if star['y'] > self.screen_height:
                star['y'] = 0
                star['x'] = random.randint(0, self.screen_width)

    def draw(self, screen):
        for star in self.stars:
            pygame.draw.rect(screen, star['color'], (int(star['x']), int(star['y']), star['size'], star['size']))