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
        
        # Bullet settings
        self.bullet_speed = 7
        self.bullet_width = 5
        self.bullet_height = 15
        self.bullet_color = (255, 0, 0) # Red bullets
        
        # Invader settings
        self.invader_speed = 1  
        self.invader_drop_speed = 2
        self.fleet_direction = choice([-1, 1])  # 1 for right, -1 for left
        self.fleet_cols = 15
        self.fleet_rows = 5 
        
        # Barrier settings
        self.barrier_width = 10
        self.barrier_height = 10
        self.barrier_color = (0, 255, 0) # Green barriers
        self.barrier_health = 3
        self.barrier_shape = [
            "XXXXXXXXX",
            "XXXXXXXXX", 
            "XXXXXXXXX",
            "XXX   XXX"
        ]
        self.barrier_count = 4 # Number of barriers to create