# MapGen.py - Map Generation and Tile Management
# Handles terrain generation, START/END points, and tile properties

import pygame
import random
from collections import deque
from typing import List, Tuple

# Import Config from Config module
from Config import Config


class MapGenerator:
    """Generate realistic clustered terrain with continuous road paths"""
    
    def __init__(self, width: int, height: int):
        self.width = width
        self.height = height
        self.tiles = {}
        self.start_points: List[Tuple[int, int]] = []
        self.end_point: Tuple[int, int] = (width - 1, height - 1)
        self._generate()
    
    def _generate(self):
        """Generate complete map"""
        # Step 1: Initialize with grass
        for y in range(self.height):
            for x in range(self.width):
                self.tiles[(x, y)] = 'grass'
        
        # Step 2: Generate clustered terrain FIRST (forest, swamp, stone) - MORE FREQUENT & LARGER
        self._generate_clusters()
        
        # Step 3: Find valid START points (only on GRASS/FOREST, avoid SWAMP/STONE)
        self._generate_start_points()
        
        # Step 4: Generate curved road paths from START to END
        self._generate_road_paths()
        
        # Step 5: Ensure end is road, START can stay as terrain or become road
        self.tiles[self.end_point] = 'road'
        for start_x, start_y in self.start_points:
            terrain = self.tiles[(start_x, start_y)]
            if terrain == 'grass':
                self.tiles[(start_x, start_y)] = 'road'
            # If forest, keep as forest (enemy can spawn on forest)
    
    def _is_border_tile(self, x: int, y: int) -> bool:
        """Check if tile is on border (edge of map)"""
        return x == 0 or x == self.width - 1 or y == 0 or y == self.height - 1
    
    def _manhattan_distance(self, x1: int, y1: int, x2: int, y2: int) -> int:
        """Calculate Manhattan distance"""
        return abs(x1 - x2) + abs(y1 - y2)
    
    def _generate_clusters(self):
        """Generate clustered terrain - MORE FREQUENT and LARGER"""
        # FOREST clusters - INCREASED (6-7 clusters, larger size)
        num_forest_clusters = random.randint(6, 7)
        for _ in range(num_forest_clusters):
            cx = random.randint(2, self.width - 3)
            cy = random.randint(2, self.height - 3)
            self._grow_cluster(cx, cy, 'forest', size=random.randint(12, 20))
        
        # SWAMP clusters - INCREASED (5-6 clusters, larger size)
        num_swamp_clusters = random.randint(5, 6)
        for _ in range(num_swamp_clusters):
            cx = random.randint(2, self.width - 3)
            cy = random.randint(2, self.height - 3)
            self._grow_cluster(cx, cy, 'swamp', size=random.randint(10, 18), 
                             allow_terrain=['grass', 'forest'])  # Swamp only on grass/forest
        
        # STONE mountains - MUCH LARGER (4-5 clusters, 15-30 size)
        num_stone_clusters = random.randint(4, 5)
        for _ in range(num_stone_clusters):
            cx = random.randint(2, self.width - 3)
            cy = random.randint(2, self.height - 3)
            self._grow_cluster(cx, cy, 'stone', size=random.randint(15, 30), 
                             growth_probability=0.7)  # Higher growth for bigger mountains
    
    def _grow_cluster(self, start_x: int, start_y: int, terrain: str, size: int,
                      growth_probability: float = 0.6, allow_terrain: List[str] = None):
        """Grow a cluster of terrain using flood-fill style growth"""
        visited = set()
        queue = deque([(start_x, start_y)])
        visited.add((start_x, start_y))
        cluster_size = 0
        
        if allow_terrain is None:
            allow_terrain = ['grass', 'forest', 'swamp']  # Default: can grow on these
        
        while queue and cluster_size < size:
            x, y = queue.popleft()
            
            # Only place if within bounds
            if 0 <= x < self.width and 0 <= y < self.height:
                current_terrain = self.tiles[(x, y)]
                
                # Check if can place this terrain
                if current_terrain not in allow_terrain:
                    continue
                
                self.tiles[(x, y)] = terrain
                cluster_size += 1
                
                # Add neighbors with probability (creates organic shape)
                for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                    nx, ny = x + dx, y + dy
                    if (nx, ny) not in visited and random.random() < growth_probability:
                        visited.add((nx, ny))
                        queue.append((nx, ny))
    
    def _generate_start_points(self):
        """Generate 3 START points on BORDER, only on GRASS/FOREST, at least 8 tiles from END"""
        border_tiles = []
        
        # Collect all border tiles that are GRASS or FOREST (not SWAMP or STONE)
        for x in range(self.width):
            for y in range(self.height):
                if self._is_border_tile(x, y):
                    terrain = self.tiles[(x, y)]
                    # Only allow GRASS or FOREST
                    if terrain in ['grass', 'forest']:
                        distance = self._manhattan_distance(x, y, self.end_point[0], self.end_point[1])
                        if distance >= Config.MIN_START_END_DISTANCE:
                            border_tiles.append((x, y))
        
        # Randomly select 3 start points
        if len(border_tiles) >= Config.NUM_START_POINTS:
            self.start_points = random.sample(border_tiles, Config.NUM_START_POINTS)
        else:
            # If not enough valid border tiles, just pick as many as possible
            self.start_points = border_tiles[:Config.NUM_START_POINTS]
        
        print(f"Generated {len(self.start_points)} START points on valid terrain: {self.start_points}")
    
    def _generate_road_paths(self):
        """Generate curved road paths from each START to END"""
        for start_x, start_y in self.start_points:
            # Create continuous path using CURVED pathfinding
            path = self._find_road_path(start_x, start_y, self.end_point[0], self.end_point[1])
            
            # Place road on map
            for x, y in path:
                if 0 <= x < self.width and 0 <= y < self.height:
                    current_terrain = self.tiles[(x, y)]
                    
                    # Road can overwrite GRASS and FOREST (logical: build roads through them)
                    # Road CANNOT go through SWAMP or STONE
                    if current_terrain in ['grass', 'forest', 'road']:
                        self.tiles[(x, y)] = 'road'
                    else:
                        # Hit swamp or stone - this path ends here (will find alternate)
                        break
    
    def _find_road_path(self, start_x: int, start_y: int, end_x: int, end_y: int) -> List[Tuple[int, int]]:
        """Find CURVED path with randomized decisions"""
        visited = set()
        queue = deque([(start_x, start_y, [])])
        visited.add((start_x, start_y))
        
        max_iterations = self.width * self.height * 3
        iterations = 0
        
        # Random direction bias untuk curved roads
        direction_bias = random.choice([(1, 0), (-1, 0), (0, 1), (0, -1)])
        
        while queue and iterations < max_iterations:
            x, y, path = queue.popleft()
            iterations += 1
            path = path + [(x, y)]
            
            # Check if reached end
            if x == end_x and y == end_y:
                return path
            
            # Get neighbors dengan RANDOMIZED preference (untuk curved roads)
            neighbors = []
            for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                nx, ny = x + dx, y + dy
                if (0 <= nx < self.width and 0 <= ny < self.height and 
                    (nx, ny) not in visited):
                    
                    terrain = self.tiles[(nx, ny)]
                    
                    # Calculate preference
                    if terrain == 'grass':
                        preference = 0  # Prefer grass
                    elif terrain == 'road':
                        preference = 0.5  # Road merge point
                    elif terrain == 'forest':
                        preference = 1  # Can overwrite forest
                    elif terrain == 'swamp':
                        preference = 999  # AVOID swamp
                    else:  # stone
                        preference = 999  # AVOID stone
                    
                    # Add directional bias untuk curves
                    if (dx, dy) == direction_bias:
                        preference -= 0.3  # Prefer biased direction
                    
                    neighbors.append((preference, nx, ny))
            
            # RANDOMIZED path selection: 30% chance to pick random neighbor
            if neighbors:
                if random.random() < 0.3:
                    # Random choice - creates twists and turns
                    neighbor = random.choice(neighbors)
                    _, nx, ny = neighbor
                    if (nx, ny) not in visited:
                        visited.add((nx, ny))
                        queue.append((nx, ny, path))
                else:
                    # Optimal choice - sorted by preference
                    neighbors.sort()
                    for _, nx, ny in neighbors:
                        if (nx, ny) not in visited:
                            visited.add((nx, ny))
                            queue.append((nx, ny, path))
        
        # If no path found, return partial
        return [(start_x, start_y)]
    
    def get_tile(self, x: int, y: int) -> str:
        """Get terrain at position"""
        if 0 <= x < self.width and 0 <= y < self.height:
            return self.tiles.get((x, y), 'grass')
        return 'stone'


class Tile:
    """Map tile"""
    def __init__(self, x: int, y: int, terrain: str):
        self.x = x
        self.y = y
        self.terrain = terrain
        self.has_barricade = False
        self.base_cost = Config.TERRAIN_COSTS.get(terrain, 1)
    
    def get_cost(self) -> int:
        """Get movement cost"""
        if self.has_barricade:
            return self.base_cost + Config.BARRICADE_COST
        return self.base_cost
    
    def get_color(self) -> Tuple[int, int, int]:
        """Get tile color"""
        color = Config.TERRAIN_COLORS.get(self.terrain, Config.TERRAIN_COLORS['grass'])
        if self.has_barricade:
            return tuple(int(c * 0.5) for c in color)
        return color
