# Handles pathfinding for enemy navigation using A* algorithm
import heapq
from typing import List, Tuple, Optional, Dict

# Import Config and MapGenerator from other modules
from Config import Config
from MapGen import MapGenerator


class Node:
    """Node for A* algorithm - represents a single tile in the pathfinding grid"""
    def __init__(self, x: int, y: int, cost: int = 1):
        self.x = x  # X coordinate on the grid
        self.y = y  # Y coordinate on the grid
        self.cost = cost  # Movement cost to enter this tile (based on terrain type)
        
        # A* algorithm values
        self.g = float('inf')  # Cost from start to this node
        self.h = 0  # Heuristic cost from this node to goal
        self.f = float('inf')  # Total cost (f = g + h)
        self.parent = None  # Previous node in the path (for backtracking)
    
    def __lt__(self, other):
        """Compare nodes by f-cost for priority queue"""
        return self.f < other.f
    
    def __eq__(self, other):
        """Nodes are equal if they have the same coordinates"""
        if isinstance(other, Node):
            return self.x == other.x and self.y == other.y
        return False
    
    def __hash__(self):
        """Hash by coordinates for set/dict usage"""
        return hash((self.x, self.y))
    
    def reset(self):
        """Reset node values for a new pathfinding search"""
        self.g = float('inf')
        self.h = 0
        self.f = float('inf')
        self.parent = None


class Pathfinder:
    """A* algorithm implementation for grid-based pathfinding"""
    def __init__(self, width: int, height: int, map_gen: MapGenerator):
        self.width = width
        self.height = height
        self.map_gen = map_gen
        self.nodes: Dict[Tuple[int, int], Node] = {}
        
        # Performance metrics
        self.nodes_expanded = 0  # Number of nodes processed
        self.nodes_evaluated = 0  # Number of neighbor evaluations
        self.last_path_length = 0  # Length of the last found path
        
        # Initialize nodes for every tile in the grid
        for x in range(width):
            for y in range(height):
                terrain = map_gen.get_tile(x, y)
                # Get movement cost from config (100 = impassable)
                cost = Config.TERRAIN_COSTS.get(terrain, 100)
                self.nodes[(x, y)] = Node(x, y, cost)
    
    def update_cost(self, x: int, y: int, cost: int):
        """Update terrain cost for a specific tile (e.g., when terrain changes)"""
        if (x, y) in self.nodes:
            self.nodes[(x, y)].cost = cost
    
    def is_walkable(self, x: int, y: int) -> bool:
        """Check if a tile is walkable (within bounds and cost < 100)"""
        # Check if coordinates are within the grid
        if not (0 <= x < self.width and 0 <= y < self.height):
            return False
        # Cost of 100 or higher means impassable terrain
        return self.nodes[(x, y)].cost < 100
    
    def _manhattan(self, x1: int, y1: int, x2: int, y2: int) -> int:
        """Manhattan distance heuristic (sum of horizontal and vertical distance)"""
        return abs(x1 - x2) + abs(y1 - y2)
    
    def _neighbors(self, x: int, y: int) -> List[Tuple[int, int]]:
        """Get 4-directional neighbors (up, down, left, right)"""
        neighbors = []
        # Check all four cardinal directions
        for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            nx, ny = x + dx, y + dy
            if self.is_walkable(nx, ny):
                neighbors.append((nx, ny))
        return neighbors
    
    def _reset_nodes(self):
        """Reset all nodes before starting a new pathfinding search"""
        for node in self.nodes.values():
            node.reset()
    
    def find_path(self, start: Tuple[int, int], goal: Tuple[int, int]) -> Optional[List[Tuple[int, int]]]:
        """
        Find shortest path from start to goal using A* algorithm
        Returns list of (x, y) coordinates or None if no path exists
        """
        # Validate that both start and goal positions are walkable
        if not self.is_walkable(start[0], start[1]) or not self.is_walkable(goal[0], goal[1]):
            return None
        
        # Reset all nodes from previous searches
        self._reset_nodes()
        
        # Initialize start node
        start_node = self.nodes[start]
        start_node.g = 0  # No cost to reach starting position
        start_node.h = self._manhattan(start[0], start[1], goal[0], goal[1])
        start_node.f = start_node.h  # f = g + h
        
        # Priority queue of nodes to explore (ordered by f-cost)
        open_list = [start_node]
        open_set = {start}  # Fast lookup for nodes in open list
        closed_set = set()  # Nodes already fully explored
        
        # Reset performance counters
        self.nodes_expanded = 0
        self.nodes_evaluated = 0
        
        # Main A* loop
        while open_list:
            # Get node with lowest f-cost
            current = heapq.heappop(open_list)
            open_set.discard((current.x, current.y))
            closed_set.add((current.x, current.y))
            self.nodes_expanded += 1
            
            # Check if we've reached the goal
            if current.x == goal[0] and current.y == goal[1]:
                # Reconstruct path by following parent pointers
                path = []
                node = current
                while node:
                    path.append((node.x, node.y))
                    node = node.parent
                path.reverse()  # Path was built backwards, so reverse it
                self.last_path_length = len(path)
                return path
            
            # Explore all neighbors of current node
            for nx, ny in self._neighbors(current.x, current.y):
                # Skip if already fully explored
                if (nx, ny) in closed_set:
                    continue
                
                neighbor = self.nodes[(nx, ny)]
                # Calculate cost to reach neighbor through current node
                tentative_g = current.g + neighbor.cost
                self.nodes_evaluated += 1
                
                # If this path to neighbor is better than any previous one
                if (nx, ny) not in open_set or tentative_g < neighbor.g:
                    # Update neighbor with better path
                    neighbor.parent = current
                    neighbor.g = tentative_g
                    neighbor.h = self._manhattan(nx, ny, goal[0], goal[1])
                    neighbor.f = neighbor.g + neighbor.h
                    
                    # Add to open list if not already there
                    if (nx, ny) not in open_set:
                        heapq.heappush(open_list, neighbor)
                        open_set.add((nx, ny))
        
        # No path found (open list is empty and goal wasn't reached)
        return None