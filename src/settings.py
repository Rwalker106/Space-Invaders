from random import choice

class Settings:
    def __init__(self):
        self.debug = True
        self.screen_width = 800
        self.screen_height = 600    
        self.fps = 60
        self.bg_color = (0, 0, 0)  # Black background
        self.title = "Space Invaders"
        
        # Player settings
        self.player_speed = 5
        self.max_bullets = 1
        self.player_lives = 3
        self.starting_score = 0
        
        # Bullet settings
        self.bullet_speed = 7
        self.invader_bullet_width = 8
        self.invader_bullet_height = 8 # invader bullets
        self.player_bullet_width = 8
        self.player_bullet_height = 12
        
        # Invader settings
        self.invader_speed = 1  
        self.invader_drop_speed = 1
        self.fleet_direction = choice([-1, 1])  # 1 for right, -1 for left
        self.fleet_cols = 15
        self.fleet_rows = 5 
        
        # Barrier settings
        self.barrier_width = 100
        self.barrier_height = 50
        self.barrier_health = 3
        self.barrier_count = 4 # Number of barriers to create
        self.speed_cap = 2.0
        
        # UFO settings
        self.ufo_speed = 3    
        self.ufo_width = 80
        self.ufo_height = 32
        self.ufo_light_width = 80
        self.ufo_light_height = 80