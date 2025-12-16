# Handles all rendering logic for the game interface
import pygame
from typing import List, Tuple, Optional, Dict, Any

# Import necessary classes from other modules
from Config import Config
from MapGen import Tile, MapGenerator
from Pathfinding import Pathfinder
from Enemy import Enemy
from Tower import Tower, Projectile, Explosion
from AssetLoader import AssetLoader


class InterfaceRenderer:
    """Handles all UI rendering for the game"""
    
    def __init__(self, screen: pygame.Surface, fonts: Dict[str, pygame.font.Font], asset_loader: AssetLoader):
        self.screen = screen
        self.fonts = fonts
        self.asset_loader = asset_loader
    
    def render_map(self, tiles: Dict[Tuple[int, int], Tile], map_width: int, map_height: int, 
                   offset_x: int = 0, offset_y: int = 0):
        """Render the game map tiles"""
        for y in range(map_height):
            for x in range(map_width):
                if (x, y) in tiles:
                    tile = tiles[(x, y)]
                    rect = pygame.Rect(
                        x * Config.TILE_SIZE + offset_x,
                        y * Config.TILE_SIZE + offset_y,
                        Config.TILE_SIZE,
                        Config.TILE_SIZE
                    )
                    
                    # Try to load SVG sprite first
                    sprite = self.asset_loader.get_tile_sprite(tile.terrain, Config.TILE_SIZE)
                    
                    if sprite:
                        # Render tile sprite
                        self.screen.blit(sprite, rect.topleft)
                    else:
                        # Fallback to current rectangle rendering
                        color = tile.get_color()
                        pygame.draw.rect(self.screen, color, rect)
                    
                    # Render barricade
                    if tile.has_barricade:
                        barricade_sprite = self.asset_loader.get_barricade_sprite(Config.TILE_SIZE)
                        if barricade_sprite:
                            self.screen.blit(barricade_sprite, rect.topleft)
                        elif not sprite:
                            # Fallback already handled by get_color() if no tile sprite
                            pass
                        elif sprite:
                            # If we have tile sprite but NO barricade sprite, draw overlay
                            s = pygame.Surface((Config.TILE_SIZE, Config.TILE_SIZE), pygame.SRCALPHA)
                            s.fill((0, 0, 0, 100))  # Dark overlay
                            self.screen.blit(s, rect.topleft)
                    
                    # Draw grid lines
                    pygame.draw.rect(self.screen, Config.COLOR_GRID, rect, 1)
    
    def render_paths(self, start_paths: Dict[Tuple[int, int], List[Tuple[int, int]]], 
                     offset_x: int = 0, offset_y: int = 0):
        """Render visualization paths from START points"""
        for path in start_paths.values():
            if path and len(path) > 1:
                points = []
                for gx, gy in path:
                    px = gx * Config.TILE_SIZE + Config.TILE_SIZE // 2 + offset_x
                    py = gy * Config.TILE_SIZE + Config.TILE_SIZE // 2 + offset_y
                    points.append((px, py))
                if len(points) > 1:
                    pygame.draw.lines(self.screen, (200, 200, 200), False, points, 2)
    
    def render_start_end_points(self, start_points: List[Tuple[int, int]], 
                                end_point: Tuple[int, int], offset_x: int = 0, offset_y: int = 0):
        """Render START and END point markers"""
        # Draw START points
        start_sprite = self.asset_loader.get_marker_sprite('start', Config.TILE_SIZE)
        for sx, sy in start_points:
            center_x = sx * Config.TILE_SIZE + Config.TILE_SIZE // 2 + offset_x
            center_y = sy * Config.TILE_SIZE + Config.TILE_SIZE // 2 + offset_y
            
            if start_sprite:
                # Render SVG sprite centered
                sprite_rect = start_sprite.get_rect(center=(center_x, center_y))
                self.screen.blit(start_sprite, sprite_rect)
            else:
                # Fallback to circle rendering
                pygame.draw.circle(self.screen, Config.COLOR_START, (center_x, center_y), 
                                 Config.TILE_SIZE // 3)
        
        # Draw END point
        end_sprite = self.asset_loader.get_marker_sprite('end', Config.TILE_SIZE)
        ex, ey = end_point
        center_x = ex * Config.TILE_SIZE + Config.TILE_SIZE // 2 + offset_x
        center_y = ey * Config.TILE_SIZE + Config.TILE_SIZE // 2 + offset_y
        
        if end_sprite:
            # Render SVG sprite centered
            sprite_rect = end_sprite.get_rect(center=(center_x, center_y))
            self.screen.blit(end_sprite, sprite_rect)
        else:
            # Fallback to circle rendering
            pygame.draw.circle(self.screen, Config.COLOR_BASE, (center_x, center_y), 
                             Config.TILE_SIZE // 2)
    
    def render_entities(self, enemies: List[Enemy], towers: List[Tower], 
                       projectiles: List[Projectile], explosions: List[Explosion],
                       offset_x: int = 0, offset_y: int = 0, selected_tower: Optional[Tower] = None):
        """Render all game entities"""
        # Pre-load tower sprites
        arrow_sprite = self.asset_loader.get_tower_sprite('arrow', Config.TILE_SIZE)
        bomb_sprite = self.asset_loader.get_tower_sprite('bomb', Config.TILE_SIZE)
        
        # Draw towers
        for tower in towers:
            show_range = (tower == selected_tower)
            
            # Select correct sprite based on type
            sprite = None
            if tower.projectile_type == "arrow":
                sprite = arrow_sprite
            elif tower.projectile_type == "bomb":
                sprite = bomb_sprite
                
            tower.draw(self.screen, offset_x, offset_y, show_range, sprite)
        
        # Get enemy sprite once for all enemies
        enemy_sprite = self.asset_loader.get_enemy_sprite(Config.TILE_SIZE)
        
        # Draw enemies
        for enemy in enemies:
            if enemy.alive:
                enemy.draw(self.screen, offset_x, offset_y, enemy_sprite)
        
        # Draw projectiles
        for projectile in projectiles:
            projectile.draw(self.screen, offset_x, offset_y)
        
        # Draw explosions
        for explosion in explosions:
            explosion.draw(self.screen, offset_x, offset_y)
    
    def render_ui_panel(self, base_health: int, resources: int, score: int, wave: int, total_waves: int,
                       wave_in_progress: bool, game_over: bool, won: bool):
        """Render the main UI stats panel"""
        panel_x = Config.MAP_WIDTH * Config.TILE_SIZE + 20
        panel_y = 20
        
        # Stats
        health_text = self.fonts['large'].render(f"Base Health: {base_health}", True, Config.COLOR_UI_TEXT)
        self.screen.blit(health_text, (panel_x, panel_y))
        
        resources_text = self.fonts['large'].render(f"Resources: ${resources}", True, Config.COLOR_UI_TEXT)
        self.screen.blit(resources_text, (panel_x, panel_y + 30))
        
        score_text = self.fonts['large'].render(f"Score: {score}", True, Config.COLOR_UI_TEXT)
        self.screen.blit(score_text, (panel_x, panel_y + 60))
        
        wave_text = self.fonts['large'].render(f"Wave: {wave}/{total_waves}", True, Config.COLOR_UI_TEXT)
        self.screen.blit(wave_text, (panel_x, panel_y + 90))
        
        # Wave status
        if not wave_in_progress and not game_over and not won:
            status_text = self.fonts['small'].render("Press SPACE to start wave", True, (0, 255, 0))
            self.screen.blit(status_text, (panel_x, panel_y + 120))
    
    def render_tower_selection(self, panel_x: int, panel_y: int, selected_tower_type: Optional[str],
                               mouse_pos: Tuple[int, int]):
        """Render tower selection UI"""
        # Arrow Tower button
        arrow_rect = pygame.Rect(panel_x, panel_y, 200, 40)
        arrow_color = (100, 150, 255) if selected_tower_type == "arrow" else (60, 90, 150)
        if arrow_rect.collidepoint(mouse_pos):
            arrow_color = tuple(min(c + 30, 255) for c in arrow_color)
        pygame.draw.rect(self.screen, arrow_color, arrow_rect)
        pygame.draw.rect(self.screen, Config.COLOR_UI_TEXT, arrow_rect, 2)
        
        arrow_text = self.fonts['small'].render(f"Arrow Tower (${Config.TOWER_ARROW_COST})", True, Config.COLOR_UI_TEXT)
        self.screen.blit(arrow_text, (panel_x + 10, panel_y + 12))
        
        # Bomb Tower button
        bomb_rect = pygame.Rect(panel_x, panel_y + 50, 200, 40)
        bomb_color = (255, 150, 50) if selected_tower_type == "bomb" else (150, 90, 30)
        if bomb_rect.collidepoint(mouse_pos):
            bomb_color = tuple(min(c + 30, 255) for c in bomb_color)
        pygame.draw.rect(self.screen, bomb_color, bomb_rect)
        pygame.draw.rect(self.screen, Config.COLOR_UI_TEXT, bomb_rect, 2)
        
        bomb_text = self.fonts['small'].render(f"Bomb Tower (${Config.TOWER_BOMB_COST})", True, Config.COLOR_UI_TEXT)
        self.screen.blit(bomb_text, (panel_x + 10, panel_y + 62))
        
        return arrow_rect, bomb_rect
    
    def render_instructions(self, panel_x: int, panel_y: int):
        """Render game instructions"""
        instructions = [
            "Instructions:",
            "- Click tower, then map to place",
            "- Right-click to place barricade ($50)",
            "- Right-click barricade to remove",
            "- Press SPACE to start wave",
            "- Press F11 for fullscreen",
            "- Press R to restart"
        ]
        
        for i, instruction in enumerate(instructions):
            text = self.fonts['tiny'].render(instruction, True, Config.COLOR_UI_TEXT)
            self.screen.blit(text, (panel_x, panel_y + i * 18))
    
    def render_alerts(self, alerts: List[str]):
        """Render alert messages"""
        alert_y = Config.WINDOW_HEIGHT // 2 - 100
        for alert_msg in alerts:
            alert_surface = self.fonts['alert'].render(alert_msg, True, (255, 255, 0))
            alert_rect = alert_surface.get_rect(center=(Config.WINDOW_WIDTH // 2, alert_y))
            
            # Draw background
            bg_rect = alert_rect.inflate(40, 20)
            bg_surface = pygame.Surface(bg_rect.size, pygame.SRCALPHA)
            pygame.draw.rect(bg_surface, (0, 0, 0, 180), bg_surface.get_rect(), border_radius=10)
            self.screen.blit(bg_surface, bg_rect.topleft)
            
            # Draw text
            self.screen.blit(alert_surface, alert_rect)
            alert_y += 60
    
    def render_game_over(self, score: int):
        """Render game over screen"""
        overlay = pygame.Surface((Config.WINDOW_WIDTH, Config.WINDOW_HEIGHT), pygame.SRCALPHA)
        pygame.draw.rect(overlay, (0, 0, 0, 180), overlay.get_rect())
        self.screen.blit(overlay, (0, 0))
        
        game_over_text = self.fonts['alert'].render("GAME OVER", True, (255, 0, 0))
        game_over_rect = game_over_text.get_rect(center=(Config.WINDOW_WIDTH // 2, Config.WINDOW_HEIGHT // 2 - 50))
        self.screen.blit(game_over_text, game_over_rect)
        
        restart_text = self.fonts['large'].render("Press R to restart", True, Config.COLOR_UI_TEXT)
        restart_rect = restart_text.get_rect(center=(Config.WINDOW_WIDTH // 2, Config.WINDOW_HEIGHT // 2 + 50))
        self.screen.blit(restart_text, restart_rect)
        
        score_text = self.fonts['large'].render(f"Total Score: {score}", True, (255, 255, 0))
        score_rect = score_text.get_rect(center=(Config.WINDOW_WIDTH // 2, Config.WINDOW_HEIGHT // 2 + 20))
        self.screen.blit(score_text, score_rect)
    
    def render_win_screen(self, score: int):
        """Render win screen"""
        overlay = pygame.Surface((Config.WINDOW_WIDTH, Config.WINDOW_HEIGHT), pygame.SRCALPHA)
        pygame.draw.rect(overlay, (0, 0, 0, 180), overlay.get_rect())
        self.screen.blit(overlay, (0, 0))
        
        win_text = self.fonts['alert'].render("VICTORY!", True, (0, 255, 0))
        win_rect = win_text.get_rect(center=(Config.WINDOW_WIDTH // 2, Config.WINDOW_HEIGHT // 2 - 50))
        self.screen.blit(win_text, win_rect)
        
        congrats_text = self.fonts['large'].render("All waves completed!", True, Config.COLOR_UI_TEXT)
        congrats_rect = congrats_text.get_rect(center=(Config.WINDOW_WIDTH // 2, Config.WINDOW_HEIGHT // 2 + 20))
        self.screen.blit(congrats_text, congrats_rect)
        
        restart_text = self.fonts['large'].render("Press R to restart", True, Config.COLOR_UI_TEXT)
        restart_rect = restart_text.get_rect(center=(Config.WINDOW_WIDTH // 2, Config.WINDOW_HEIGHT // 2 + 90))
        self.screen.blit(restart_text, restart_rect)
        
        score_text = self.fonts['large'].render(f"Total Score: {score}", True, (255, 255, 0))
        score_rect = score_text.get_rect(center=(Config.WINDOW_WIDTH // 2, Config.WINDOW_HEIGHT // 2 + 60))
        self.screen.blit(score_text, score_rect)
    
    def render_difficulty_selection(self, panel_x: int, panel_y: int, current_difficulty: str, locked: bool, mouse_pos: Tuple[int, int]):
        """Render difficulty selection buttons"""
        # Header
        header_text = self.fonts['small'].render("Select Difficulty:", True, Config.COLOR_UI_TEXT)
        self.screen.blit(header_text, (panel_x, panel_y))
        
        difficulties = ["EASY", "NORMAL", "HARD"]
        colors = {
            "EASY": (0, 200, 0),
            "NORMAL": (200, 200, 0),
            "HARD": (200, 0, 0)
        }
        
        button_width = 60
        button_height = 30
        spacing = 10
        
        button_rects = {}
        
        current_x = panel_x
        buttons_y = panel_y + 20
        
        for diff in difficulties:
            rect = pygame.Rect(current_x, buttons_y, button_width, button_height)
            button_rects[diff] = rect
            
            # Determine color
            base_color = colors[diff]
            
            if locked:
                # Dim colors if locked
                if current_difficulty == diff:
                     # Keep selected one visible but dim others
                     color = base_color
                else:
                     color = (50, 50, 50) # Greyed out
            else:
                # Active selection logic
                if current_difficulty == diff:
                    color = tuple(min(c + 50, 255) for c in base_color) # Highlight selected
                    pygame.draw.rect(self.screen, (255, 255, 255), rect.inflate(4, 4), 2) # Selection border
                elif rect.collidepoint(mouse_pos):
                    color = tuple(min(c + 30, 255) for c in base_color) # Hover
                else:
                    color = base_color
            
            pygame.draw.rect(self.screen, color, rect)
            pygame.draw.rect(self.screen, Config.COLOR_UI_TEXT, rect, 1)
            
            # Text
            text_surf = self.fonts['tiny'].render(diff, True, (0, 0, 0) if not (locked and current_difficulty != diff) else (150, 150, 150))
            text_rect = text_surf.get_rect(center=rect.center)
            self.screen.blit(text_surf, text_rect)
            
            current_x += button_width + spacing
            
        return button_rects
