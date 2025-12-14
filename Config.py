# Config.py - Game Configuration
# Central configuration for all game parameters

class Config:
    # Display
    WINDOW_WIDTH = 1400
    WINDOW_HEIGHT = 1000
    FPS = 60
    
    # Map - FULL 32x32 grid harus fit di screen
    MAP_WIDTH = 32
    MAP_HEIGHT = 32
    TILE_SIZE = 28  # Reduced dari 40 untuk fit 32x32 di screen
    
    # Terrain costs
    TERRAIN_COSTS = {
        'road': 1,
        'grass': 2,
        'forest': 4,
        'swamp': 6,
        'stone': 100,
    }
    
    # Terrain colors
    TERRAIN_COLORS = {
        'road': (255, 255, 255),      # White
        'grass': (144, 238, 144),     # Light green
        'forest': (34, 139, 34),      # Dark green
        'swamp': (135, 206, 235),     # Light blue
        'stone': (169, 169, 169),     # Gray
    }
    
    # Game
    ENEMY_SPEED = 2.0
    ENEMY_HEALTH = 100
    BASE_HEALTH = 150
    INITIAL_RESOURCES = 300
    BARRICADE_COST = 20
    BARRICADE_RESOURCE_COST = 50
    KILL_REWARD = 20
    ENEMY_DAMAGE = 10
    
    # Waves
    WAVE_ENEMY_COUNT = [5, 8, 12, 15, 20, 25]
    WAVE_DELAY = 3.0
    SPAWN_RATE = 0.8
    
    # Start points
    NUM_START_POINTS = 3
    MIN_START_END_DISTANCE = 8  # Manhattan distance
    
    # Colors
    COLOR_BG = (20, 20, 30)
    COLOR_GRID = (40, 40, 50)
    COLOR_ENEMY = (255, 100, 100)
    COLOR_BASE = (0, 150, 255)
    COLOR_START = (0, 255, 0)
    COLOR_UI_BG = (40, 40, 50)
    COLOR_UI_TEXT = (255, 255, 255)
    
    ALERT_DURATION = 120  # frames (2 seconds at 60 FPS)
    
    HEALTH_BAR_HEIGHT = 6
    
    # Towers
    TOWER_ARROW_COST = 50
    TOWER_ARROW_RANGE = 5  # tiles
    TOWER_ARROW_DAMAGE = 25
    TOWER_ARROW_FIRE_RATE = 90  # frames (1.5 seconds at 60 FPS)
    
    TOWER_BOMB_COST = 100
    TOWER_BOMB_RANGE = 3  # tiles
    TOWER_BOMB_DAMAGE = 50
    TOWER_BOMB_FIRE_RATE = 180  # frames (3 seconds at 60 FPS)
    
    PROJECTILE_SPEED = 8
    EXPLOSION_RADIUS = 1.5  # tiles (reduced from 2 for balance)
    EXPLOSION_DURATION = 30  # frames (0.5 seconds at 60 FPS)
    
    COLOR_TOWER = (100, 100, 255)  # Blue for arrow towers
    COLOR_BOMB_TOWER = (255, 140, 0)  # Orange for bomb towers
    COLOR_PROJECTILE = (0, 0, 0)  # Black for arrows
    COLOR_BOMB_PROJECTILE = (255, 165, 0)  # Orange
    COLOR_EXPLOSION = (255, 100, 0)  # Red-orange
    
    # PNG Assets
    ASSETS_DIR = "assets"
    USE_PNG_GRAPHICS = True  # Set to False to always use fallback rendering
    
    # PNG file paths (relative to ASSETS_DIR)
    TILE_PNG_PATHS = {
        'grass': 'tiles/grass.png',
        'road': 'tiles/road.png',
        'forest': 'tiles/forest.png',
        'swamp': 'tiles/swamp.png',
        'stone': 'tiles/stone.png',
    }
    
    ENTITY_PNG_PATHS = {
        'enemy': 'entities/enemy.png',
    }
    
    MARKER_PNG_PATHS = {
        'start': 'markers/start.png',
        'end': 'markers/end.png',
    }
    
    BARRICADE_PNG_PATH = 'barricade.png'
    
    TOWER_PNG_PATHS = {
        'arrow': 'towers/arrow_tower.png',
        'bomb': 'towers/bomb_tower.png',
    }
