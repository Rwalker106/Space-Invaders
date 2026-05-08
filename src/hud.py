from pygame.sprite import Sprite
import pygame


class HUD:
    def __init__(self, game):
        self.game = game
        self.screen = game.screen
        self.settings = game.settings
        self.font = pygame.font.SysFont(None, 36)
        
    def draw(self):
        # Draw score
        score_text = self.font.render(f"Score: {self.game.score}", True, (255, 255, 255))
        self.screen.blit(score_text, (10, 10))
        
        # Draw lives
        lives_text = self.font.render(f"Lives: {self.game.lives}", True, (255, 255, 255))
        self.screen.blit(lives_text, (self.settings.screen_width - lives_text.get_width() - 10, 10))