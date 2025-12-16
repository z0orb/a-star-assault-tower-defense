# Handles enemy spawning, movement, and rendering
import pygame
import math
from typing import List, Tuple

# Import Config from Config module
from Config import Config


class Enemy:
    """Enemy entity"""
    _id = 0
    
    def __init__(self, x: float, y: float):
        Enemy._id += 1
        self.id = Enemy._id
        self.x = x
        self.y = y
        self.health = Config.ENEMY_HEALTH
        self.path: List[Tuple[int, int]] = []
        self.path_index = 0
        self.speed = Config.ENEMY_SPEED
        self.alive = True
        self.arrived = False
    
    def set_path(self, path: List[Tuple[int, int]]):
        """Set path"""
        self.path = path if path else []
        self.path_index = 1 if len(path) > 1 else 0
    
    def update(self) -> bool:
        """Update enemy position"""
        if not self.alive or self.arrived:
            return False
        
        if self.path_index >= len(self.path):
            self.arrived = True
            return False
        
        # Get next waypoint in pixels
        grid_x, grid_y = self.path[self.path_index]
        target_x = grid_x * Config.TILE_SIZE + Config.TILE_SIZE / 2
        target_y = grid_y * Config.TILE_SIZE + Config.TILE_SIZE / 2
        
        dx = target_x - self.x
        dy = target_y - self.y
        dist = math.sqrt(dx**2 + dy**2)
        
        if dist < self.speed:
            self.x = target_x
            self.y = target_y
            self.path_index += 1
            if self.path_index >= len(self.path):
                self.arrived = True
                return False
        else:
            self.x += (dx / dist) * self.speed
            self.y += (dy / dist) * self.speed
        
        return True
    
    def draw(self, surface, offset_x: int = 0, offset_y: int = 0, sprite=None):
        """Draw enemy"""
        screen_x = int(self.x + offset_x)
        screen_y = int(self.y + offset_y)
        
        if sprite:
            # Render SVG sprite centered on enemy position
            sprite_rect = sprite.get_rect(center=(screen_x, screen_y))
            surface.blit(sprite, sprite_rect)
        else:
            # Fallback to current circle rendering
            pygame.draw.circle(surface, Config.COLOR_ENEMY, (screen_x, screen_y), max(2, Config.TILE_SIZE // 4))
        
        # Health bar (unchanged)
        health_bar_width = Config.TILE_SIZE * 0.8
        health_bar_x = screen_x - health_bar_width / 2
        health_bar_y = screen_y - Config.TILE_SIZE / 2 - 5
        
        pygame.draw.rect(surface, (100, 0, 0), 
                        (health_bar_x, health_bar_y, health_bar_width, 2))
        health_percent = self.health / Config.ENEMY_HEALTH
        pygame.draw.rect(surface, (0, 200, 0),
                        (health_bar_x, health_bar_y, health_bar_width * health_percent, 2))
