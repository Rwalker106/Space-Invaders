import pygame
import random

class Starfield:
    def __init__(self, screen_width, screen_height, num_stars=100):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.stars = [
            [random.randint(0, screen_width),
             random.randint(0, screen_height),
             random.uniform(0.5, 3.0)]  # speed
            for _ in range(num_stars)
        ]
    
    def update(self):
        for star in self.stars:
            star[1] += star[2]  # move down by speed
            if star[1] > self.screen_height:
                star[1] = 0
                star[0] = random.randint(0, self.screen_width)

    def draw(self, screen):
        for star in self.stars:
            brightness = int(star[2] * 80)  # faster = brighter
            pygame.draw.circle(screen, (brightness, brightness, brightness),(int(star[0]), int(star[1])), 1)