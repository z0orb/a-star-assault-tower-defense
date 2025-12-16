import pygame
import sys
import random
import math
from typing import List, Tuple, Optional, Dict, Set

# Import Config from Config module
from Config import Config

# Import from other game modules
from MapGen import MapGenerator, Tile
from Pathfinding import Pathfinder
from Enemy import Enemy
from Tower import Tower, ArrowTower, BombTower, Projectile, Explosion
from Interface import InterfaceRenderer
from GameEvents import AlertManager
from AssetLoader import AssetLoader

# Game manager class
class Game:
    """Main game manager"""
    
    def __init__(self):
        # Set DPI awareness for Windows to prevent blurry scaling
        if sys.platform == 'win32':
            try:
                import ctypes
                ctypes.windll.shcore.SetProcessDpiAwareness(1)
            except Exception:
                try:
                    import ctypes
                    ctypes.windll.user32.SetProcessDPIAware()
                except Exception:
                    pass

        pygame.init()
        
        # Smart resolution handling
        display_info = pygame.display.Info()
        screen_width = display_info.current_w
        screen_height = display_info.current_h
        
        # Check if screen is smaller than game window
        if screen_width < Config.WINDOW_WIDTH or screen_height < Config.WINDOW_HEIGHT:
            self.fullscreen = True
            self.screen = pygame.display.set_mode((Config.WINDOW_WIDTH, Config.WINDOW_HEIGHT), pygame.FULLSCREEN | pygame.SCALED)
        else:
            self.fullscreen = False
            self.screen = pygame.display.set_mode((Config.WINDOW_WIDTH, Config.WINDOW_HEIGHT), pygame.SCALED)
            
        pygame.display.set_caption("A* Assault")
        self.clock = pygame.time.Clock()
        
        # Initialize fonts
        fonts = {
            'tiny': pygame.font.Font(None, 14),
            'small': pygame.font.Font(None, 16),
            'large': pygame.font.Font(None, 24),
            'alert': pygame.font.Font(None, 32)
        }
        
        # Initialize asset loader and renderer
        self.asset_loader = AssetLoader()
        self.renderer = InterfaceRenderer(self.screen, fonts, self.asset_loader)
        self.alert_manager = AlertManager()
        
        # Map generation
        self.map_gen = MapGenerator(Config.MAP_WIDTH, Config.MAP_HEIGHT)
        self.start_points = self.map_gen.start_points
        
        # Tiles
        self.tiles: Dict[Tuple[int, int], Tile] = {}
        for y in range(Config.MAP_HEIGHT):
            for x in range(Config.MAP_WIDTH):
                terrain = self.map_gen.get_tile(x, y)
                self.tiles[(x, y)] = Tile(x, y, terrain)
        
        # Pathfinding
        self.pathfinder = Pathfinder(Config.MAP_WIDTH, Config.MAP_HEIGHT, self.map_gen)
        
        # Entities
        self.enemies: List[Enemy] = []
        self.base_x = Config.MAP_WIDTH - 1
        self.base_y = Config.MAP_HEIGHT - 1
        self.base_health = Config.BASE_HEALTH
        
        # Game state
        self.resources = Config.INITIAL_RESOURCES
        self.wave = 0
        self.wave_active = False
        self.spawn_timer = 0
        self.enemies_spawned = 0
        self.enemies_to_spawn = 0
        self.paused = False
        self.game_won = False
        self.game_lost = False
        self.fps = 0
        self.kills = 0
        self.score = 0
        
        self.start_paths: Dict[Tuple[int, int], List[Tuple[int, int]]] = {}
        self._recalculate_all_start_paths()
        
        # Towers and projectiles
        self.towers: List[Tower] = []
        self.projectiles: List[Projectile] = []
        self.explosions: List[Explosion] = []
        self.selected_tower_type: Optional[str] = None

        # Difficulty
        self.difficulty = "EASY"
        self.total_waves = Config.DIFFICULTY_WAVES[self.difficulty]
        self.difficulty_locked = False
        self.difficulty_button_rects = {}
        
        # Display settings
        self.fullscreen = False
        
        # Calculate map display area
        self.map_width_px = Config.MAP_WIDTH * Config.TILE_SIZE
        self.map_height_px = Config.MAP_HEIGHT * Config.TILE_SIZE
        self.map_offset_x = 10
        self.map_offset_y = 10
        self.ui_height = Config.WINDOW_HEIGHT - self.map_height_px - 20
        self.ui_panel_x = self.map_offset_x + self.map_width_px + 20  # Right panel position
    
    def handle_events(self):
        """Handle input"""
        mouse_pos = pygame.mouse.get_pos()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            
            elif event.type == pygame.KEYDOWN:
                # Setup Esc key to quit
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()

                # F11 for fullscreen toggle
                if event.key == pygame.K_F11:
                    self.toggle_fullscreen()
                
                # Space to start wave
                if event.key == pygame.K_SPACE:
                    if not self.wave_active and not self.game_lost and not self.game_won:
                        self.start_wave()
                
                # R to restart
                if event.key == pygame.K_r:
                    # Properly restart the game at any time
                    self.restart_game()
            
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left click
                    # Check tower selection buttons
                    panel_x = self.ui_panel_x
                    panel_y = 150
                    
                    arrow_rect = pygame.Rect(panel_x, panel_y, 200, 40)
                    bomb_rect = pygame.Rect(panel_x, panel_y + 50, 200, 40)
                    
                    if arrow_rect.collidepoint(mouse_pos):
                        self.selected_tower_type = "arrow"
                    elif bomb_rect.collidepoint(mouse_pos):
                        self.selected_tower_type = "bomb"
                    else:
                        # Check difficulty selection if not locked
                        if not self.difficulty_locked:
                            for diff, rect in self.difficulty_button_rects.items():
                                if rect.collidepoint(mouse_pos):
                                    self.difficulty = diff
                                    self.total_waves = Config.DIFFICULTY_WAVES[self.difficulty]
                        
                        # Check if clicking on map
                        map_x = (mouse_pos[0] - self.map_offset_x) // Config.TILE_SIZE
                        map_y = (mouse_pos[1] - self.map_offset_y) // Config.TILE_SIZE
                        
                        if 0 <= map_x < Config.MAP_WIDTH and 0 <= map_y < Config.MAP_HEIGHT:
                            if self.selected_tower_type:
                                self.place_tower(map_x, map_y, self.selected_tower_type)
                
                elif event.button == 3:  # Right click
                    # Check if clicking on map for barricade
                    map_x = (mouse_pos[0] - self.map_offset_x) // Config.TILE_SIZE
                    map_y = (mouse_pos[1] - self.map_offset_y) // Config.TILE_SIZE
                    
                    if 0 <= map_x < Config.MAP_WIDTH and 0 <= map_y < Config.MAP_HEIGHT:
                        tile = self.tiles.get((map_x, map_y))
                        if tile:
                            if tile.has_barricade:
                                self.remove_barricade(map_x, map_y)
                            else:
                                self.place_barricade(map_x, map_y)
    
    def toggle_fullscreen(self):
        """Toggle between windowed and fullscreen mode"""
        self.fullscreen = not self.fullscreen
        if self.fullscreen:
            self.screen = pygame.display.set_mode((Config.WINDOW_WIDTH, Config.WINDOW_HEIGHT), pygame.FULLSCREEN | pygame.SCALED)
        else:
            self.screen = pygame.display.set_mode((Config.WINDOW_WIDTH, Config.WINDOW_HEIGHT), pygame.SCALED)
        
        # Update renderer's screen reference
        self.renderer.screen = self.screen
    
    def restart_game(self):
        """Restart the game with a new map"""
        # Regenerate map
        self.map_gen = MapGenerator(Config.MAP_WIDTH, Config.MAP_HEIGHT)
        self.start_points = self.map_gen.start_points
        
        # Reset tiles
        self.tiles: Dict[Tuple[int, int], Tile] = {}
        for y in range(Config.MAP_HEIGHT):
            for x in range(Config.MAP_WIDTH):
                terrain = self.map_gen.get_tile(x, y)
                self.tiles[(x, y)] = Tile(x, y, terrain)
        
        # Reset pathfinding
        self.pathfinder = Pathfinder(Config.MAP_WIDTH, Config.MAP_HEIGHT, self.map_gen)
        
        # Reset entities
        self.enemies: List[Enemy] = []
        self.base_health = Config.BASE_HEALTH
        
        # Reset game state
        self.resources = Config.INITIAL_RESOURCES
        self.wave = 0
        self.wave_active = False
        self.spawn_timer = 0
        self.enemies_spawned = 0
        self.enemies_to_spawn = 0
        self.game_won = False
        self.game_lost = False
        self.kills = 0
        self.score = 0
        
        # Reset Difficulty State
        self.difficulty = "EASY"
        self.total_waves = Config.DIFFICULTY_WAVES[self.difficulty]
        self.difficulty_locked = False
        
        # Recalculate paths
        self.start_paths: Dict[Tuple[int, int], List[Tuple[int, int]]] = {}
        self._recalculate_all_start_paths()
        
        # Reset towers and projectiles
        self.towers: List[Tower] = []
        self.projectiles: List[Projectile] = []
        self.explosions: List[Explosion] = []
        self.selected_tower_type: Optional[str] = None
        
        # Clear alerts
        self.alert_manager.clear()
    
    def start_wave(self):
        """Start new wave"""
        if self.wave < self.total_waves:
            # Lock difficulty selection once first wave starts
            if self.wave == 0:
                self.difficulty_locked = True
                
            self.wave += 1
            self.wave_active = True
            
            # Dynamic enemy count calculation
            if self.wave <= len(Config.WAVE_ENEMY_COUNT):
                # Use predefined count
                self.enemies_to_spawn = Config.WAVE_ENEMY_COUNT[self.wave - 1]
            else:
                # Dynamic scaling
                base_enemies = Config.WAVE_ENEMY_COUNT[-1]
                extra_waves = self.wave - len(Config.WAVE_ENEMY_COUNT)
                self.enemies_to_spawn = base_enemies + (extra_waves * Config.DYNAMIC_WAVE_SCALING_ADD)
            
            self.enemies_spawned = 0
            self.spawn_timer = 0
            self.alert_manager.add_alert(f"Wave {self.wave} started!", Config.ALERT_DURATION)
    
    def place_barricade(self, x: int, y: int):
        """Place barricade"""
        tile = self.tiles.get((x, y))
        if not tile or tile.has_barricade:
            return
        
        if self.resources < Config.BARRICADE_RESOURCE_COST:
            self.alert_manager.add_alert("Not enough resources!", Config.ALERT_DURATION)
            return
        
        tile.has_barricade = True
        self.resources -= Config.BARRICADE_RESOURCE_COST
        self._sync_pathfinder()
        self._recalculate_paths()
        self._recalculate_all_start_paths()
        self.alert_manager.add_alert("Barricade placed!", Config.ALERT_DURATION // 2)
    
    def remove_barricade(self, x: int, y: int):
        """Remove barricade"""
        tile = self.tiles.get((x, y))
        if tile and tile.has_barricade:
            tile.has_barricade = False
            self._sync_pathfinder()
            self._recalculate_paths()
            self._recalculate_all_start_paths()
    
    def place_tower(self, x: int, y: int, tower_type: str):
        """Place tower"""
        tile = self.tiles.get((x, y))
        if not tile:
            return
        
        # Check if tile is valid for tower placement
        if tile.terrain == 'stone':
            self.alert_manager.add_alert("Cannot place tower on stone!", Config.ALERT_DURATION)
            return
        
        if tile.has_barricade:
            self.alert_manager.add_alert("Cannot place tower on barricade!", Config.ALERT_DURATION)
            return
        
        # Check if there's already a tower here
        for tower in self.towers:
            if tower.x == x and tower.y == y:
                self.alert_manager.add_alert("Tower already exists here!", Config.ALERT_DURATION)
                return
        
        # Check resources and place tower
        if tower_type == "arrow":
            if self.resources >= Config.TOWER_ARROW_COST:
                self.towers.append(ArrowTower(x, y))
                self.resources -= Config.TOWER_ARROW_COST
                self.alert_manager.add_alert("Arrow tower placed!", Config.ALERT_DURATION // 2)
            else:
                self.alert_manager.add_alert("Not enough resources!", Config.ALERT_DURATION)
        
        elif tower_type == "bomb":
            if self.resources >= Config.TOWER_BOMB_COST:
                self.towers.append(BombTower(x, y))
                self.resources -= Config.TOWER_BOMB_COST
                self.alert_manager.add_alert("Bomb tower placed!", Config.ALERT_DURATION // 2)
            else:
                self.alert_manager.add_alert("Not enough resources!", Config.ALERT_DURATION)
    
    def _sync_pathfinder(self):
        """Sync map costs to pathfinder"""
        for (x, y), tile in self.tiles.items():
            self.pathfinder.update_cost(x, y, tile.get_cost())
    
    def _recalculate_paths(self):
        """Recalculate paths for all enemies"""
        for enemy in self.enemies:
            if enemy.alive and not enemy.arrived:
                grid_x = int(enemy.x / Config.TILE_SIZE)
                grid_y = int(enemy.y / Config.TILE_SIZE)
                path = self.pathfinder.find_path((grid_x, grid_y), (self.base_x, self.base_y))
                if path:
                    enemy.set_path(path)
    
    def _recalculate_all_start_paths(self):
        """Recalculate visualization paths from each START point"""
        self.start_paths = {}
        for start_point in self.start_points:
            path = self.pathfinder.find_path(start_point, (self.base_x, self.base_y))
            if path:
                self.start_paths[start_point] = path
    
    def spawn_enemy(self):
        """Spawn single enemy from random START point"""
        if not self.start_points:
            return
        
        start_point = random.choice(self.start_points)
        enemy_x = start_point[0] * Config.TILE_SIZE + Config.TILE_SIZE / 2
        enemy_y = start_point[1] * Config.TILE_SIZE + Config.TILE_SIZE / 2
        enemy = Enemy(enemy_x, enemy_y)
        
        # Apply difficulty health scaling
        # Base health + (wave number * scaling factor)
        extra_health = (self.wave - 1) * Config.ENEMY_HEALTH_SCALING
        enemy.health = Config.ENEMY_HEALTH + extra_health
        enemy.max_health = enemy.health
        
        path = self.pathfinder.find_path(start_point, (self.base_x, self.base_y))
        if path:
            enemy.set_path(path)
            self.enemies.append(enemy)
    
    def update(self):
        """Update game"""
        if self.game_lost or self.game_won:
            return
        
        # Update alert manager
        self.alert_manager.update()
        
        # Spawn enemies
        if self.wave_active and self.enemies_spawned < self.enemies_to_spawn:
            self.spawn_timer += 1
            if self.spawn_timer >= Config.SPAWN_RATE * Config.FPS:
                self.spawn_enemy()
                self.enemies_spawned += 1
                self.spawn_timer = 0
        
        # Update enemies
        for enemy in self.enemies:
            enemy.update()
            
            # Check if enemy reached base
            if enemy.arrived and enemy.alive:
                self.base_health -= Config.ENEMY_DAMAGE
                enemy.alive = False
                if self.base_health <= 0:
                    self.game_lost = True
                    self.alert_manager.clear()
        
        # Update towers and create projectiles
        for tower in self.towers:
            projectile = tower.update(self.enemies)
            if projectile:
                self.projectiles.append(projectile)
        
        # Update projectiles
        for projectile in self.projectiles:
            explosion = projectile.update(self.enemies)
            if explosion:
                self.explosions.append(explosion)
                explosion.apply_damage(self.enemies)
        
        # Remove dead projectiles
        self.projectiles = [p for p in self.projectiles if p.alive]
        
        # Update explosions
        for explosion in self.explosions:
            explosion.update()
        
        # Remove dead explosions
        self.explosions = [e for e in self.explosions if e.alive]
        
        # Count kills and give rewards
        for enemy in self.enemies:
            if not enemy.alive and not enemy.arrived:
                self.kills += 1
                self.score += Config.SCORE_PER_KILL
                self.resources += Config.KILL_REWARD
        
        # Remove dead enemies (keep only alive ones)
        self.enemies = [e for e in self.enemies if e.alive]
        
        # Check wave completion
        if self.wave_active:
            if self.enemies_spawned >= self.enemies_to_spawn and len(self.enemies) == 0:
                self.wave_active = False
                
                # Check if all waves completed
                if self.wave >= self.total_waves:
                    self.game_won = True
                    self.alert_manager.clear()
                else:
                    self.alert_manager.add_alert(f"Wave {self.wave} complete!", Config.ALERT_DURATION)
    
    def render(self):
        """Render game"""
        self.screen.fill(Config.COLOR_BG)
        
        # Render map
        self.renderer.render_map(self.tiles, Config.MAP_WIDTH, Config.MAP_HEIGHT, 
                                self.map_offset_x, self.map_offset_y)
        
        # Render paths
        self.renderer.render_paths(self.start_paths, self.map_offset_x, self.map_offset_y)
        
        # Render START and END points
        self.renderer.render_start_end_points(self.start_points, (self.base_x, self.base_y),
                                             self.map_offset_x, self.map_offset_y)
        
        # Render entities
        self.renderer.render_entities(self.enemies, self.towers, self.projectiles, self.explosions,
                                      self.map_offset_x, self.map_offset_y)
        
        # Render UI panel
        self.renderer.render_ui_panel(self.base_health, self.resources, self.score, self.wave, self.total_waves,
                                      self.wave_active, self.game_lost, self.game_won)
        
        # Render tower selection
        mouse_pos = pygame.mouse.get_pos()
        self.renderer.render_tower_selection(self.ui_panel_x, 150, self.selected_tower_type, mouse_pos)
        
        # Render instructions
        self.renderer.render_instructions(self.ui_panel_x, 250)
        
        # Render difficulty selection
        self.difficulty_button_rects = self.renderer.render_difficulty_selection(
            self.ui_panel_x, 380, self.difficulty, self.difficulty_locked, mouse_pos
        )
        
        # Render alerts
        active_alerts = self.alert_manager.get_active_alerts()
        self.renderer.render_alerts(active_alerts)
        
        # Render game over or win screen
        if self.game_lost:
            self.renderer.render_game_over(self.score)
        elif self.game_won:
            self.renderer.render_win_screen(self.score)
        
        pygame.display.flip()
    
    def run(self):
        """Main loop"""
        running = True
        while running:
            self.handle_events()
            self.update()
            self.render()
            self.clock.tick(Config.FPS)
            self.fps = self.clock.get_fps()


# Program Entry Point
if __name__ == "__main__":
    game = Game()
    game.run()