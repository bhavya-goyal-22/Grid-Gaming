"""
Pathfinding Game Backend
Contains the core algorithms and game logic for the grid-based pathfinding game.
"""

import heapq
import time
from typing import List, Tuple, Dict, Optional, Set
import numpy as np


class GridGameEngine:
    """Core game engine for pathfinding algorithms"""
    
    def __init__(self, grid_size=(6, 6)):
        self.GRID_SIZE = grid_size
        self.GRID_H, self.GRID_W = grid_size
        
        # Cell types
        self.EMPTY = 0
        self.BUILDING = 1
        self.ROADBLOCK = 2
        self.START = 3
        self.GOAL = 4
        
        # Movement directions (no diagonal)
        self.DELTAS = [(-1, 0), (1, 0), (0, -1), (0, 1)]
        
        # Scoring system
        self.ADJ_BONUS_BUILDING = 5
        self.ADJ_PENALTY_ROADBLOCK = 3
        
        # Default obstacles
        self.default_buildings = {(1, 0), (3, 0), (3, 5), (5, 1)}
        self.default_roadblocks = {(0, 2), (0, 3), (1, 2), (2, 4), (3, 2), (5, 3)}
        
        # Game state
        self.reset_game()
    
    def reset_game(self):
        """Reset game to initial state"""
        self.buildings = self.default_buildings.copy()
        self.roadblocks = self.default_roadblocks.copy()
        self.start_pos = None
        self.goal_pos = None
        self.grid = np.zeros(self.GRID_SIZE, dtype=int)
        self.setup_grid()
        
        # Algorithm results
        self.last_a_star_result = None
        self.last_iddfs_result = None
        self.last_complexity_stats = {}
    
    def setup_grid(self):
        """Setup the visual grid representation"""
        self.grid.fill(self.EMPTY)
        
        for pos in self.buildings:
            if self.is_valid_position(pos):
                self.grid[pos] = self.BUILDING
                
        for pos in self.roadblocks:
            if self.is_valid_position(pos):
                self.grid[pos] = self.ROADBLOCK
    
    def is_valid_position(self, pos):
        """Check if position is within grid bounds"""
        r, c = pos
        return 0 <= r < self.GRID_H and 0 <= c < self.GRID_W
    
    def is_position_free(self, pos):
        """Check if position is free (not occupied by obstacles)"""
        return (self.is_valid_position(pos) and 
                pos not in self.buildings and 
                pos not in self.roadblocks)
    
    def get_available_positions(self):
        """Get all positions that can be used for start/goal"""
        available = []
        for r in range(self.GRID_H):
            for c in range(self.GRID_W):
                pos = (r, c)
                if self.is_position_free(pos):
                    available.append(pos)
        return available
    
    def set_start_goal(self, start_pos, goal_pos):
        """Set start and goal positions"""
        if not self.is_position_free(start_pos):
            raise ValueError(f"Start position {start_pos} is not available")
        if not self.is_position_free(goal_pos):
            raise ValueError(f"Goal position {goal_pos} is not available")
        if start_pos == goal_pos:
            raise ValueError("Start and goal positions cannot be the same")
            
        self.start_pos = start_pos
        self.goal_pos = goal_pos
        
        # Update visual grid
        self.setup_grid()
        self.grid[start_pos] = self.START
        self.grid[goal_pos] = self.GOAL
    
    def manhattan_distance(self, pos1, pos2):
        """Calculate Manhattan distance between two positions"""
        return abs(pos1[0] - pos2[0]) + abs(pos1[1] - pos2[1])
    
    def calculate_position_points(self, pos):
        """Calculate safety points for a position based on adjacency"""
        points = 0
        for dr, dc in self.DELTAS:
            adj_pos = (pos[0] + dr, pos[1] + dc)
            if adj_pos in self.buildings:
                points += self.ADJ_BONUS_BUILDING
            if adj_pos in self.roadblocks:
                points -= self.ADJ_PENALTY_ROADBLOCK
        return points
    
    def build_transitions(self):
        """Build transition matrix and heuristics"""
        if not self.start_pos or not self.goal_pos:
            raise ValueError("Start and goal positions must be set first")
            
        transitions = {}
        h_vals = {}
        position_points = {}
        
        for r in range(self.GRID_H):
            for c in range(self.GRID_W):
                pos = (r, c)
                if not self.is_position_free(pos) and pos != self.start_pos and pos != self.goal_pos:
                    continue
                
                # Find valid neighbors
                neighbors = []
                for dr, dc in self.DELTAS:
                    new_pos = (r + dr, c + dc)
                    if (self.is_position_free(new_pos) or new_pos == self.goal_pos):
                        neighbors.append((new_pos, 1.0))  # uniform cost
                
                transitions[pos] = neighbors
                h_vals[pos] = self.manhattan_distance(pos, self.goal_pos)
                position_points[pos] = self.calculate_position_points(pos)
        
        return transitions, h_vals, position_points
    
    def a_star_search(self):
        """A* search algorithm with performance tracking"""
        if not self.start_pos or not self.goal_pos:
            raise ValueError("Start and goal positions must be set")
        
        start_time = time.time()
        transitions, h_vals, position_points = self.build_transitions()
        
        frontier = [(h_vals[self.start_pos], 0, self.start_pos, [self.start_pos])]
        visited = {}
        
        # Performance tracking
        nodes_expanded = 0
        max_frontier_size = 0
        nodes_generated = 0
        
        while frontier:
            max_frontier_size = max(max_frontier_size, len(frontier))
            f, g, node, path = heapq.heappop(frontier)
            nodes_expanded += 1
            
            if node == self.goal_pos:
                end_time = time.time()
                
                # Calculate path points
                total_points = sum(position_points.get(pos, 0) for pos in path)
                
                result = {
                    'path': path,
                    'total_points': total_points,
                    'path_length': len(path),
                    'algorithm': 'A*',
                    'execution_time': end_time - start_time,
                    'nodes_expanded': nodes_expanded,
                    'nodes_generated': nodes_generated,
                    'max_frontier_size': max_frontier_size,
                    'optimal': True
                }
                
                self.last_a_star_result = result
                return result
            
            if node in visited and visited[node] <= g:
                continue
            visited[node] = g
            
            for neighbor, cost in transitions.get(node, []):
                nodes_generated += 1
                new_g = g + cost
                new_f = new_g + h_vals[neighbor]
                heapq.heappush(frontier, (new_f, new_g, neighbor, path + [neighbor]))
        
        # No path found
        result = {
            'path': None,
            'total_points': 0,
            'path_length': 0,
            'algorithm': 'A*',
            'execution_time': time.time() - start_time,
            'nodes_expanded': nodes_expanded,
            'nodes_generated': nodes_generated,
            'max_frontier_size': max_frontier_size,
            'optimal': True,
            'error': 'No path found'
        }
        
        self.last_a_star_result = result
        return result
    
    def iddfs_search(self, max_depth=50):
        """Iterative Deepening Depth-First Search with performance tracking"""
        if not self.start_pos or not self.goal_pos:
            raise ValueError("Start and goal positions must be set")
        
        start_time = time.time()
        transitions, h_vals, position_points = self.build_transitions()
        
        # Performance tracking
        total_nodes_expanded = 0
        total_nodes_generated = 0
        max_depth_reached = 0
        iterations = 0
        
        def dls(node, depth, path, visited, current_depth):
            nonlocal total_nodes_expanded, total_nodes_generated, max_depth_reached
            
            total_nodes_expanded += 1
            max_depth_reached = max(max_depth_reached, current_depth)
            
            if node == self.goal_pos:
                return path
            if depth <= 0:
                return None
            
            for neighbor, _ in transitions.get(node, []):
                total_nodes_generated += 1
                if neighbor not in visited:
                    visited.add(neighbor)
                    result = dls(neighbor, depth - 1, path + [neighbor], visited, current_depth + 1)
                    if result:
                        return result
                    visited.remove(neighbor)
            return None
        
        for depth in range(1, max_depth + 1):
            iterations += 1
            visited = {self.start_pos}
            path = dls(self.start_pos, depth, [self.start_pos], visited, 0)
            
            if path:
                end_time = time.time()
                
                # Calculate path points
                total_points = sum(position_points.get(pos, 0) for pos in path)
                
                result = {
                    'path': path,
                    'total_points': total_points,
                    'path_length': len(path),
                    'algorithm': 'IDDFS',
                    'execution_time': end_time - start_time,
                    'nodes_expanded': total_nodes_expanded,
                    'nodes_generated': total_nodes_generated,
                    'max_depth_reached': max_depth_reached,
                    'iterations': iterations,
                    'optimal': False
                }
                
                self.last_iddfs_result = result
                return result
        
        # No path found
        result = {
            'path': None,
            'total_points': 0,
            'path_length': 0,
            'algorithm': 'IDDFS',
            'execution_time': time.time() - start_time,
            'nodes_expanded': total_nodes_expanded,
            'nodes_generated': total_nodes_generated,
            'max_depth_reached': max_depth_reached,
            'iterations': iterations,
            'optimal': False,
            'error': f'No path found within depth limit {max_depth}'
        }
        
        self.last_iddfs_result = result
        return result
    
    def compare_algorithms(self):
        """Run both algorithms and compare results"""
        results = {}
        
        # Run A*
        try:
            results['astar'] = self.a_star_search()
        except Exception as e:
            results['astar'] = {'error': str(e)}
        
        # Run IDDFS
        try:
            results['iddfs'] = self.iddfs_search()
        except Exception as e:
            results['iddfs'] = {'error': str(e)}
        
        return results
    
    def get_grid_analysis(self):
        """Get comprehensive grid analysis data"""
        if not self.start_pos or not self.goal_pos:
            return None
        
        transitions, h_vals, position_points = self.build_transitions()
        
        analysis = {
            'grid_layout': self.grid.copy(),
            'heuristic_values': h_vals,
            'position_points': position_points,
            'transitions': transitions,
            'available_positions': self.get_available_positions(),
            'buildings': list(self.buildings),
            'roadblocks': list(self.roadblocks),
            'start_pos': self.start_pos,
            'goal_pos': self.goal_pos
        }
        
        return analysis


# Game utility functions
def format_result_summary(result):
    """Format algorithm result for display"""
    if 'error' in result:
        return f"❌ {result['algorithm']}: {result['error']}"
    
    summary = f"✅ {result['algorithm']} Results:\n"
    summary += f"  • Path Length: {result['path_length']} squares\n"
    summary += f"  • Safety Points: {result['total_points']}\n"
    summary += f"  • Execution Time: {result['execution_time']:.4f}s\n"
    summary += f"  • Nodes Expanded: {result['nodes_expanded']}\n"
    
    if result['algorithm'] == 'IDDFS':
        summary += f"  • Iterations: {result['iterations']}\n"
        summary += f"  • Max Depth: {result['max_depth_reached']}\n"
    else:
        summary += f"  • Max Frontier Size: {result['max_frontier_size']}\n"
    
    return summary


def create_random_game(engine, difficulty='medium'):
    """Create a random game setup"""
    import random
    
    available = engine.get_available_positions()
    if len(available) < 2:
        raise ValueError("Not enough free positions for start and goal")
    
    # Select random start and goal
    start = random.choice(available)
    available.remove(start)
    goal = random.choice(available)
    
    engine.set_start_goal(start, goal)
    
    # Add some random obstacles based on difficulty
    if difficulty == 'easy':
        pass  # Use default obstacles
    elif difficulty == 'medium':
        # Add 1-2 random roadblocks
        free_positions = [pos for pos in engine.get_available_positions() 
                         if pos != start and pos != goal]
        if free_positions:
            new_roadblock = random.choice(free_positions)
            engine.roadblocks.add(new_roadblock)
    elif difficulty == 'hard':
        # Add 2-3 random obstacles
        free_positions = [pos for pos in engine.get_available_positions() 
                         if pos != start and pos != goal]
        for _ in range(min(3, len(free_positions))):
            if free_positions:
                new_obstacle = random.choice(free_positions)
                free_positions.remove(new_obstacle)
                if random.choice([True, False]):
                    engine.buildings.add(new_obstacle)
                else:
                    engine.roadblocks.add(new_obstacle)
    
    engine.setup_grid()
    engine.grid[start] = engine.START
    engine.grid[goal] = engine.GOAL
    
    return start, goal
