# Pathfinding.py - A* Pathfinding Algorithm
# Handles pathfinding for enemy navigation

import heapq
from typing import List, Tuple, Optional, Dict

# Import Config and MapGenerator from other modules
from Config import Config
from MapGen import MapGenerator


class Node:
    """Node untuk A* algorithm"""
    def __init__(self, x: int, y: int, cost: int = 1):
        self.x = x
        self.y = y
        self.cost = cost
        self.g = float('inf')
        self.h = 0
        self.f = float('inf')
        self.parent = None
    
    def __lt__(self, other):
        return self.f < other.f
    
    def __eq__(self, other):
        if isinstance(other, Node):
            return self.x == other.x and self.y == other.y
        return False
    
    def __hash__(self):
        return hash((self.x, self.y))
    
    def reset(self):
        self.g = float('inf')
        self.h = 0
        self.f = float('inf')
        self.parent = None


class Pathfinder:
    """Implementasi A* algorithm"""
    def __init__(self, width: int, height: int, map_gen: MapGenerator):
        self.width = width
        self.height = height
        self.map_gen = map_gen
        self.nodes: Dict[Tuple[int, int], Node] = {}
        self.nodes_expanded = 0
        self.nodes_evaluated = 0
        self.last_path_length = 0
        
        for x in range(width):
            for y in range(height):
                terrain = map_gen.get_tile(x, y)
                cost = Config.TERRAIN_COSTS.get(terrain, 100)
                self.nodes[(x, y)] = Node(x, y, cost)
    
    def update_cost(self, x: int, y: int, cost: int):
        """Update terrain cost"""
        if (x, y) in self.nodes:
            self.nodes[(x, y)].cost = cost
    
    def is_walkable(self, x: int, y: int) -> bool:
        """Check walkable"""
        if not (0 <= x < self.width and 0 <= y < self.height):
            return False
        return self.nodes[(x, y)].cost < 100
    
    def _manhattan(self, x1: int, y1: int, x2: int, y2: int) -> int:
        """Manhattan distance heuristic"""
        return abs(x1 - x2) + abs(y1 - y2)
    
    def _neighbors(self, x: int, y: int) -> List[Tuple[int, int]]:
        """Get 4-directional neighbors"""
        neighbors = []
        for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            nx, ny = x + dx, y + dy
            if self.is_walkable(nx, ny):
                neighbors.append((nx, ny))
        return neighbors
    
    def _reset_nodes(self):
        """Reset all nodes"""
        for node in self.nodes.values():
            node.reset()
    
    def find_path(self, start: Tuple[int, int], goal: Tuple[int, int]) -> Optional[List[Tuple[int, int]]]:
        """A* pathfinding"""
        if not self.is_walkable(start[0], start[1]) or not self.is_walkable(goal[0], goal[1]):
            return None
        
        self._reset_nodes()
        start_node = self.nodes[start]
        start_node.g = 0
        start_node.h = self._manhattan(start[0], start[1], goal[0], goal[1])
        start_node.f = start_node.h
        
        open_list = [start_node]
        open_set = {start}
        closed_set = set()
        
        self.nodes_expanded = 0
        self.nodes_evaluated = 0
        
        while open_list:
            current = heapq.heappop(open_list)
            open_set.discard((current.x, current.y))
            closed_set.add((current.x, current.y))
            self.nodes_expanded += 1
            
            if current.x == goal[0] and current.y == goal[1]:
                path = []
                node = current
                while node:
                    path.append((node.x, node.y))
                    node = node.parent
                path.reverse()
                self.last_path_length = len(path)
                return path
            
            for nx, ny in self._neighbors(current.x, current.y):
                if (nx, ny) in closed_set:
                    continue
                
                neighbor = self.nodes[(nx, ny)]
                tentative_g = current.g + neighbor.cost
                self.nodes_evaluated += 1
                
                if (nx, ny) not in open_set or tentative_g < neighbor.g:
                    neighbor.parent = current
                    neighbor.g = tentative_g
                    neighbor.h = self._manhattan(nx, ny, goal[0], goal[1])
                    neighbor.f = neighbor.g + neighbor.h
                    
                    if (nx, ny) not in open_set:
                        heapq.heappush(open_list, neighbor)
                        open_set.add((nx, ny))
        
        return None
