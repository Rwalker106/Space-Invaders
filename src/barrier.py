from pygame.sprite import Sprite
import pygame        


class Barrier(Sprite):
    def __init__(self, game, x, y):
        super().__init__()
        self.game = game
        self.settings = game.settings
        self.image = pygame.image.load("assets/images/barrier1.png").convert_alpha()
        self.image = pygame.transform.scale(self.image, (self.settings.barrier_width, self.settings.barrier_height))
        self.mask = pygame.mask.from_surface(self.image)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        
        
    def take_hit(self, damage_x, damage_y):

        # Convert damage coordinates to local barrier coordinates
        local_x = damage_x - self.rect.x
        local_y = damage_y - self.rect.y
        
        # Carve a transparent hole using BLEND_RGBA_MIN.
        # Fill erase surface fully opaque so min() leaves untouched pixels unchanged.
        # The transparent circle (alpha=0) forces those pixels to 0 in the destination.
        erase = pygame.Surface(self.image.get_size(), pygame.SRCALPHA)
        erase.fill((255, 255, 255, 255))
        pygame.draw.circle(erase, (0, 0, 0, 0), (local_x, local_y), 10)
        self.image.blit(erase, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
        
        # Regenerate the mask after modifying the image
        self.mask = pygame.mask.from_surface(self.image)
        
        # Kill if no visible pixels remain
        if self.mask.count() == 0:
            self.kill()