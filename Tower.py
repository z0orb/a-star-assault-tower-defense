# Tower.py - Tower Entity Management
# Handles towers, projectiles, and explosions

import pygame
import math
from typing import List, Tuple, Optional

# Import Config and Enemy from other modules
from Config import Config
from Enemy import Enemy


class Projectile:
    """Projectile entity (arrows, etc.)"""
    def __init__(self, x: float, y: float, target_x: float, target_y: float, damage: int, 
                 projectile_type: str = "arrow", explosion_radius: int = 0):
        self.x = x
        self.y = y
        self.damage = damage
        self.alive = True
        self.projectile_type = projectile_type  # "arrow" or "bomb"
        self.explosion_radius = explosion_radius  # For bombs
        
        # Calculate direction to target
        dx = target_x - x
        dy = target_y - y
        dist = math.sqrt(dx**2 + dy**2)
        
        if dist > 0:
            self.vx = (dx / dist) * Config.PROJECTILE_SPEED
            self.vy = (dy / dist) * Config.PROJECTILE_SPEED
        else:
            self.vx = 0
            self.vy = 0
    
    def update(self, enemies: List['Enemy']) -> Optional['Explosion']:
        """Update projectile position and check collisions, returns explosion if bomb hits"""
        if not self.alive:
            return None
        
        # Move projectile
        self.x += self.vx
        self.y += self.vy
        
        # Check collision with enemies
        for enemy in enemies:
            if enemy.alive and not enemy.arrived:
                enemy_x = enemy.x
                enemy_y = enemy.y
                dist = math.sqrt((self.x - enemy_x)**2 + (self.y - enemy_y)**2)
                
                if dist < Config.TILE_SIZE / 2:  # Hit detection
                    self.alive = False
                    
                    # Create explosion for bomb projectiles
                    if self.projectile_type == "bomb":
                        return Explosion(self.x, self.y, self.explosion_radius, self.damage)
                    else:
                        # Direct damage for arrows
                        enemy.health -= self.damage
                        if enemy.health <= 0:
                            enemy.alive = False
                    return None
        
        # Remove if out of bounds
        if (self.x < 0 or self.x > Config.MAP_WIDTH * Config.TILE_SIZE or
            self.y < 0 or self.y > Config.MAP_HEIGHT * Config.TILE_SIZE):
            self.alive = False
            return None
        
        return None
    
    def draw(self, surface, offset_x: int = 0, offset_y: int = 0):
        """Draw projectile"""
        if self.alive:
            screen_x = int(self.x + offset_x)
            screen_y = int(self.y + offset_y)
            
            # Use appropriate color based on type
            if self.projectile_type == "bomb":
                color = Config.COLOR_BOMB_PROJECTILE
                radius = 4  # Slightly larger for bombs
            else:
                color = Config.COLOR_PROJECTILE
                radius = 3
            
            pygame.draw.circle(surface, color, (screen_x, screen_y), radius)


class Explosion:
    """Visual effect for bomb explosions"""
    def __init__(self, x: float, y: float, radius_tiles: int, damage: int):
        self.x = x
        self.y = y
        self.radius = radius_tiles * Config.TILE_SIZE  # Convert to pixels
        self.damage = damage
        self.timer = Config.EXPLOSION_DURATION
        self.alive = True
    
    def update(self) -> bool:
        """Update explosion timer"""
        self.timer -= 1
        if self.timer <= 0:
            self.alive = False
            return False
        return True
    
    def apply_damage(self, enemies: List['Enemy']):
        """Apply AoE damage to all enemies in radius"""
        for enemy in enemies:
            if enemy.alive and not enemy.arrived:
                dx = enemy.x - self.x
                dy = enemy.y - self.y
                dist = math.sqrt(dx**2 + dy**2)
                
                if dist <= self.radius:
                    enemy.health -= self.damage
                    if enemy.health <= 0:
                        enemy.alive = False
    
    def draw(self, surface, offset_x: int = 0, offset_y: int = 0):
        """Draw explosion visual effect"""
        if self.alive:
            screen_x = int(self.x + offset_x)
            screen_y = int(self.y + offset_y)
            
            # Fade out effect based on timer
            alpha = int(255 * (self.timer / Config.EXPLOSION_DURATION))
            
            # Draw explosion circle with alpha
            explosion_surface = pygame.Surface((self.radius * 2, self.radius * 2), pygame.SRCALPHA)
            pygame.draw.circle(explosion_surface, (*Config.COLOR_EXPLOSION, alpha), 
                             (self.radius, self.radius), self.radius)
            surface.blit(explosion_surface, (screen_x - self.radius, screen_y - self.radius))


class Tower:
    """Base tower class"""
    def __init__(self, x: int, y: int, tower_range: int, damage: int, fire_rate: int,
                 projectile_type: str = "arrow", explosion_radius: int = 0):
        self.x = x  # Grid coordinates
        self.y = y
        self.range = tower_range  # In tiles
        self.damage = damage
        self.fire_rate = fire_rate  # Frames between shots
        self.cooldown = 0
        self.target: Optional[Enemy] = None
        self.projectile_type = projectile_type  # "arrow" or "bomb"
        self.explosion_radius = explosion_radius  # For bombs
    
    def get_pixel_pos(self) -> Tuple[float, float]:
        """Get center position in pixels"""
        return (self.x * Config.TILE_SIZE + Config.TILE_SIZE / 2,
                self.y * Config.TILE_SIZE + Config.TILE_SIZE / 2)
    
    def find_target(self, enemies: List[Enemy]) -> Optional[Enemy]:
        """Find nearest enemy in range"""
        tower_px, tower_py = self.get_pixel_pos()
        range_px = self.range * Config.TILE_SIZE
        
        nearest = None
        nearest_dist = float('inf')
        
        for enemy in enemies:
            if enemy.alive and not enemy.arrived:
                dx = enemy.x - tower_px
                dy = enemy.y - tower_py
                dist = math.sqrt(dx**2 + dy**2)
                
                if dist <= range_px and dist < nearest_dist:
                    nearest = enemy
                    nearest_dist = dist
        
        return nearest
    
    def update(self, enemies: List[Enemy]) -> Optional[Projectile]:
        """Update tower, returns projectile if shooting"""
        # Decrease cooldown
        if self.cooldown > 0:
            self.cooldown -= 1
        
        # Find target
        self.target = self.find_target(enemies)
        
        # Shoot if ready and has target
        if self.target and self.cooldown <= 0:
            self.cooldown = self.fire_rate
            tower_px, tower_py = self.get_pixel_pos()
            return Projectile(tower_px, tower_py, self.target.x, self.target.y, 
                            self.damage, self.projectile_type, self.explosion_radius)
        
        return None
    
    def draw(self, surface, offset_x: int = 0, offset_y: int = 0, show_range: bool = False):
        """Draw tower"""
        tower_px, tower_py = self.get_pixel_pos()
        screen_x = int(tower_px + offset_x)
        screen_y = int(tower_py + offset_y)
        
        # Draw range indicator (semi-transparent circle)
        if show_range:
            range_px = self.range * Config.TILE_SIZE
            range_surface = pygame.Surface((range_px * 2, range_px * 2), pygame.SRCALPHA)
            pygame.draw.circle(range_surface, (100, 100, 255, 30), 
                             (range_px, range_px), range_px)
            surface.blit(range_surface, (screen_x - range_px, screen_y - range_px))
        
        # Use different colors based on tower type
        if self.projectile_type == "bomb":
            tower_color = Config.COLOR_BOMB_TOWER
            tower_highlight = (255, 180, 50)  # Lighter orange
        else:
            tower_color = Config.COLOR_TOWER
            tower_highlight = (150, 150, 255)  # Lighter blue
        
        # Draw tower body
        pygame.draw.rect(surface, tower_color,
                        (screen_x - Config.TILE_SIZE // 3, screen_y - Config.TILE_SIZE // 3,
                         Config.TILE_SIZE * 2 // 3, Config.TILE_SIZE * 2 // 3))
        pygame.draw.circle(surface, tower_highlight, (screen_x, screen_y), 
                          Config.TILE_SIZE // 4)


class ArrowTower(Tower):
    """Arrow tower - shoots arrows at enemies"""
    def __init__(self, x: int, y: int):
        super().__init__(x, y, 
                        Config.TOWER_ARROW_RANGE,
                        Config.TOWER_ARROW_DAMAGE,
                        Config.TOWER_ARROW_FIRE_RATE)


class BombTower(Tower):
    """Bomb tower - shoots explosive projectiles with AoE damage"""
    def __init__(self, x: int, y: int):
        super().__init__(x, y,
                        Config.TOWER_BOMB_RANGE,
                        Config.TOWER_BOMB_DAMAGE,
                        Config.TOWER_BOMB_FIRE_RATE,
                        projectile_type="bomb",
                        explosion_radius=Config.EXPLOSION_RADIUS)
