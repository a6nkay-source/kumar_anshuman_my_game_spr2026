import heapq # Used for the A* pathfinding algorithm
from settings import * 
import random
# I am using A* pathfinding for the enemies 
# to find the player, and this is the implementation of it.
# I referenced the A* algorithm from Red Blob Games, but I heavily modified it to fit the needs of my game. 
# The A* algorithm is a popular pathfinding algorithm that is used to find the shortest path between two points in a grid. 
# It uses a function to estimate the cost of reaching the goal from a given node, and it uses a priority postion to 
# estimate the distance between 2 coordinate points 


class Node:
    def __init__(self, pos, g_cost=0, h_cost=0, parent=None):
        self.pos = pos  # (x, y) grid position
        self.g_cost = g_cost  # Cost from start
        self.h_cost = h_cost    
        self.parent = parent
    
    def f_cost(self):
        return self.g_cost + self.h_cost
    
    def __lt__(self, other):
        return self.f_cost() < other.f_cost()
    
    def __eq__(self, other):
        return self.pos == other.pos # The different nodes are equal if they are at the same position
    
    def __hash__(self):
        return hash(self.pos)


def heuristic(pos1, pos2): # distance between 2 point in grid
    return abs(pos1[0] - pos2[0]) + abs(pos1[1] - pos2[1])


def get_neighbors(pos, map_data): # Get walkable tiles adjacent to the current tile
    x, y = pos
    neighbors = []
    
    # Check all directions 
    for dx, dy in [(0, 1), (0, -1), (1, 0), (-1, 0)]: 
        nx, ny = x + dx, y + dy
        
        # Check bounds
        if 0 <= ny < len(map_data) and 0 <= nx < len(map_data[0]): # Check if the map is within bounds
            # Check if not a wall
            if map_data[ny][nx] != '1':
                neighbors.append((nx, ny))
    
    return neighbors


def astar_pathfind(start_pos, goal_pos, map_data, max_iterations=1000):
   
    if start_pos == goal_pos:
        return []
    
    # Convert pixel positions to grid positions, rounding to the nearest tile
    start_grid = (int(round(start_pos[0] / TILESIZE)), int(round(start_pos[1] / TILESIZE))) # Converts pixel position to grid position
    goal_grid = (int(round(goal_pos[0] / TILESIZE)), int(round(goal_pos[1] / TILESIZE))) # Converts pixel position to grid position
    
    # Check if goal is walkable
    if goal_grid[1] < len(map_data) and goal_grid[0] < len(map_data[0]): # This checks if the goal is within bounds
        if map_data[goal_grid[1]][goal_grid[0]] == '1':
            return []
    else:
        return []
    
    open_list = []
    closed_set = set()
    
    start_node = Node(start_grid, 0, heuristic(start_grid, goal_grid))
    heapq.heappush(open_list, start_node)
    
    iterations = 0
    while open_list and iterations < max_iterations:
        iterations += 1
        current = heapq.heappop(open_list)
        
        if current.pos == goal_grid:
            # Reconstruct path
            path = []
            node = current
            while node:
                path.append(node.pos)
                node = node.parent
            path.reverse()
            # Convert back to pixel coordinates (tile center), exclude start position
            pixel_path = [(x * TILESIZE + TILESIZE // 2, y * TILESIZE + TILESIZE // 2) for x, y in path[1:]]
            return pixel_path
        
        closed_set.add(current.pos)
        
        for neighbor_pos in get_neighbors(current.pos, map_data):
            if neighbor_pos in closed_set:
                continue
            
            g_cost = current.g_cost + 1
            h_cost = heuristic(neighbor_pos, goal_grid)
            
            neighbor = Node(neighbor_pos, g_cost, h_cost, parent=current)
            
            # Check if this node is already in open_list with higher cost
            existing = None
            for node in open_list:
                if node.pos == neighbor_pos: 
                    existing = node
                    break
            
            if existing is None: # This is if the neighbor is not in the open list.
                heapq.heappush(open_list, neighbor)
            elif g_cost < existing.g_cost:
                existing.g_cost = g_cost # This updates the exisisting cost
                existing.parent = current # This updates the exsiisting parent
                heapq.heapify(open_list)
    
    return []  # No path found
# Health bar function used to draw it

    return False

