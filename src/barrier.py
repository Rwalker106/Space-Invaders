from pygame.sprite import Sprite
import pygame



        


class BarrierBlock(Sprite):
    def __init__(self, game, x, y):
        super().__init__()
        self.game = game
        self.settings = game.settings
        self.barrier_health = self.settings.barrier_health
        self.image = pygame.Surface((self.settings.barrier_width, self.settings.barrier_height))
        self.image.fill(self.settings.barrier_color) # Green barrier blocks
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        
        
    def take_hit(self):
        self.barrier_health -= 1
        if self.barrier_health == 2:
            self.image.fill((255, 165, 0)) # Change to orange when damaged
        elif self.barrier_health == 1:
            self.image.fill((255, 0, 0)) # Change to red when heavily damaged
        elif self.barrier_health <= 0: 
            self.kill()
            
        
class Barrier:
    def __init__(self, game, x, y):
        self.game = game
        self.blocks = pygame.sprite.Group()
        self.create_barrier(x, y)

            
    def create_barrier(self, x_start, y_start):
        for row_index, row in enumerate(self.game.settings.barrier_shape):
            for col_index, cell in enumerate(row):
                if cell == "X":
                    block_x = x_start + col_index * self.game.settings.barrier_width
                    block_y = y_start + row_index * self.game.settings.barrier_height
                    block = BarrierBlock(self.game, block_x, block_y)
                    self.blocks.add(block)