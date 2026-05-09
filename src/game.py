# pyrefly: ignore [missing-import]
import pygame
from src.settings import Settings
from src.player import Player
from src.invader import InvaderFleet
from src.barrier import Barrier
from src.starfield import Starfield
from src.ufo import UFO
from src.hud import HUD
from src.powerup import PowerUp
from src.boss import Boss
from src.particle import ParticleSystem
import random




class SI_Game:
    """Overall class to manage the game"""
    def __init__(self):
        # --- pygame core ---
        pygame.init()
        self.settings = Settings()
        self.screen_width = self.settings.screen_width
        self.screen_height = self.settings.screen_height
        self.screen = pygame.display.set_mode((self.screen_width, self.screen_height))
        pygame.display.set_caption(self.settings.title)
        self.clock = pygame.time.Clock()
        self.running = True

        # --- images (load once at startup) ---
        # Backgrounds are now generated as dynamic Starfield
        self.player_bullets_image = pygame.image.load("assets/images/player_bullet1.png").convert_alpha()
        self.invader_bullets_image = pygame.image.load("assets/images/invader_bullet1.png").convert_alpha()
        
        self.ufo_image = pygame.image.load("assets/images/ufo.png").convert_alpha()
        self.ufo_light_image = pygame.image.load("assets/images/ufo_light.png").convert_alpha()


        # --- audio ---
        pygame.mixer.init()
        self.shoot_sfx = pygame.mixer.Sound("assets/sounds/shoot.wav")
        self.player_hit_sfx = pygame.mixer.Sound("assets/sounds/player_hit.wav")
        self.invader_killed_sfx = pygame.mixer.Sound("assets/sounds/invaderkilled.wav")
        self.invader_shoot_sfx = pygame.mixer.Sound("assets/sounds/invaders_shoot.wav")
        self.current_music = None
        self.music_linger_timer = None
        
        # UFO audio effects
        self.ufo_channel = pygame.mixer.Channel(5)  # Dedicated channel for UFO sounds
        self.ufo_sfx = pygame.mixer.Sound("assets/sounds/ufo-beep-1084.wav")
        self.ufo_hit_sfx = pygame.mixer.Sound("assets/sounds/explosion.wav")
        self.ufo_powerup_sfx = pygame.mixer.Sound("assets/sounds/power-up-drop.wav")

        # --- game state ---
        self.state = "start"
        self.score = self.settings.starting_score
        self.lives = self.settings.player_lives
        

        self.plyr_is_hit = False
        self.player_is_hit_timer = 0
        self.player_is_hit_duration = 2
        self.cued_to_shoot = False
        self.count_down = 0


        # --- sprite groups ---
        self.all_sprites = pygame.sprite.Group()
        self.player_bullets = pygame.sprite.Group()
        self.invader_bullets = pygame.sprite.Group()
        self.powerups = pygame.sprite.Group()
        self.multi_shot_timer = 0
        self.current_level = 1
        self.boss = None
        self.level_transition_timer = 0
        self.shake_timer = 0
        self.time_freeze_timer = 0
        self.laser_timer = 0
        self.particle_system = ParticleSystem(self)
        self.game_surface = pygame.Surface((self.screen_width, self.screen_height))

        # --- game objects ---
        self.player = Player(self)
        self.all_sprites.add(self.player)
        self.invader_fleet = InvaderFleet(self, frames=None)
        self.barriers = []
        self.hud = HUD(self)
        self.starfield = Starfield(self.screen_width, self.screen_height)

        # --- settings menu ---
        self.selected_difficulty = "Medium"
        self.selected_option = 0
        self.options = {
            "Difficulty": {
                "choices": ["Easy", "Medium", "Hard"], "selected": 1},
            "player ship": {
                "choices": ["Cool Pixel", "Blue Bubble", "Wide Red", "Pink Pill"],
                "images": ["assets/images/Cool Pixel Spaceship.png",
                           "assets/images/Blue Bubble.png",
                           "assets/images/wide_red.png",
                           "assets/images/pink_pill.png"],
                "selected": 0},
            "invader ship": {
                "choices": ["Theme 1", "Theme 2", "Theme 3"],
                "images": [
                    [("assets/images/theme1_invader1_a.png", "assets/images/theme1_invader1_b.png"),
                     ("assets/images/theme1_invader2_a.png", "assets/images/theme1_invader2_b.png"),
                     ("assets/images/theme1_invader3_a.png", "assets/images/theme1_invader3_b.png"),
                     ("assets/images/theme1_invader4_a.png", "assets/images/theme1_invader4_b.png")],
                    [("assets/images/theme2_invader1_a.png", "assets/images/theme2_invader1_b.png"),
                     ("assets/images/theme2_invader2_a.png", "assets/images/theme2_invader2_b.png"),
                     ("assets/images/theme2_invader3_a.png", "assets/images/theme2_invader3_b.png"),
                     ("assets/images/theme2_invader4_a.png", "assets/images/theme2_invader4_b.png")],
                    [("assets/images/theme3_invader1_a.png", "assets/images/theme3_invader1_b.png"),
                     ("assets/images/theme3_invader2_a.png", "assets/images/theme3_invader2_b.png"),
                     ("assets/images/theme3_invader3_a.png", "assets/images/theme3_invader3_b.png"),
                     ("assets/images/theme3_invader4_a.png", "assets/images/theme3_invader4_b.png")]],
                "selected": 0},
            "music": {
                "choices": ["game_theme_1.ogg", "game_theme_2.ogg",
                            "game_theme_3.ogg", "game_theme_4.ogg"],
                "selected": 0},
            "Music Vol": {"choices": list(range(0, 101, 5)), "selected": 10},
            "SFX Vol": {"choices": list(range(0, 101, 5)), "selected": 10}}
            
        self._load_user_settings()
        
        self.player_ship_imgs = [
            pygame.transform.scale(pygame.image.load(path), (50, 40))
            for path in self.options["player ship"]["images"]
        ]
        self.invader_ship_imgs = [
            [(pygame.transform.scale(pygame.image.load(p[0]).convert_alpha(), (40, 30)),
              pygame.transform.scale(pygame.image.load(p[1]).convert_alpha(), (40, 30)))
             for p in theme]
            for theme in self.options["invader ship"]["images"]
        ]
       
        
        # Ufo settings
        self.ufo = None # No UFO active at start.
        self.ufo_timer = 0
        self.ufo_interval = random.randint(20, 40)  # Random interval between UFO appearances
        
        # Apply initial loaded settings
        self._apply_settings()
        
#######################CODE STARTS HERE#########################################

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
            elif self.state == "level_transition":
                self._draw_level_transition()
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
                self._apply_settings()
                self._save_user_settings()
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
                self._save_user_settings()
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
            if key == "Music Vol":
                volume = data["choices"][data["selected"]] / 100
                pygame.mixer.music.set_volume(volume)
            if key == "SFX Vol":
                volume = data["choices"][data["selected"]] / 100
                self.shoot_sfx.set_volume(volume)
                self.player_hit_sfx.set_volume(volume)
                self.invader_killed_sfx.set_volume(volume)
                self.invader_shoot_sfx.set_volume(volume)
                self.ufo_sfx.set_volume(volume)
                self.ufo_hit_sfx.set_volume(volume)
                self.ufo_powerup_sfx.set_volume(volume)

        elif (event.key == pygame.K_RIGHT or event.key == pygame.K_d) and self.state == "settings":
            key = list(self.options.keys())[self.selected_option]
            data = self.options[key]
            data["selected"] = min(len(data["choices"]) - 1, data["selected"] + 1)
            if key == "music":
                self.current_music = None
                track = data["choices"][data["selected"]]
                self._play_music(track)
                self.music_linger_timer = -1  # already previewing, suppress linger trigger
            if key == "Music Vol":
                volume = data["choices"][data["selected"]] / 100
                pygame.mixer.music.set_volume(volume)
            if key == "SFX Vol":
                volume = data["choices"][data["selected"]] / 100
                self.shoot_sfx.set_volume(volume)
                self.player_hit_sfx.set_volume(volume)
                self.invader_killed_sfx.set_volume(volume)
                self.invader_shoot_sfx.set_volume(volume)
                self.ufo_sfx.set_volume(volume)
                self.ufo_hit_sfx.set_volume(volume)
                self.ufo_powerup_sfx.set_volume(volume)
            
        elif event.key == pygame.K_UP and self.state == "settings":
            self.selected_option = max(0, self.selected_option - 1)
            self.music_linger_timer = None
        elif event.key == pygame.K_DOWN and self.state == "settings":
            self.selected_option = min(len(self.options) - 1, self.selected_option + 1)
            self.music_linger_timer = None

    def _handle_settings_held_keys(self):
        keys = pygame.key.get_pressed()
        key = list(self.options.keys())[self.selected_option]
        if key == "Music Vol":
            if keys[pygame.K_LEFT]:
                self.options["Music Vol"]["selected"] = max(0, self.options["Music Vol"]["selected"] - 1)
            elif keys[pygame.K_RIGHT]:
                self.options["Music Vol"]["selected"] = min(len(self.options["Music Vol"]["choices"]) - 1, self.options["Music Vol"]["selected"] + 1)
            volume = self.options["Music Vol"]["choices"][self.options["Music Vol"]["selected"]] / 100
            pygame.mixer.music.set_volume(volume)
        elif key == "SFX Vol":
            if keys[pygame.K_LEFT]:
                self.options["SFX Vol"]["selected"] = max(0, self.options["SFX Vol"]["selected"] - 1)
            elif keys[pygame.K_RIGHT]:
                self.options["SFX Vol"]["selected"] = min(len(self.options["SFX Vol"]["choices"]) - 1, self.options["SFX Vol"]["selected"] + 1)
            volume = self.options["SFX Vol"]["choices"][self.options["SFX Vol"]["selected"]] / 100
            self.shoot_sfx.set_volume(volume)
            self.player_hit_sfx.set_volume(volume)
            self.invader_killed_sfx.set_volume(volume)
            self.invader_shoot_sfx.set_volume(volume)
            self.ufo_sfx.set_volume(volume)
            self.ufo_hit_sfx.set_volume(volume)
            self.ufo_powerup_sfx.set_volume(volume)

    
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
        self.player.shielded = False
        
        self._apply_settings()
        self.settings.fleet_rows = 5 # Reset rows
        
        self.current_level = 1
        self._start_next_level(initial=True)
        
        music_selected_idx = self.options["music"]["selected"]
        track = self.options["music"]["choices"][music_selected_idx]
        self._play_music(track)
        if self.ufo is not None:
            self.ufo.kill()
            self.ufo = None
            self.ufo_channel.stop()
        self.ufo_timer = 0
        self.cued_to_shoot = False
        self.count_down = 0

    def _start_next_level(self, initial=False):
        if not initial:
            self.current_level += 1
            
        if self.current_level > self.settings.max_levels:
            self.state = "win"
            return
            
        # Clean up old sprites
        for b in list(self.player_bullets) + list(self.invader_bullets) + list(self.powerups):
            b.kill()
        self.player_bullets.empty()
        self.invader_bullets.empty()
        self.powerups.empty()
        if self.boss:
            self.boss.kill()
            self.boss = None
            
        # Reset powerup states
        self.settings.max_bullets = 1
        self.multi_shot_timer = 0
        self.time_freeze_timer = 0
        self.laser_timer = 0
        self.player.shielded = False
        
        # Difficulty scaling
        if not initial:
            self.settings.invader_speed += 0.15
            if self.current_level % 3 == 0 and self.settings.fleet_rows < 8:
                self.settings.fleet_rows += 1
                
        if self.current_level % 5 == 0:
            # Boss level
            self.invader_fleet.invaders.empty()
            self.boss = Boss(self, self.current_level)
            self.all_sprites.add(self.boss)
        else:
            # Normal wave
            invader_selected_idx = self.options["invader ship"]["selected"]
            invader_frames = self.invader_ship_imgs[invader_selected_idx]
            self.invader_fleet = InvaderFleet(self, frames=invader_frames)
            
        self.level_transition_timer = 2.0
        self.state = "level_transition"

            
    # Collision detection``
    def _check_collisions(self):
        # First check bullets fired from the player intersecting with invaders
        player_hits = pygame.sprite.groupcollide(self.player_bullets, self.invader_fleet.invaders, False, False)
        if player_hits:
            for bullet, invaders in player_hits.items():
                if not getattr(bullet, 'is_laser', False):
                    bullet.kill()
                for i in invaders:
                    i.health -= 1
                    if i.health <= 0:
                        self.invader_killed_sfx.play() # play invader killed sound effect
                        self.particle_system.create_explosion(i.rect.centerx, i.rect.centery, (255, 200, 50), 10)
                        self.score += i.point_value
                        if random.random() < 0.05:
                            powerup = PowerUp(self, i.rect.centerx, i.rect.centery)
                            self.powerups.add(powerup)
                            self.all_sprites.add(powerup)
                        i.kill()
                    else:
                        self.ufo_hit_sfx.play() # Play hit sound for armored
                        self.particle_system.create_explosion(i.rect.centerx, i.rect.centery, (200, 200, 200), 5)
        
        # Then check bullets fired from the invaders intersecting with the player
        invader_hits = pygame.sprite.spritecollide(self.player, self.invader_bullets, True)
        
        if invader_hits:
            if self.player.shielded:
                self.player.shielded = False
                self.player_hit_sfx.play()
            else:
                self._player_is_hit()
                self.shake_timer = 0.5
                self.particle_system.create_explosion(self.player.rect.centerx, self.player.rect.centery, (255, 50, 50), 20)
                self.player_hit_sfx.play() # play player hit sound effect
                if self.lives <= 0:
                    self.settings.save_high_score(self.score)
                    self.state = "game_over"
                            
        if self.boss and self.boss.alive():
            boss_hits = pygame.sprite.spritecollide(self.boss, self.player_bullets, False)
            if boss_hits:
                for bullet in boss_hits:
                    if not getattr(bullet, 'is_laser', False):
                        bullet.kill()
                self.boss.take_damage()
                self.particle_system.create_explosion(self.boss.rect.centerx, self.boss.rect.centery, (200, 50, 255), 5)
                self.score += 50
                if self.boss.health <= 0:
                    self.shake_timer = 1.0
                    self.particle_system.create_explosion(self.boss.rect.centerx, self.boss.rect.centery, (255, 100, 100), 50)
                            
        boss_active = self.boss and self.boss.alive()
        if len(self.invader_fleet.invaders) == 0 and not boss_active:
            if self.current_level >= self.settings.max_levels:
                self.settings.save_high_score(self.score)
            self._start_next_level()
            
        if self.invader_fleet._check_bottom():
            self.settings.save_high_score(self.score)
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
        
        # Check player hits UFO
        if self.ufo and not getattr(self.ufo, 'hit', False):
            ufo_hits = pygame.sprite.spritecollide(self.ufo, self.player_bullets, True)
            if ufo_hits:
                self.ufo.take_hit()
                # Spawn powerup right below the UFO body (inside the light beam)
                powerup = PowerUp(self, self.ufo.rect.centerx, self.ufo.rect.top + self.settings.ufo_height)
                self.powerups.add(powerup)
                self.all_sprites.add(powerup)
                self.score += self.ufo.get_points()
                self.ufo_channel.stop()

        # Check player collects powerups
        powerup_hits = pygame.sprite.spritecollide(self.player, self.powerups, True)
        for powerup in powerup_hits:
            self.ufo_powerup_sfx.play()
            if powerup.type == "multi_shot":
                self.settings.max_bullets = 3
                self.multi_shot_timer = self.settings.multi_shot_duration
            elif powerup.type == "life":
                self.lives = min(self.lives + 1, self.settings.max_lives)
            elif powerup.type == "time_freeze":
                self.time_freeze_timer = 5.0
            elif powerup.type == "laser":
                self.laser_timer = 5.0
                
    def _invader_shoot(self):
        if self.time_freeze_timer > 0:
            return
        if len(self.invader_fleet.invaders) > 0 and not self.cued_to_shoot:
            self.count_down = random.randint(0,5) #set counter to random value between 0 and 5 seconds
            self.cued_to_shoot = True
        else:
            self.count_down -= 1 / self.settings.fps #decrease counter based on frame rate
            if self.count_down <= 0:
                self.invader_fleet.shoot()
                self.invader_shoot_sfx.play() # play shoot sound effect
                self.cued_to_shoot = False

                
    def _tick_ufo(self):
        if self.ufo is not None and not self.ufo.alive():
            self.ufo_channel.stop()
            self.ufo = None
        if self.ufo is None:
            self.ufo_timer += 1 / self.settings.fps
            if self.ufo_timer >= self.ufo_interval:
                self.ufo = UFO(self, image=self.ufo_image, light_image=self.ufo_light_image)
                self.all_sprites.add(self.ufo)
                self.ufo_channel.play(self.ufo_sfx, loops=-1)
                self.ufo_timer = 0
                self.ufo_interval = random.randint(20, 40)
        if self.ufo is not None:
            self.ufo.update()

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
        music_vol = self.options["Music Vol"]["choices"][self.options["Music Vol"]["selected"]] / 100
        pygame.mixer.music.set_volume(music_vol)
        
        sfx_vol = self.options["SFX Vol"]["choices"][self.options["SFX Vol"]["selected"]] / 100
        self.shoot_sfx.set_volume(sfx_vol)
        self.player_hit_sfx.set_volume(sfx_vol)
        self.invader_killed_sfx.set_volume(sfx_vol)
        self.invader_shoot_sfx.set_volume(sfx_vol)
        self.ufo_sfx.set_volume(sfx_vol)
        self.ufo_hit_sfx.set_volume(sfx_vol)
        self.ufo_powerup_sfx.set_volume(sfx_vol)

    def _save_user_settings(self):
        import json
        settings_to_save = {}
        for key, data in self.options.items():
            settings_to_save[key] = data["selected"]
        try:
            with open("user_settings.json", "w") as f:
                json.dump(settings_to_save, f)
        except Exception as e:
            print("Could not save settings:", e)

    def _load_user_settings(self):
        import json
        try:
            with open("user_settings.json", "r") as f:
                saved_settings = json.load(f)
                for key, val in saved_settings.items():
                    if key in self.options:
                        self.options[key]["selected"] = val
        except Exception:
            pass
            
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

    def _draw_level_transition(self):
        self.screen.fill((0, 0, 0))
        font = pygame.font.SysFont(None, 72)
        text = "BOSS STAGE!" if self.current_level % 5 == 0 else f"Stage {self.current_level}"
        color = (255, 50, 50) if self.current_level % 5 == 0 else (255, 255, 255)
        level_text = font.render(text, True, color)
        self.screen.blit(level_text, (self.screen_width//2 - level_text.get_width()//2, self.screen_height//2 - level_text.get_height()//2))
        pygame.display.flip()
        
        self.level_transition_timer -= 1 / self.settings.fps
        if self.level_transition_timer <= 0:
            self.state = "playing"
            
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
        self.starfield.update()
        self.starfield.draw(self.screen)
        
        font_huge = pygame.font.SysFont(None, 100)
        font_large = pygame.font.SysFont(None, 72)
        font_small = pygame.font.SysFont(None, 36)
        
        game_over_text = font_huge.render("GAME OVER", True, (255, 50, 50))
        score_text = font_large.render(f"Final Score: {self.score}", True, (255, 255, 255))
        enter_text = font_small.render("Press ENTER to Restart", True, (255, 255, 255))
        esc_text = font_small.render("Press ESC to Quit", True, (255, 255, 255))
        
        self.screen.blit(game_over_text, (self.screen_width//2 - game_over_text.get_width()//2, self.screen_height//3))
        self.screen.blit(score_text, (self.screen_width//2 - score_text.get_width()//2, self.screen_height//2))
        self.screen.blit(enter_text, (self.screen_width//2 - enter_text.get_width()//2, self.screen_height//2 + 80))
        self.screen.blit(esc_text, (self.screen_width//2 - esc_text.get_width()//2, self.screen_height//2 + 130))
        
        pygame.display.flip()

        
    def draw_settings_screen(self):
        self.screen.fill((0, 0, 0)) 
        self.starfield.update()
        self.starfield.draw(self.screen)
        
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
                    img = self.invader_ship_imgs[self.options[option]["selected"]][0][0]
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
        self.powerups.update()
        self.particle_system.update()
        self.starfield.update()
        
        if self.time_freeze_timer > 0:
            self.time_freeze_timer -= 1 / self.settings.fps
        else:
            self.invader_bullets.update()
            self.invader_fleet.update()
            if self.boss and self.boss.alive():
                self.boss.update()
            self._tick_ufo()
        
        if self.multi_shot_timer > 0:
            self.multi_shot_timer -= 1 / self.settings.fps
            if self.multi_shot_timer <= 0:
                self.settings.max_bullets = 1
                
        if self.laser_timer > 0:
            self.laser_timer -= 1 / self.settings.fps
                
        # Dive bomber mechanic
        if self.current_level > 2 and len(self.invader_fleet.invaders) > 0:
            dive_chance = 0.001 + (self.current_level * 0.0005)
            if random.random() < dive_chance:
                diver = random.choice(self.invader_fleet.invaders.sprites())
                if not getattr(diver, 'diving', False):
                    diver.diving = True
            
            
    
    def _draw(self):
        self.game_surface.fill((0, 0, 0))
        self.starfield.draw(self.game_surface)
        
        self.all_sprites.draw(self.game_surface) # player, bullets, boss, particles
        
        if self.player.shielded and not self.plyr_is_hit:
            pygame.draw.circle(self.game_surface, (0, 191, 255), self.player.rect.center, 35, 3)

        self.invader_fleet.invaders.draw(self.game_surface) # invaders
        
        # Screen Shake
        offset_x, offset_y = 0, 0
        if self.shake_timer > 0:
            self.shake_timer -= 1 / self.settings.fps
            offset_x = random.randint(-5, 5)
            offset_y = random.randint(-5, 5)
            
        self.screen.fill((0, 0, 0))
        self.screen.blit(self.game_surface, (offset_x, offset_y))
        
        # HUD drawn on screen (unshaken)
        self.hud.draw()
        
        pygame.display.flip()