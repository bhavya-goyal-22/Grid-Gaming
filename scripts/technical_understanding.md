# Grid Gaming Algorithms Explanation

## Overview
This document explains how the pathfinding algorithms work in the Grid Gaming project, including the cost function, heuristic, and algorithm implementations.

## Grid Environment
- **6x6 grid** with buildings (B) and roadblocks (X)
- **Buildings**: {(1,0), (3,0), (3,5), (5,1)} - provide safety bonus
- **Roadblocks**: {(0,2), (0,3), (1,2), (2,4), (3,2), (5,3)} - cause safety penalty
- **Movement**: Only 4-directional (no diagonal)

## Points Cost Function

### Safety Scoring System
- **+5 points**: For each adjacent building (safety bonus)
- **-3 points**: For each adjacent roadblock (safety penalty)

### Example Calculation
For position (2,1):
- Adjacent positions: (1,1), (3,1), (2,0), (2,2)
- Check each adjacent position:
  - (1,1): Empty → 0 points
  - (3,1): Empty → 0 points  
  - (2,0): Empty → 0 points
  - (2,2): Has roadblock → -3 points
- **Total points for (2,1) = -3 points**

For position (2,0):
- Adjacent positions: (1,0), (3,0), (2,1)
- Check each adjacent position:
  - (1,0): Has building → +5 points
  - (3,0): Has building → +5 points
  - (2,1): Empty → 0 points
- **Total points for (2,0) = +10 points**

## Heuristic Function

### Manhattan Distance
Used to estimate distance to goal without considering obstacles.

**Formula**: h(n) = |current_row - goal_row| + |current_col - goal_col|

### Example
If goal is at (5,5):
- h((0,0)) = |0-5| + |0-5| = 10
- h((2,3)) = |2-5| + |3-5| = 3 + 2 = 5
- h((4,5)) = |4-5| + |5-5| = 1 + 0 = 1

## A* Algorithm

### How it Works
1. **f(n) = g(n) + h(n)**
   - g(n) = actual cost from start
   - h(n) = heuristic cost to goal
2. Always expands node with lowest f(n)
3. Guarantees optimal path with admissible heuristic

### Example Step-by-Step
Start: (0,0), Goal: (0,4)

**Step 1**: Start at (0,0)
- g(0,0) = 0, h(0,0) = 4, f(0,0) = 4

**Step 2**: Expand (0,0), add neighbors
- (1,0): g=1, h=5, f=6 (but blocked by building)
- (0,1): g=1, h=3, f=4 ✓

**Step 3**: Expand (0,1)
- (0,2): g=2, h=2, f=4 (but blocked by roadblock)
- (1,1): g=2, h=4, f=6 ✓

Continue until goal reached...

**Final Path**: (0,0) → (1,1) → (1,2) → ... → (0,4)
- **Path Cost**: 8 moves
- **Safety Points**: Sum of points at each position
- **Total f-cost**: Optimal solution found

## IDDFS Algorithm

### How it Works
1. **Depth-limited search** with increasing depth limits
2. **Space efficient**: O(d) memory usage
3. Finds **first solution** at minimum depth (not necessarily optimal)

### Example Step-by-Step
Start: (0,0), Goal: (0,4)

**Iteration 1 (Depth = 1)**:
- Explore: (0,0) only
- Result: Goal not found

**Iteration 2 (Depth = 2)**:
- Explore: (0,0) → (0,1), (1,0)
- Result: Goal not found

**Iteration 3 (Depth = 3)**:
- Explore: (0,0) → (0,1) → (1,1)
- Explore: (0,0) → (0,1) → (0,2) [blocked]
- Result: Goal not found

Continue until solution found...

**Final Path**: First valid path found (may not be optimal)
- **Path Cost**: Variable (depends on first solution found)
- **Safety Points**: Calculated after path discovery
- **Memory Used**: Only current path stored

## Algorithm Comparison

| Feature | A* | IDDFS |
|---------|----|----|
| **Optimality** | ✅ Guaranteed optimal | ❌ First solution found |
| **Memory Usage** | O(b^d) - exponential | O(d) - linear |
| **Time Complexity** | O(b^d) | O(b^d) |
| **Heuristic Required** | ✅ Yes (Manhattan) | ❌ No |
| **Best For** | Optimal solutions | Memory-constrained |

## Example Results

### A* Result
```
Path: [(0,0), (1,1), (2,1), (2,2), (2,3), (1,4), (0,4)]
Total Points: +12 (safety bonuses/penalties)
Number of Squares: 7
```

### IDDFS Result  
```
Path: [(0,0), (1,1), (1,2), (1,3), (1,4), (0,4)]
Total Points: -6 (different path, different points)
Number of Squares: 6
```

## Key Takeaways

1. **A*** finds the optimal path using heuristic guidance
2. **IDDFS** finds a valid path using minimal memory
3. **Safety points** are calculated based on adjacency to buildings/roadblocks
4. **Manhattan distance** provides admissible heuristic for A*
5. **Choice depends** on whether you prioritize optimality or memory efficiency
