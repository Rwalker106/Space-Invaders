import pygame
from src.settings import Settings
from src.player import Player
from src.invader import InvaderFleet
from src.barrier import Barrier
from src.starfield import Starfield
from src.hud import HUD
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
            "assets/images/space_bg.png").convert_alpha()
        self.background_image = pygame.transform.scale(self.background_image, (self.screen_width, self.screen_height))
        self.game_over_bg = pygame.image.load("assets/images/game_over_press_enter.png").convert_alpha()
        self.game_over_bg = pygame.transform.scale(self.game_over_bg, (self.screen_width, self.screen_height))
        self.player_bullets_image = pygame.image.load("assets/images/player_bullet1.png").convert_alpha()
        self.invader_bullets_image = pygame.image.load("assets/images/invader_bullet1.png").convert_alpha()
        self.player = Player(self)  
        self.lives = self.settings.player_lives
        self.score = self.settings.starting_score
        self.all_sprites = pygame.sprite.Group()
        self.player_bullets = pygame.sprite.Group()
        self.invader_bullets = pygame.sprite.Group()
        self.invader_fleet = InvaderFleet(self, frames=None) 
        self.all_sprites.add(self.player) # player and bullets. Bullets area added when shot.
        self.cued_to_shoot = False
        self.count_down = 0
        self.barriers = []
        self.hud = HUD(self)
        self.state = "start"
        self.plyr_is_hit = False
        self.player_is_hit_timer = 0
        self.player_is_hit_duration = 2 # seconds
        self.selected_difficulty = "Medium" # default difficulty setting
        self.selected_option = 0
        self.starfield = Starfield(self.screen_width, self.screen_height)
        self.options = {
            "Difficulty": {
                "choices": ["Easy", "Medium", "Hard"], "selected": 1}, 
            "player ship": {"choices": ["Cool Pixel", "Blue Bubble", "Wide Red", "Pink Pill"],  
            "images":["assets/images/Cool Pixel Spaceship.png", 
                  "assets/images/Blue Bubble.png", 
                  "assets/images/wide_red.png", 
                  "assets/images/pink_pill.png"],
            "selected": 0
            },
            "invader ship": 
                {"choices": 
                    ["Theme 1", "Theme 2", "Theme 3"],
                 "images": [ # Theme 1
                        [("assets/images/theme1_invader1_a.png","assets/images/theme1_invader1_b.png"),
                         ("assets/images/theme1_invader2_a.png","assets/images/theme1_invader2_b.png"),
                         ("assets/images/theme1_invader3_a.png","assets/images/theme1_invader3_b.png"),
                         ("assets/images/theme1_invader4_a.png","assets/images/theme1_invader4_b.png")], 
                         # Theme 2
                         [("assets/images/theme2_invader1_a.png", "assets/images/theme2_invader1_b.png"),
                         ("assets/images/theme2_invader2_a.png","assets/images/theme2_invader2_b.png"),
                         ("assets/images/theme2_invader3_a.png","assets/images/theme2_invader3_b.png"),
                         ("assets/images/theme2_invader4_a.png","assets/images/theme2_invader4_b.png")],
                         # Theme 3
                        [("assets/images/theme3_invader1_a.png", "assets/images/theme3_invader1_b.png"),
                        ("assets/images/theme3_invader2_a.png","assets/images/theme3_invader2_b.png"),
                        ("assets/images/theme3_invader3_a.png","assets/images/theme3_invader3_b.png"),
                        ("assets/images/theme3_invader4_a.png","assets/images/theme3_invader4_b.png")
                        ]
                        ],
                    "selected": 0}, 
            "music": {
                "choices": ["game_theme_1.ogg",
                            "game_theme_2.ogg",
                            "game_theme_3.ogg",
                            "game_theme_4.ogg"],
                "selected": 0}, 
            "Volume": {"choices": list(range(0, 101)), "selected": 50}}
        self.player_ship_imgs = [
            pygame.transform.scale(pygame.image.load(path), (50, 40))
            for path in self.options["player ship"]["images"]
        ]
        self.invader_ship_imgs = [
            [ #for each theme 
             ( # for each pair of invader frames
                pygame.transform.scale(pygame.image.load(p[0]).convert_alpha(), (40, 30)),
                pygame.transform.scale(pygame.image.load(p[1]).convert_alpha(), (40, 30)),
            ) for p in theme
             ]
            for theme in self.options["invader ship"]["images"]
        ]
        #audio setup
        pygame.mixer.init()
        self.shoot_sfx = pygame.mixer.Sound("assets/sounds/shoot.wav")
        self.player_hit_sfx = pygame.mixer.Sound("assets/sounds/player_hit.wav")
        self.invader_killed_sfx = pygame.mixer.Sound("assets/sounds/invaderkilled.wav")
        self.invader_shoot_sfx = pygame.mixer.Sound("assets/sounds/invaders_shoot.wav")
        self.current_music = None
        self.music_linger_timer = None  # None=not on music row, >0=counting down, -1=already previewing

    def run(self):
        """Start the main loop for the game."""
        while self.running:
            self._handle_events()
            if self.state == "start":
                self.draw_start_screen()
            elif self.state == "settings":
                self._handle_settings_held_keys()
                self._update_settings()
                self.draw_settings_screen()
            elif self.state == "playing":
                if self.plyr_is_hit:
                    self._draw_hit_effect()
                else:
                    self._update()
                    self._invader_shoot()
                    self._check_collisions()
                    self._draw()
            elif self.state == "game_over":
                self._draw_game_over_screen()
            elif self.state == "win":
                self._draw_win_screen()
            self.clock.tick(self.settings.fps)
                
    def _handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                self._keydown_events(event)
                        
                
    def _keydown_events(self, event):
        if event.key == pygame.K_SPACE and self.state == "playing":
            if self.player.shoot():
                self.shoot_sfx.play()
            
        elif event.key == pygame.K_ESCAPE:
            if self.state == "settings":
                self.state = "start"
            else:
                self.running = False
                
        elif event.key == pygame.K_RETURN:
            if self.state == "win":
                self._start_game()
            elif self.state == "start":
                self._start_game()
            elif self.state == "settings":
                self._apply_settings()
                self.state = "start"
            elif self.state == "game_over":
                self._start_game()
            
        elif event.key == pygame.K_s and self.state == "start":
            self.state = "settings"

            
        elif (event.key == pygame.K_LEFT or event.key == pygame.K_a) and self.state == "settings":
            key = list(self.options.keys())[self.selected_option]
            data = self.options[key]
            data["selected"] = max(0, data["selected"] - 1)
            if key == "music":
                self.current_music = None
                track = data["choices"][data["selected"]]
                self._play_music(track)
                self.music_linger_timer = -1  # already previewing, suppress linger trigger
            if key == "Volume":
                volume = data["choices"][data["selected"]] / 100
                pygame.mixer.music.set_volume(volume)
                self.shoot_sfx.set_volume(volume)
                self.player_hit_sfx.set_volume(volume)
                self.invader_killed_sfx.set_volume(volume)
                self.invader_shoot_sfx.set_volume(volume)

        elif (event.key == pygame.K_RIGHT or event.key == pygame.K_d) and self.state == "settings":
            key = list(self.options.keys())[self.selected_option]
            data = self.options[key]
            data["selected"] = min(len(data["choices"]) - 1, data["selected"] + 1)
            if key == "music":
                self.current_music = None
                track = data["choices"][data["selected"]]
                self._play_music(track)
                self.music_linger_timer = -1  # already previewing, suppress linger trigger
            if key == "Volume":
                volume = data["choices"][data["selected"]] / 100
                pygame.mixer.music.set_volume(volume)
                self.shoot_sfx.set_volume(volume)
                self.player_hit_sfx.set_volume(volume)
                self.invader_killed_sfx.set_volume(volume)
                self.invader_shoot_sfx.set_volume(volume)
            
        elif event.key == pygame.K_UP and self.state == "settings":
            self.selected_option = max(0, self.selected_option - 1)
            self.music_linger_timer = None
        elif event.key == pygame.K_DOWN and self.state == "settings":
            self.selected_option = min(len(self.options) - 1, self.selected_option + 1)
            self.music_linger_timer = None

    def _handle_settings_held_keys(self):
        keys = pygame.key.get_pressed()
        key = list(self.options.keys())[self.selected_option]
        if key == "Volume":
            if keys[pygame.K_LEFT]:
                self.options["Volume"]["selected"] = max(0, self.options["Volume"]["selected"] - 1)
            elif keys[pygame.K_RIGHT]:
                self.options["Volume"]["selected"] = min(len(self.options["Volume"]["choices"]) - 1, self.options["Volume"]["selected"] + 1)
            volume = self.options["Volume"]["choices"][self.options["Volume"]["selected"]] / 100
            pygame.mixer.music.set_volume(volume)
            self.shoot_sfx.set_volume(volume)
            self.player_hit_sfx.set_volume(volume)
            self.invader_killed_sfx.set_volume(volume)
            self.invader_shoot_sfx.set_volume(volume)

    
    def _start_game(self):
        
        # Barriers reset — kill() removes sprites from all groups before rebuilding
        for b in self.barriers:
            b.kill()
        self.barriers = []
        self._create_barriers()
        # Ship selection
        self.all_sprites.remove(self.player) # remove old player sprite before creating new one with selected ship
        selected_idx = self.options["player ship"]["selected"]
        selected_image  = self.player_ship_imgs[selected_idx]
        scaled_image = pygame.transform.scale(selected_image, (50, 40))
        self.player = Player(self, image=scaled_image)
        self.all_sprites.add(self.player)
        
        self.score = self.settings.starting_score
        self.lives = self.settings.player_lives
        invader_selected_idx = self.options["invader ship"]["selected"]
        invader_frames = self.invader_ship_imgs[invader_selected_idx]
        self.invader_fleet = InvaderFleet(self, frames=invader_frames)
        music_selected_idx = self.options["music"]["selected"]
        track = self.options["music"]["choices"][music_selected_idx]
        self._play_music(track)
        self.player_bullets.empty() # clear bullets
        self.invader_bullets.empty()    
        self.state = "playing"

            
    # Collision detection``
    def _check_collisions(self):
        # First check bullets fired from the player intersecting with invaders
        player_hits = pygame.sprite.groupcollide(self.player_bullets, self.invader_fleet.invaders, True, True)
        if player_hits:
            self.invader_killed_sfx.play() # play invader killed sound effect
            for invader in player_hits.values():
                for i in invader:
                    self.score += i.point_value
        
        # Then check bullets fired from the invaders intersecting with the player
        invader_hits = pygame.sprite.spritecollide(self.player, self.invader_bullets, True)
        
        if invader_hits:
            self._player_is_hit()
            self.player_hit_sfx.play() # play player hit sound effect
            if self.lives <= 0:
                self.state = "game_over"
                            
        if len(self.invader_fleet.invaders) == 0:
            self.state = "win"
        if self.invader_fleet._check_bottom():
            self.state = "game_over"            
            
        # Check bullet-barrier collisions — collide_mask respects transparent arch cutout
        for barrier in self.barriers:
            for bullet in pygame.sprite.spritecollide(barrier, self.invader_bullets, True, pygame.sprite.collide_mask):
                barrier.take_hit(bullet.rect.centerx, bullet.rect.centery)

        for barrier in self.barriers:
            for bullet in pygame.sprite.spritecollide(barrier, self.player_bullets, True, pygame.sprite.collide_mask):
                barrier.take_hit(bullet.rect.centerx, bullet.rect.centery)

        # Invaders touching barriers erode them
        for barrier in self.barriers:
            for inv in pygame.sprite.spritecollide(barrier, self.invader_fleet.invaders, False):
                barrier.take_hit(inv.rect.centerx, inv.rect.bottom)
                

    def _invader_shoot(self):
        if len(self.invader_fleet.invaders) > 0 and not self.cued_to_shoot:
            self.count_down = random.randint(0,5) #set counter to random value between 0 and 5 seconds
            self.cued_to_shoot = True
        else:
            self.count_down -= 1 / self.settings.fps #decrease counter based on frame rate
            if self.count_down <= 0:
                self.invader_fleet.shoot()
                self.invader_shoot_sfx.play() # play shoot sound effect
                self.cued_to_shoot = False

                
    def _create_barriers(self):
        num_barriers = self.settings.barrier_count
        gap = self.screen_width // num_barriers
        barrier_pixel_width = self.settings.barrier_width
        y_position = int(self.settings.screen_height * 0.75) # place barriers at 75% of screen height
        for i in range(num_barriers):
            x_position = gap * i + (gap // 2) - (barrier_pixel_width //2) # center barrier in gap based on image width
            barrier = Barrier(self, x_position, y_position)
            self.barriers.append(barrier)
            self.all_sprites.add(barrier) # add barrier to all sprites group for drawing and collision detection
         
         
    def _update_settings(self):
        keys = list(self.options.keys())
        current_key = keys[self.selected_option] if self.selected_option < len(keys) else None
        if current_key == "music":
            if self.music_linger_timer is None:
                self.music_linger_timer = 2.0
            elif self.music_linger_timer > 0:
                self.music_linger_timer -= 1 / self.settings.fps
                if self.music_linger_timer <= 0:
                    self.music_linger_timer = -1
                    track = self.options["music"]["choices"][self.options["music"]["selected"]]
                    self.current_music = None
                    self._play_music(track)
        else:
            self.music_linger_timer = None

    def _apply_settings(self):
        difficulty = self.options["Difficulty"]["choices"][self.options["Difficulty"]["selected"]]
        
        if difficulty == "Easy":
            self.settings.invader_speed    = 0.5
            self.settings.invader_drop_speed = 1
            self.settings.barrier_count    = 5
            self.lives                     = 5
            self.settings.speed_cap        = 1.5
        elif difficulty == "Medium":
            self.settings.invader_speed    = 1
            self.settings.invader_drop_speed = 2
            self.settings.barrier_count    = 4
            self.lives                     = 3
            self.settings.speed_cap        = 3
        elif difficulty == "Hard":
            self.settings.invader_speed    = 2
            self.settings.invader_drop_speed = 3
            self.settings.barrier_count    = 2
            self.lives                     = 1
            self.settings.speed_cap        = 4
            
        # Audio setting
        volume = self.options["Volume"]["choices"][self.options["Volume"]["selected"]] / 100
        pygame.mixer.music.set_volume(volume)
        self.shoot_sfx.set_volume(volume)
        self.player_hit_sfx.set_volume(volume)
        self.invader_killed_sfx.set_volume(volume)
        self.invader_shoot_sfx.set_volume(volume)
            
    def _player_is_hit(self):
        self.lives -= 1
        self.plyr_is_hit = True
        self.player_is_hit_timer = self.player_is_hit_duration
      
    # Audio configurations    
    def _play_music(self, filename, loop=-1):
        if self.current_music != filename:
            self.current_music = filename
            pygame.mixer.music.load(f"assets/sounds/{filename}")
            pygame.mixer.music.play(loop)

        

    # draw and overlay modules    
    def _draw_hit_effect(self):
        self._draw() # draw current game state before overlay
        overlay = pygame.Surface((self.screen_width, self.screen_height))
        overlay.set_alpha(128)  # Semi-transparent
        overlay.fill((255, 0, 0))  # Red color
        self.screen.blit(overlay, (0, 0))
        font = pygame.font.SysFont(None, 72)
        hit_text = font.render("Lost a Life!", True, (0, 0, 0))
        self.screen.blit(hit_text, (self.screen_width//2 - hit_text.get_width()//2, self.screen_height//2 - hit_text.get_height()//2))
        pygame.display.flip()
        self.player_is_hit_timer -= 1 / self.settings.fps
        if self.player_is_hit_timer <= 0:
            self.plyr_is_hit = False
            
    def draw_start_screen(self):
        self._play_music(("spaceinvaders1.ogg"))
        self.screen.fill((0, 0, 0))
        title_font = pygame.font.SysFont(None, 72)
        font = pygame.font.SysFont(None, 36)
        title_text = title_font.render("Space Invaders", True, (255, 255, 255))
        prompt_text = font.render("Press ENTER to Start", True, (255, 255, 255))
        prompt_settings = font.render("Press 'S' for Settings", True, (255, 255, 255))
        self.screen.blit(title_text, (self.screen_width//2 - title_text.get_width()//2, self.screen_height//3))
        self.screen.blit(prompt_text, (self.screen_width//2 - prompt_text.get_width()//2, self.screen_height//2))
        self.screen.blit(prompt_settings, (self.screen_width//2 - prompt_settings.get_width()//2, self.screen_height//2 + 40))
        pygame.display.flip()
        
    def _draw_game_over_screen(self):
        self._play_music("spaceinvaders1.ogg")
        self.screen.fill((0, 0, 0))
        self.screen.blit(self.game_over_bg, (0, 0))
        font_large = pygame.font.SysFont(None, 72)
        font_small = pygame.font.SysFont(None, 36)
        
        score_text = font_large.render(f"Score: {self.score}", True, (255, 255, 255))
        esc_text = font_small.render("Press ESC to quit", True, (255, 255, 255))
        self.screen.blit(score_text, (self.screen_width//2 - score_text.get_width()//2, self.screen_height//2 - score_text.get_height()//2 - 300))
        self.screen.blit(esc_text, (self.screen_width//2 - esc_text.get_width()//2, self.screen_height//2 + 250))
        pygame.display.flip()

        
    def draw_settings_screen(self):
        self.screen.fill((255, 0, 0)) # trying red background for settings screen
        title_font = pygame.font.SysFont(None, 72)
        font = pygame.font.SysFont(None, 36)
        title_text = title_font.render("Settings", True, (255, 255, 255))
        self.screen.blit(title_text, (self.screen_width//2 - title_text.get_width()//2, self.screen_height//5))
        
        for i, option in enumerate(self.options):
            
            current_value = self.options[option]["choices"][self.options[option]["selected"]]
            if "ship" not in option.lower():
                option_text = f"{option}: {current_value}"
                color = (255, 255, 0) if i == self.selected_option else (255, 255, 255)
                option_text = font.render(option_text, True, color)
                self.screen.blit(option_text, (self.screen_width//2 - option_text.get_width()//2, self.screen_height//2 + i*40))
            else:
                color = (255, 255, 0) if i == self.selected_option else (255, 255, 255)
                if option == "player ship":
                    img = self.player_ship_imgs[self.options[option]["selected"]]
                else:
                    img = self.invader_ship_imgs[self.options[option]["selected"]][0]
                label = font.render(f"{option}: {current_value}", True, color)
                x = self.screen_width // 2 - (img.get_width() + 10 + label.get_width()) // 2
                y = self.screen_height // 2 + i * 40
                self.screen.blit(img, (x, y))
                self.screen.blit(label, (x + img.get_width() + 10, y + (img.get_height() - label.get_height()) // 2))
                
            

        
        if self.music_linger_timer is not None and self.music_linger_timer > 0:
            secs = int(self.music_linger_timer) + 1
            hint = font.render(f"Preview in {secs}s...", True, (255, 200, 0))
            self.screen.blit(hint, (self.screen_width//2 - hint.get_width()//2, self.screen_height - 80))

        back_text = font.render("Press ESC to go back", True, (200, 200, 200))
        self.screen.blit(back_text, (self.screen_width//2 - back_text.get_width()//2, 45))

        pygame.display.flip()
        
        
    def _draw_win_screen(self):
        self._play_music("win_music.ogg")
        self.screen.fill((0, 0, 0))
        self.starfield.update()
        self.starfield.draw(self.screen)
        
        font_large = pygame.font.SysFont(None, 72)
        font_small = pygame.font.SysFont(None, 36)  
        
        win_text = font_large.render("You Win!", True, (255, 255, 255))
        score_text = font_small.render(f"Final Score: {self.score}", True, (255, 255, 255))
        enter_text = font_small.render("Press ENTER to play again", True, (255, 255, 255))
        esc_text = font_small.render("Press ESC to quit", True, (255, 255, 255))

        self.screen.blit(win_text, (self.screen_width//2 - win_text.get_width()//2, self.screen_height//3))
        self.screen.blit(score_text, (self.screen_width//2 - score_text.get_width()//2, self.screen_height//2))
        self.screen.blit(enter_text, (self.screen_width//2 - enter_text.get_width()//2, self.screen_height//2 + 60))
        self.screen.blit(esc_text, (self.screen_width//2 - esc_text.get_width()//2, self.screen_height//2 + 100))
        
        pygame.display.flip()    
            
    def _update(self):
        self.player.update()
        self.player_bullets.update()
        self.invader_bullets.update()
        self.invader_fleet.update()
        
    
    def _draw(self):
        self.screen.blit(self.background_image, (0, 0))
        self.all_sprites.draw(self.screen) # player and bullets
        self.invader_fleet.invaders.draw(self.screen) # invaders
        self.hud.draw()
        
        pygame.display.flip()
    















