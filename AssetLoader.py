# AssetLoader.py - PNG Asset Loading and Caching
# Handles loading PNG files and converting them to pygame surfaces with fallback support

import pygame
import os
from typing import Optional, Dict, Tuple

from Config import Config


class AssetLoader:
    """Loads and caches PNG assets, converts them to pygame surfaces"""
    
    def __init__(self):
        self.cache: Dict[Tuple[str, int], Optional[pygame.Surface]] = {}
        self.png_enabled = Config.USE_PNG_GRAPHICS
        
        if not Config.USE_PNG_GRAPHICS:
            print("PNG graphics disabled in configuration")
    
    def _load_png_to_surface(self, filepath: str, size: int) -> Optional[pygame.Surface]:
        """Load PNG file and convert to pygame surface at specified size"""
        if not self.png_enabled:
            return None
        
        # Check if file exists
        if not os.path.exists(filepath):
            return None
        
        try:
            # Load PNG file directly with pygame
            surface = pygame.image.load(filepath)
            
            # Scale to desired size
            surface = pygame.transform.scale(surface, (size, size))
            
            # Convert to display format for better performance
            surface = surface.convert_alpha()
            
            return surface
            
        except Exception as e:
            print(f"Warning: Failed to load PNG '{filepath}': {e}")
            return None
    
    def get_tile_sprite(self, terrain_type: str, size: int) -> Optional[pygame.Surface]:
        """Get tile sprite for terrain type, returns None if not available"""
        cache_key = (f"tile_{terrain_type}", size)
        
        # Check cache first
        if cache_key in self.cache:
            return self.cache[cache_key]
        
        # Try to load PNG
        if terrain_type in Config.TILE_PNG_PATHS:
            png_path = os.path.join(Config.ASSETS_DIR, Config.TILE_PNG_PATHS[terrain_type])
            surface = self._load_png_to_surface(png_path, size)
            self.cache[cache_key] = surface
            return surface
        
        # No PNG defined for this terrain
        self.cache[cache_key] = None
        return None
    
    def get_enemy_sprite(self, size: int) -> Optional[pygame.Surface]:
        """Get enemy sprite, returns None if not available"""
        cache_key = ("enemy", size)
        
        # Check cache first
        if cache_key in self.cache:
            return self.cache[cache_key]
        
        # Try to load PNG
        if 'enemy' in Config.ENTITY_PNG_PATHS:
            png_path = os.path.join(Config.ASSETS_DIR, Config.ENTITY_PNG_PATHS['enemy'])
            surface = self._load_png_to_surface(png_path, size)
            self.cache[cache_key] = surface
            return surface
        
        # No PNG defined
        self.cache[cache_key] = None
        return None
    
    def get_marker_sprite(self, marker_type: str, size: int) -> Optional[pygame.Surface]:
        """Get START or END marker sprite, returns None if not available"""
        cache_key = (f"marker_{marker_type}", size)
        
        # Check cache first
        if cache_key in self.cache:
            return self.cache[cache_key]
        
        # Try to load PNG
        if marker_type in Config.MARKER_PNG_PATHS:
            png_path = os.path.join(Config.ASSETS_DIR, Config.MARKER_PNG_PATHS[marker_type])
            surface = self._load_png_to_surface(png_path, size)
            self.cache[cache_key] = surface
            return surface
        
        # No PNG defined
        self.cache[cache_key] = None
        return None
    
    def clear_cache(self):
        """Clear the sprite cache (useful for reloading assets)"""
        self.cache.clear()
