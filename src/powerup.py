import pygame
import random

class PowerUp(pygame.sprite.Sprite):
    def __init__(self, game, center_x, center_y):
        super().__init__()
        self.game = game
        self.settings = game.settings
        
        self.type = random.choice(["multi_shot", "life", "shield", "time_freeze", "laser"])
        
        # Create an image surface with per-pixel alpha
        radius = 15
        self.image = pygame.Surface((radius*2, radius*2), pygame.SRCALPHA)
        
        if self.type == "multi_shot":
            color = (255, 165, 0) # Orange
            letter = "M"
        elif self.type == "life":
            color = (0, 255, 0) # Green
            letter = "1UP"
        elif self.type == "shield":
            color = (0, 191, 255) # DeepSkyBlue
            letter = "S"
        elif self.type == "time_freeze":
            color = (138, 43, 226) # BlueViolet
            letter = "T"
        else: # laser
            color = (255, 0, 0) # Red
            letter = "L"
            
        # Draw glowing orb
        pygame.draw.circle(self.image, (*color, 100), (radius, radius), radius) # outer glow
        pygame.draw.circle(self.image, color, (radius, radius), radius - 4) # inner core
        
        # Add letter
        font = pygame.font.SysFont(None, 20 if letter == "1UP" else 24)
        text = font.render(letter, True, (255, 255, 255))
        text_rect = text.get_rect(center=(radius, radius))
        self.image.blit(text, text_rect)
        
        self.rect = self.image.get_rect()
        self.rect.centerx = center_x
        self.rect.centery = center_y
        
    def update(self):
        # Move powerup down the screen
        self.rect.y += self.settings.powerup_drop_speed
        
        # Remove if it falls off bottom
        if self.rect.top > self.settings.screen_height:
            self.kill()
