import pygame
from src import barrier
from src.settings import Settings
from src.player import Player
from src.invader import InvaderFleet
from src.barrier import Barrier
import random


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
        self.player_bullets = pygame.sprite.Group()
        self.invader_bullets = pygame.sprite.Group()
        self.invader_fleet = InvaderFleet(self) 
        self.all_sprites.add(self.player) # player and bullets. Bullets area added when shot.
        self.player_wins = False
        self.cued_to_shoot = False
        self.count_down = 0
        self.barriers = []
        self._create_barriers()

        print (self.all_sprites)

    def run(self):
        """Start the main loop for the game."""
        while self.running:
            self._handle_events()
            self._update()
            self._invader_shoot()
            self._check_collisions()
            self._draw()
            self.clock.tick(self.settings.fps)
                
    def _handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                self._keydown_events(event)
                        
                
    def _keydown_events(self, event):
        if event.key == pygame.K_SPACE:
            self.player.shoot()
        elif event.key == pygame.K_ESCAPE:
            self.running = False
            
    # Collision detection
    def _check_collisions(self):
        # First check bullets fired from the player intersecting with invaders
        player_hits = pygame.sprite.groupcollide(self.player_bullets, self.invader_fleet.invaders, True, True)
        
        # Then check bullets fired from the invaders intersecting with the player
        invader_hits = pygame.sprite.spritecollide(self.player, self.invader_bullets, True)
        
        if invader_hits:
            self.running = False
            print("Game Over! Player was hit.")
            
        if len(self.invader_fleet.invaders) == 0:
            self.invader_fleet = InvaderFleet(self) # new fleet
            self.player_wins = True
            print("Player wins!")
        if self.invader_fleet._check_bottom():
            self.running = False
            print("Game Over! Invaders reached the bottom.")
            
            
        # Check bullet-barrier collisions
        # Invader bullets hitting barriers degrades them with 3 hits before destroyed. 
        for barrier in self.barriers:
            invader_hits = pygame.sprite.groupcollide(barrier.blocks, self.invader_bullets, False, True)
            for block in invader_hits:
                block.take_hit()
                
        for barrier in self.barriers:
            player_hits = pygame.sprite.groupcollide(barrier.blocks, self.player_bullets, True, True)

        # Invaders hitting barriers destroys the block immediately
        for barrier in self.barriers:
            invader_hits_barrier = pygame.sprite.groupcollide(barrier.blocks, self.invader_fleet.invaders, True, False)

    def _invader_shoot(self):
        if len(self.invader_fleet.invaders) > 0 and not self.cued_to_shoot:
            self.count_down = random.randint(0,5) #set counter to random value between 0 and 5 seconds
            self.cued_to_shoot = True
        else:
            self.count_down -= 1 / self.settings.fps #decrease counter based on frame rate
            if self.count_down <= 0:
                self.invader_fleet.shoot()
                self.cued_to_shoot = False
                
    def _create_barriers(self):
        num_barriers = self.settings.barrier_count
        gap = self.screen_width // num_barriers
        barrier_pixel_width = len(self.settings.barrier_shape[0]) * self.settings.barrier_width

        y_position = int(self.settings.screen_height * 0.75) # place barriers at 75% of screen height
        for i in range(num_barriers):
            x_position = gap * i + (gap // 2) - (barrier_pixel_width //2) # center barrier based on width of 9 blocks
            barrier = Barrier(self, x_position, y_position)
            self.barriers.append(barrier)
            self.all_sprites.add(barrier.blocks) # add all blocks to sprite group for drawing and collision detection
            
            
    def _update(self):
        self.player.update()
        self.player_bullets.update()
        self.invader_bullets.update()
        self.invader_fleet.update()
        
    
    def _draw(self):
        self.screen.blit(self.background_image, (0, 0))
        self.all_sprites.draw(self.screen) # player and bullets
        self.invader_fleet.invaders.draw(self.screen) # invaders
        
        pygame.display.flip()
    















