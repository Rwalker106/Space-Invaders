import pygame
from src.settings import Settings
from src.player import Player

class SI_Game:
    """Overall class to manage the game"""
    def __init__(self):
        """Initialize the game and create game resources."""
        pygame.init()
        self.settings = Settings()
        self.screen_width = self.settings.screen_width
        self.screen_height = self.settings.screen_height
        self.screen = pygame.display.set_mode((self.screen_width, self.screen_height))
        pygame.display.set_caption(self.settings.title)
        self.clock = pygame.time.Clock()
        self.running = True
        # Background Image
        self.background_image = pygame.image.load(
            "assets/images/space_bg.jpg")
        self.background_image = pygame.transform.scale(self.background_image, (self.screen_width, self.screen_height))
        self.player = Player(self)  
        self.all_sprites = pygame.sprite.Group()
        self.all_sprites.add(self.player)


    def run(self):
        """Start the main loop for the game."""
        while self.running:
            self._handle_events()
            self._update_screen()
            self._draw()
            self.clock.tick(self.settings.fps)
                
    def _handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False    
    
    def _update_screen(self):
        self.all_sprites.update()
    
    def _draw(self):
        self.screen.blit(self.background_image, (0, 0))
        self.all_sprites.draw(self.screen)
        pygame.display.flip()
    















