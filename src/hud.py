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
        
        # Draw high score
        high_score = max(self.game.score, getattr(self.settings, 'high_score', 0))
        hs_text = self.font.render(f"High Score: {high_score}", True, (255, 255, 0))
        self.screen.blit(hs_text, (10, 40))
        
        # Draw Level
        level_text = self.font.render(f"Level: {getattr(self.game, 'current_level', 1)}", True, (255, 255, 255))
        self.screen.blit(level_text, (self.settings.screen_width // 2 - level_text.get_width() // 2, 10))
        
        # Draw lives
        if self.game.lives > 0:
            player_img = self.game.player.image
            small_ship = pygame.transform.scale(player_img, (player_img.get_width() // 2, player_img.get_height() // 2))
            
            for i in range(self.game.lives):
                x = self.settings.screen_width - 10 - (i + 1) * (small_ship.get_width() + 10)
                self.screen.blit(small_ship, (x, 10))
                
        # Draw Boss Health Bar if Boss is active
        if hasattr(self.game, 'boss') and self.game.boss is not None and self.game.boss.alive():
            health_ratio = self.game.boss.health / self.game.boss.max_health
            bar_width = 400
            bar_height = 20
            x = (self.settings.screen_width - bar_width) // 2
            y = 40
            pygame.draw.rect(self.screen, (100, 100, 100), (x, y, bar_width, bar_height))
            pygame.draw.rect(self.screen, (255, 0, 0), (x, y, int(bar_width * health_ratio), bar_height))
            pygame.draw.rect(self.screen, (255, 255, 255), (x, y, bar_width, bar_height), 2)
            boss_text = pygame.font.SysFont(None, 24).render("BOSS", True, (255, 255, 255))
            self.screen.blit(boss_text, (x + bar_width // 2 - boss_text.get_width() // 2, y + 2))