"""
Pathfinding Game Application
A simple GUI game for visualizing pathfinding algorithms using tkinter.
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.patches import Rectangle, Circle
import numpy as np
from pathfinding_backend import GridGameEngine, format_result_summary, create_random_game


class PathfindingGameApp:
    def __init__(self, root):
        self.root = root
        self.root.title("AI Pathfinding Game - A* vs IDDFS")
        self.root.geometry("1400x800")
        self.root.configure(bg='#f0f0f0')
        
        # Initialize game engine
        self.engine = GridGameEngine()
        
        # Game state
        self.mode = "set_start"  # "set_start", "set_goal", "play"
        self.selected_algorithm = "both"
        
        # UI setup
        self.setup_ui()
        self.update_display()
        
    def setup_ui(self):
        """Setup the user interface"""
        # Main container
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(1, weight=1)
        
        # Control Panel (Left)
        self.setup_control_panel(main_frame)
        
        # Game Grid (Center)
        self.setup_game_grid(main_frame)
        
        # Results Panel (Right)
        self.setup_results_panel(main_frame)
        
    def setup_control_panel(self, parent):
        """Setup the control panel"""
        control_frame = ttk.LabelFrame(parent, text="Game Controls", padding="10")
        control_frame.grid(row=0, column=0, rowspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(0, 10))
        
        # Mode indicator
        self.mode_label = ttk.Label(control_frame, text="Click to set START position", 
                                   font=('Arial', 12, 'bold'), foreground='green')
        self.mode_label.grid(row=0, column=0, columnspan=2, pady=(0, 10))
        
        # Position display
        ttk.Label(control_frame, text="Current Positions:").grid(row=1, column=0, sticky=tk.W)
        self.position_label = ttk.Label(control_frame, text="Start: None\nGoal: None")
        self.position_label.grid(row=2, column=0, columnspan=2, sticky=tk.W, pady=(0, 10))
        
        # Algorithm selection
        ttk.Label(control_frame, text="Algorithm:").grid(row=3, column=0, sticky=tk.W)
        self.algorithm_var = tk.StringVar(value="both")
        algorithm_combo = ttk.Combobox(control_frame, textvariable=self.algorithm_var,
                                     values=["both", "A*", "IDDFS"], state="readonly", width=15)
        algorithm_combo.grid(row=4, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # Action buttons with animated effects
        self.run_button = ttk.Button(control_frame, text="► Run Pathfinding", 
                                   command=self.run_algorithms_animated, state='disabled')
        self.run_button.grid(row=5, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=2)
        
        ttk.Button(control_frame, text="⚂ Random Game", 
                  command=self.create_random_game_animated).grid(row=6, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=2)
        
        ttk.Button(control_frame, text="↻ Reset Game", 
                  command=self.reset_game_animated).grid(row=7, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=2)
        
        self.analysis_button = ttk.Button(control_frame, text="▣ Show Analysis", 
                  command=self.show_analysis, state='disabled')
        self.analysis_button.grid(row=8, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=2)
        
        # Separator
        ttk.Separator(control_frame, orient='horizontal').grid(row=9, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=10)
        
        # Legend
        ttk.Label(control_frame, text="Legend:", font=('Arial', 10, 'bold')).grid(row=10, column=0, sticky=tk.W)
        legend_frame = ttk.Frame(control_frame)
        legend_frame.grid(row=11, column=0, columnspan=2, sticky=(tk.W, tk.E))
        
        legends = [
            ("■ Start", "green"),
            ("■ Goal", "red"),
            ("■ Building (+5 pts)", "brown"),
            ("■ Roadblock (-3 pts)", "orange"),
            ("□ Empty", "lightgray"),
            ("● Path", "blue")
        ]
        
        for i, (text, color) in enumerate(legends):
            ttk.Label(legend_frame, text=text, font=('Arial', 9)).grid(row=i, column=0, sticky=tk.W, pady=1)
        
        # Add quit instruction
        ttk.Separator(legend_frame, orient='horizontal').grid(row=len(legends), column=0, sticky=(tk.W, tk.E), pady=5)
        ttk.Label(legend_frame, text="Press 'Q' to quit game", font=('Arial', 9, 'italic'), 
                 foreground='darkred').grid(row=len(legends)+1, column=0, sticky=tk.W, pady=1)
        
    def setup_game_grid(self, parent):
        """Setup the interactive game grid"""
        grid_frame = ttk.LabelFrame(parent, text="Interactive Grid (Click to set positions)", padding="10")
        grid_frame.grid(row=0, column=1, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Create matplotlib figure for the grid
        self.fig, self.ax = plt.subplots(1, 1, figsize=(8, 8))
        self.canvas = FigureCanvasTkAgg(self.fig, grid_frame)
        self.canvas.get_tk_widget().grid(row=0, column=0)
        
        # Bind click events
        self.canvas.mpl_connect('button_press_event', self.on_grid_click)
        
        # Bind key press events for quit functionality
        self.canvas.mpl_connect('key_press_event', self.on_key_press)
        self.canvas.get_tk_widget().focus_set()  # Enable key events
        
    def setup_results_panel(self, parent):
        """Setup the results display panel"""
        results_frame = ttk.LabelFrame(parent, text="Algorithm Results", padding="10")
        results_frame.grid(row=0, column=2, rowspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(10, 0))
        results_frame.columnconfigure(0, weight=1)
        results_frame.rowconfigure(0, weight=1)
        
        # Results text area
        self.results_text = scrolledtext.ScrolledText(results_frame, width=40, height=20, 
                                                     font=('Courier', 10))
        self.results_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Comparison button
        self.compare_button = ttk.Button(results_frame, text=">> Compare Algorithms", 
                                       command=self.show_comparison, state='disabled')
        self.compare_button.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(10, 0))
        
    def update_display(self):
        """Update the visual display of the grid"""
        self.ax.clear()
        
        # Grid setup
        grid_h, grid_w = self.engine.GRID_H, self.engine.GRID_W
        
        # Draw grid lines
        for i in range(grid_h + 1):
            self.ax.axhline(i, color='black', linewidth=1)
        for j in range(grid_w + 1):
            self.ax.axvline(j, color='black', linewidth=1)
        
        # Draw cells
        for r in range(grid_h):
            for c in range(grid_w):
                pos = (r, c)
                x, y = c, grid_h - 1 - r
                
                # Determine cell color and content
                if pos == self.engine.start_pos:
                    rect = Rectangle((x, y), 1, 1, facecolor='green', alpha=0.8)
                    self.ax.add_patch(rect)
                    self.ax.text(x+0.5, y+0.5, 'START', ha='center', va='center', 
                               fontweight='bold', fontsize=10, color='white')
                elif pos == self.engine.goal_pos:
                    rect = Rectangle((x, y), 1, 1, facecolor='red', alpha=0.8)
                    self.ax.add_patch(rect)
                    self.ax.text(x+0.5, y+0.5, 'GOAL', ha='center', va='center', 
                               fontweight='bold', fontsize=10, color='white')
                elif pos in self.engine.buildings:
                    rect = Rectangle((x, y), 1, 1, facecolor='brown', alpha=0.8)
                    self.ax.add_patch(rect)
                    self.ax.text(x+0.5, y+0.5, 'B', ha='center', va='center', 
                               color='white', fontweight='bold', fontsize=12)
                elif pos in self.engine.roadblocks:
                    rect = Rectangle((x, y), 1, 1, facecolor='orange', alpha=0.8)
                    self.ax.add_patch(rect)
                    self.ax.text(x+0.5, y+0.5, 'X', ha='center', va='center', 
                               color='white', fontweight='bold', fontsize=12)
                else:
                    rect = Rectangle((x, y), 1, 1, facecolor='lightgray', alpha=0.3)
                    self.ax.add_patch(rect)
                    # Show coordinates
                    self.ax.text(x+0.5, y+0.5, f'{pos}', ha='center', va='center', 
                               fontsize=8, alpha=0.7)
        
        self.ax.set_xlim(0, grid_w)
        self.ax.set_ylim(0, grid_h)
        self.ax.set_aspect('equal')
        self.ax.set_title('Pathfinding Grid - Click to interact', fontsize=12, fontweight='bold')
        
        # Add subtle grid enhancement
        self.ax.grid(True, alpha=0.3, linestyle=':', color='gray')
        
        self.canvas.draw()
        
        # Update position display with color coding
        start_str = str(self.engine.start_pos) if self.engine.start_pos else "None"
        goal_str = str(self.engine.goal_pos) if self.engine.goal_pos else "None"
        self.position_label.config(text=f"Start: {start_str}\nGoal: {goal_str}")
        
        # Update button states with visual feedback
        can_run = self.engine.start_pos is not None and self.engine.goal_pos is not None
        self.run_button.config(state='normal' if can_run else 'disabled')
        self.analysis_button.config(state='normal' if can_run else 'disabled')
        
    def on_grid_click(self, event):
        """Handle grid click events"""
        if event.inaxes != self.ax:
            return
            
        # Convert click coordinates to grid position
        col = int(event.xdata)
        row = self.engine.GRID_H - 1 - int(event.ydata)
        pos = (row, col)
        
        # Validate position
        if not self.engine.is_valid_position(pos):
            return
            
        if pos in self.engine.buildings or pos in self.engine.roadblocks:
            messagebox.showwarning("Invalid Position", 
                                 f"Position {pos} is blocked by an obstacle!")
            return
        
        # Handle position setting based on mode
        if self.mode == "set_start":
            self.engine.start_pos = pos
            self.highlight_cell(pos, 'lightgreen', 800)
            self.mode = "set_goal"
            self.mode_label.config(text="Click to set GOAL position", foreground='red')
            
        elif self.mode == "set_goal":
            if pos == self.engine.start_pos:
                messagebox.showwarning("Invalid Position", 
                                     "Goal position cannot be the same as start position!")
                return
                
            self.engine.goal_pos = pos
            self.highlight_cell(pos, 'lightcoral', 800)
            self.mode = "play"
            self.mode_label.config(text="Ready to run algorithms!", foreground='blue')
            
            # Update engine state
            try:
                self.engine.set_start_goal(self.engine.start_pos, self.engine.goal_pos)
            except ValueError as e:
                messagebox.showerror("Error", str(e))
                return
        
        self.update_display()
    
    def run_algorithms(self):
        """Run the selected pathfinding algorithms"""
        if not self.engine.start_pos or not self.engine.goal_pos:
            messagebox.showerror("Error", "Please set both start and goal positions!")
            return
        
        algorithm = self.algorithm_var.get()
        self.results_text.delete(1.0, tk.END)
        self.results_text.insert(tk.END, f"Running {algorithm} algorithm(s)...\n\n")
        self.root.update()
        
        try:
            if algorithm == "both":
                results = self.engine.compare_algorithms()
                
                if 'astar' in results:
                    self.results_text.insert(tk.END, format_result_summary(results['astar']) + "\n\n")
                if 'iddfs' in results:
                    self.results_text.insert(tk.END, format_result_summary(results['iddfs']) + "\n\n")
                
                # Show comparison
                if 'astar' in results and 'iddfs' in results:
                    self.results_text.insert(tk.END, ">> Quick Comparison:\n")
                    a_star = results['astar']
                    iddfs = results['iddfs']
                    
                    if 'error' not in a_star and 'error' not in iddfs:
                        self.results_text.insert(tk.END, 
                            f"Path Length: A*={a_star['path_length']}, IDDFS={iddfs['path_length']}\n")
                        self.results_text.insert(tk.END, 
                            f"Safety Points: A*={a_star['total_points']}, IDDFS={iddfs['total_points']}\n")
                        self.results_text.insert(tk.END, 
                            f"Execution Time: A*={a_star['execution_time']:.4f}s, IDDFS={iddfs['execution_time']:.4f}s\n")
                        self.results_text.insert(tk.END, 
                            f"Nodes Expanded: A*={a_star['nodes_expanded']}, IDDFS={iddfs['nodes_expanded']}\n")
                
                self.compare_button.config(state='normal')
                
            elif algorithm == "A*":
                result = self.engine.a_star_search()
                self.results_text.insert(tk.END, format_result_summary(result))
                
            elif algorithm == "IDDFS":
                result = self.engine.iddfs_search()
                self.results_text.insert(tk.END, format_result_summary(result))
            
            # Draw paths if found with animation
            self.root.after(500, lambda: self.animate_path_drawing(algorithm))
            
        except Exception as e:
            messagebox.showerror("Error", f"Algorithm execution failed: {str(e)}")
    
    def draw_paths(self, algorithm="both"):
        """Draw the found paths on the grid"""
        # Clear previous paths and redraw base grid
        self.update_display()
        
        # Draw A* path only if A* was selected
        if (algorithm in ["both", "A*"] and
            self.engine.last_a_star_result and 
            self.engine.last_a_star_result.get('path') and
            'error' not in self.engine.last_a_star_result):
            
            path = self.engine.last_a_star_result['path']
            self.draw_path(path, 'blue', 'A*', offset=(0.15, 0.15))
        
        # Draw IDDFS path only if IDDFS was selected
        if (algorithm in ["both", "IDDFS"] and
            self.engine.last_iddfs_result and 
            self.engine.last_iddfs_result.get('path') and
            'error' not in self.engine.last_iddfs_result):
            
            path = self.engine.last_iddfs_result['path']
            # Use purple if both algorithms, blue if only IDDFS
            color = 'purple' if (algorithm == "both" and self.engine.last_a_star_result) else 'blue'
            self.draw_path(path, color, 'IDDFS', offset=(-0.15, -0.15))
        
        self.canvas.draw()
    
    def draw_path(self, path, color, algorithm, offset=(0, 0)):
        """Draw a single path on the grid"""
        if not path or len(path) < 2:
            return
        
        grid_h = self.engine.GRID_H
        
        # Draw path nodes (skip start and goal)
        for i, pos in enumerate(path[1:-1], 1):
            x, y = pos[1] + 0.5 + offset[0], grid_h - 1 - pos[0] + 0.5 + offset[1]
            circle = Circle((x, y), 0.2, facecolor=color, alpha=0.8, edgecolor='black', linewidth=1)
            self.ax.add_patch(circle)
            self.ax.text(x, y, str(i), ha='center', va='center', 
                        fontweight='bold', fontsize=8, color='white')
        
        # Draw path arrows
        for i in range(len(path) - 1):
            pos1, pos2 = path[i], path[i + 1]
            x1 = pos1[1] + 0.5 + offset[0]
            y1 = grid_h - 1 - pos1[0] + 0.5 + offset[1]
            x2 = pos2[1] + 0.5 + offset[0]
            y2 = grid_h - 1 - pos2[0] + 0.5 + offset[1]
            
            self.ax.annotate('', xy=(x2, y2), xytext=(x1, y1),
                           arrowprops=dict(arrowstyle='->', color=color, lw=2, alpha=0.7))
        
        # Add algorithm label
        if path:
            start_pos = path[0]
            x = start_pos[1] + 0.5 + offset[0]
            y = grid_h - 1 - start_pos[0] + 0.8 + offset[1]
            self.ax.text(x, y, algorithm, ha='center', va='center',
                        bbox=dict(boxstyle='round,pad=0.3', facecolor=color, alpha=0.7),
                        fontsize=8, color='white', fontweight='bold')
    
    def create_random_game(self):
        """Create a random game setup"""
        try:
            start, goal = create_random_game(self.engine, 'medium')
            self.mode = "play"
            self.mode_label.config(text="Random game created! Ready to run algorithms!", foreground='blue')
            
            # Clear previous results
            self.results_text.delete(1.0, tk.END)
            self.results_text.insert(tk.END, f">> Random game created!\nStart: {start}\nGoal: {goal}\n\n")
            
            # Highlight the new positions
            self.highlight_cell(start, 'lightgreen', 1000)
            self.root.after(200, lambda: self.highlight_cell(goal, 'lightcoral', 1000))
            
            self.update_display()
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to create random game: {str(e)}")
    
    def reset_game(self):
        """Reset the game to initial state"""
        self.engine.reset_game()
        self.mode = "set_start"
        self.mode_label.config(text="Click to set START position", foreground='green')
        
        # Clear results
        self.results_text.delete(1.0, tk.END)
        self.results_text.insert(tk.END, "Game reset! Click on the grid to set start and goal positions.\n")
        
        # Reset button states
        self.compare_button.config(state='disabled')
        
        self.update_display()
    
    def show_analysis(self):
        """Show detailed grid analysis in a new window"""
        if not self.engine.start_pos or not self.engine.goal_pos:
            messagebox.showwarning("No Analysis", "Please set start and goal positions first!")
            return
        
        try:
            # Update engine state to ensure we have the latest data
            self.engine.set_start_goal(self.engine.start_pos, self.engine.goal_pos)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to prepare analysis: {str(e)}")
            return
        
        # Create analysis window
        analysis_window = tk.Toplevel(self.root)
        analysis_window.title("Grid Analysis - Layout, Safety, Heuristic & Cost Analysis")
        analysis_window.geometry("1200x900")
        
        # Create matplotlib figure for analysis
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(14, 12))
        canvas = FigureCanvasTkAgg(fig, analysis_window)
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Get grid data
        grid_h, grid_w = self.engine.GRID_H, self.engine.GRID_W
        
        # Plot 1: Grid Layout with Path
        self.plot_grid_layout(ax1, "Grid Layout with Obstacles")
        
        # Plot 2: Safety Points Analysis
        self.plot_safety_points(ax2, "Safety Points Distribution")
        
        # Plot 3: Heuristic Values (Manhattan Distance)
        self.plot_heuristic_values(ax3, "Manhattan Distance Heuristic h(n)")
        
        # Plot 4: g(n) Cost Analysis
        self.plot_g_costs(ax4, "g(n) Path Costs from Start")
        
        plt.tight_layout()
        canvas.draw()
    
    def plot_grid_layout(self, ax, title):
        """Plot basic grid layout with obstacles"""
        grid_h, grid_w = self.engine.GRID_H, self.engine.GRID_W
        
        # Draw grid lines
        for i in range(grid_h + 1):
            ax.axhline(i, color='black', linewidth=1)
        for j in range(grid_w + 1):
            ax.axvline(j, color='black', linewidth=1)
        
        # Draw cells
        for r in range(grid_h):
            for c in range(grid_w):
                pos = (r, c)
                x, y = c, grid_h - 1 - r
                
                if pos == self.engine.start_pos:
                    rect = Rectangle((x, y), 1, 1, facecolor='green', alpha=0.8)
                    ax.add_patch(rect)
                    ax.text(x+0.5, y+0.5, 'START', ha='center', va='center', fontweight='bold', color='white')
                elif pos == self.engine.goal_pos:
                    rect = Rectangle((x, y), 1, 1, facecolor='red', alpha=0.8)
                    ax.add_patch(rect)
                    ax.text(x+0.5, y+0.5, 'GOAL', ha='center', va='center', fontweight='bold', color='white')
                elif pos in self.engine.buildings:
                    rect = Rectangle((x, y), 1, 1, facecolor='brown', alpha=0.8)
                    ax.add_patch(rect)
                    ax.text(x+0.5, y+0.5, 'B', ha='center', va='center', color='white', fontweight='bold')
                elif pos in self.engine.roadblocks:
                    rect = Rectangle((x, y), 1, 1, facecolor='orange', alpha=0.8)
                    ax.add_patch(rect)
                    ax.text(x+0.5, y+0.5, 'X', ha='center', va='center', color='white', fontweight='bold')
                else:
                    rect = Rectangle((x, y), 1, 1, facecolor='lightblue', alpha=0.3)
                    ax.add_patch(rect)
                    ax.text(x+0.5, y+0.5, f'{pos}', ha='center', va='center', fontsize=8)
        
        ax.set_xlim(0, grid_w)
        ax.set_ylim(0, grid_h)
        ax.set_aspect('equal')
        ax.set_title(title, fontweight='bold')
    
    def plot_safety_points(self, ax, title):
        """Plot safety points for each position"""
        grid_h, grid_w = self.engine.GRID_H, self.engine.GRID_W
        
        # Calculate safety points for each position
        position_points = {}
        for r in range(grid_h):
            for c in range(grid_w):
                pos = (r, c)
                if pos not in self.engine.buildings and pos not in self.engine.roadblocks:
                    points = 0
                    # Check adjacency to buildings and roadblocks
                    for dr, dc in [(-1,0), (1,0), (0,-1), (0,1)]:
                        adj_pos = (r + dr, c + dc)
                        if adj_pos in self.engine.buildings:
                            points += 5
                        if adj_pos in self.engine.roadblocks:
                            points -= 3
                    position_points[pos] = points
        
        # Draw grid
        for i in range(grid_h + 1):
            ax.axhline(i, color='black', linewidth=1)
        for j in range(grid_w + 1):
            ax.axvline(j, color='black', linewidth=1)
        
        # Color code based on safety points
        for r in range(grid_h):
            for c in range(grid_w):
                pos = (r, c)
                x, y = c, grid_h - 1 - r
                
                if pos in self.engine.buildings or pos in self.engine.roadblocks:
                    color = 'gray'
                    text = 'B' if pos in self.engine.buildings else 'X'
                    text_color = 'white'
                else:
                    points = position_points.get(pos, 0)
                    if points > 0:
                        color = 'lightgreen'
                    elif points < 0:
                        color = 'lightcoral'
                    else:
                        color = 'white'
                    text = f'{points}'
                    text_color = 'black'
                
                rect = Rectangle((x, y), 1, 1, facecolor=color, alpha=0.7)
                ax.add_patch(rect)
                ax.text(x+0.5, y+0.5, text, ha='center', va='center', 
                       color=text_color, fontweight='bold', fontsize=10)
        
        ax.set_xlim(0, grid_w)
        ax.set_ylim(0, grid_h)
        ax.set_aspect('equal')
        ax.set_title(title, fontweight='bold')
    
    def plot_heuristic_values(self, ax, title):
        """Plot Manhattan distance heuristic values"""
        grid_h, grid_w = self.engine.GRID_H, self.engine.GRID_W
        goal = self.engine.goal_pos
        
        if not goal:
            ax.text(0.5, 0.5, 'No goal set', ha='center', va='center', transform=ax.transAxes)
            ax.set_title(title, fontweight='bold')
            return
        
        # Calculate heuristic values
        max_h = 0
        h_values = {}
        for r in range(grid_h):
            for c in range(grid_w):
                pos = (r, c)
                h_val = abs(r - goal[0]) + abs(c - goal[1])  # Manhattan distance
                h_values[pos] = h_val
                max_h = max(max_h, h_val)
        
        # Draw grid
        for i in range(grid_h + 1):
            ax.axhline(i, color='black', linewidth=1)
        for j in range(grid_w + 1):
            ax.axvline(j, color='black', linewidth=1)
        
        # Color code based on heuristic distance
        for r in range(grid_h):
            for c in range(grid_w):
                pos = (r, c)
                x, y = c, grid_h - 1 - r
                
                if pos in self.engine.buildings or pos in self.engine.roadblocks:
                    color = 'gray'
                    text = 'BLOCKED'
                    text_color = 'white'
                else:
                    h_val = h_values[pos]
                    intensity = 1 - (h_val / max_h) if max_h > 0 else 1
                    color = plt.cm.YlOrRd(intensity)
                    text = f'h={h_val}'
                    text_color = 'black' if intensity > 0.5 else 'white'
                
                rect = Rectangle((x, y), 1, 1, facecolor=color, alpha=0.8)
                ax.add_patch(rect)
                ax.text(x+0.5, y+0.5, text, ha='center', va='center', 
                       color=text_color, fontweight='bold', fontsize=8)
        
        ax.set_xlim(0, grid_w)
        ax.set_ylim(0, grid_h)
        ax.set_aspect('equal')
        ax.set_title(title, fontweight='bold')
    
    def plot_g_costs(self, ax, title):
        """Plot g(n) costs - actual path costs from start position"""
        grid_h, grid_w = self.engine.GRID_H, self.engine.GRID_W
        start = self.engine.start_pos
        
        if not start:
            ax.text(0.5, 0.5, 'No start position set', ha='center', va='center', transform=ax.transAxes)
            ax.set_title(title, fontweight='bold')
            return
        
        # Calculate g(n) costs using simple BFS from start
        from collections import deque
        
        g_costs = {start: 0}
        queue = deque([start])
        visited = {start}
        
        while queue:
            current = queue.popleft()
            current_cost = g_costs[current]
            
            # Check all 4 directions
            for dr, dc in [(-1,0), (1,0), (0,-1), (0,1)]:
                nr, nc = current[0] + dr, current[1] + dc
                neighbor = (nr, nc)
                
                # Check if neighbor is valid and not blocked
                if (0 <= nr < grid_h and 0 <= nc < grid_w and 
                    neighbor not in self.engine.buildings and 
                    neighbor not in self.engine.roadblocks and
                    neighbor not in visited):
                    
                    g_costs[neighbor] = current_cost + 1  # Uniform cost = 1
                    queue.append(neighbor)
                    visited.add(neighbor)
        
        # Find max cost for color scaling
        max_cost = max(g_costs.values()) if g_costs else 0
        
        # Draw grid
        for i in range(grid_h + 1):
            ax.axhline(i, color='black', linewidth=1)
        for j in range(grid_w + 1):
            ax.axvline(j, color='black', linewidth=1)
        
        # Color code based on g(n) costs
        for r in range(grid_h):
            for c in range(grid_w):
                pos = (r, c)
                x, y = c, grid_h - 1 - r
                
                if pos in self.engine.buildings or pos in self.engine.roadblocks:
                    color = 'gray'
                    text = 'BLOCKED'
                    text_color = 'white'
                elif pos in g_costs:
                    cost = g_costs[pos]
                    if pos == start:
                        color = 'green'
                        text = f'START\ng={cost}'
                        text_color = 'white'
                    elif pos == self.engine.goal_pos:
                        color = 'red'
                        text = f'GOAL\ng={cost}'
                        text_color = 'white'
                    else:
                        # Color based on distance from start (lower cost = lighter)
                        intensity = cost / max_cost if max_cost > 0 else 0
                        color = plt.cm.Blues(0.3 + 0.7 * intensity)  # Light blue to dark blue
                        text = f'g={cost}'
                        text_color = 'white' if intensity > 0.5 else 'black'
                else:
                    color = 'lightgray'
                    text = 'UNREACHABLE'
                    text_color = 'black'
                
                rect = Rectangle((x, y), 1, 1, facecolor=color, alpha=0.8)
                ax.add_patch(rect)
                ax.text(x+0.5, y+0.5, text, ha='center', va='center', 
                       color=text_color, fontweight='bold', fontsize=8)
        
        ax.set_xlim(0, grid_w)
        ax.set_ylim(0, grid_h)
        ax.set_aspect('equal')
        ax.set_title(title, fontweight='bold')
        
        # Add color bar explanation
        ax.text(0.02, 0.98, f'Max cost: {max_cost}\nLighter = closer to start', 
                transform=ax.transAxes, va='top', fontsize=8,
                bbox=dict(boxstyle='round,pad=0.3', facecolor='white', alpha=0.8))
    
    def show_comparison(self):
        """Show detailed algorithm comparison"""
        if not self.engine.last_a_star_result or not self.engine.last_iddfs_result:
            messagebox.showwarning("No Results", "Please run both algorithms first!")
            return
        
        # Create comparison window
        comp_window = tk.Toplevel(self.root)
        comp_window.title("Algorithm Comparison")
        comp_window.geometry("600x400")
        
        # Create comparison text
        text_widget = scrolledtext.ScrolledText(comp_window, font=('Courier', 11))
        text_widget.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        a_star = self.engine.last_a_star_result
        iddfs = self.engine.last_iddfs_result
        
        comparison = ">> DETAILED ALGORITHM COMPARISON\n"
        comparison += "="*50 + "\n\n"
        
        if 'error' not in a_star and 'error' not in iddfs:
            comparison += f"{'Metric':<25} {'A*':<15} {'IDDFS':<15}\n"
            comparison += "-" * 55 + "\n"
            comparison += f"{'Path Length':<25} {a_star['path_length']:<15} {iddfs['path_length']:<15}\n"
            comparison += f"{'Safety Points':<25} {a_star['total_points']:<15} {iddfs['total_points']:<15}\n"
            comparison += f"{'Execution Time (s)':<25} {a_star['execution_time']:<15.6f} {iddfs['execution_time']:<15.6f}\n"
            comparison += f"{'Nodes Expanded':<25} {a_star['nodes_expanded']:<15} {iddfs['nodes_expanded']:<15}\n"
            comparison += f"{'Nodes Generated':<25} {a_star['nodes_generated']:<15} {iddfs['nodes_generated']:<15}\n"
            
            if 'max_frontier_size' in a_star:
                comparison += f"{'Max Frontier Size':<25} {a_star['max_frontier_size']:<15} {'N/A':<15}\n"
            if 'iterations' in iddfs:
                comparison += f"{'Iterations':<25} {'N/A':<15} {iddfs['iterations']:<15}\n"
            
            comparison += "\n ANALYSIS:\n"
            
            if a_star['path_length'] < iddfs['path_length']:
                comparison += "• A* found a shorter path (optimal solution)\n"
            elif a_star['path_length'] > iddfs['path_length']:
                comparison += "• IDDFS found a shorter path (unusual but possible)\n"
            else:
                comparison += "• Both algorithms found paths of equal length\n"
            
            if a_star['total_points'] > iddfs['total_points']:
                comparison += "• A* achieved higher safety points\n"
            elif a_star['total_points'] < iddfs['total_points']:
                comparison += "• IDDFS achieved higher safety points\n"
            else:
                comparison += "• Both algorithms achieved equal safety points\n"
            
            if a_star['execution_time'] < iddfs['execution_time']:
                comparison += "• A* was faster to execute\n"
            else:
                comparison += "• IDDFS was faster to execute\n"
            
            comparison += f"\nCOMPLEXITY COMPARISON:\n"
            comparison += f"• A* Space Complexity: O(b^d) - stored {a_star['max_frontier_size']} nodes\n"
            comparison += f"• IDDFS Space Complexity: O(d) - linear in depth ({iddfs.get('max_depth_reached', 'N/A')})\n"
            comparison += f"• A* expanded {a_star['nodes_expanded']} nodes\n"
            comparison += f"• IDDFS expanded {iddfs['nodes_expanded']} nodes over {iddfs.get('iterations', 'N/A')} iterations\n"
        
        text_widget.insert(tk.END, comparison)
    
    def run_algorithms_animated(self):
        """Run algorithms with animated progress feedback"""
        original_text = self.run_button.cget('text')
        self.run_button.config(text="► Running...", state='disabled')
        
        def restore_and_run():
            self.run_algorithms()
            self.run_button.config(text=original_text, state='normal')
        
        self.root.after(100, restore_and_run)
    
    def create_random_game_animated(self):
        """Create random game with animation"""
        self.results_text.insert(tk.END, "Generating random game...\n")
        self.root.update()
        self.root.after(200, self.create_random_game)
    
    def reset_game_animated(self):
        """Reset game with smooth animation"""
        # Fade effect
        self.ax.set_alpha(0.5)
        self.canvas.draw()
        
        def complete_reset():
            self.reset_game()
            self.ax.set_alpha(1.0)
            self.canvas.draw()
        
        self.root.after(300, complete_reset)
    
    def highlight_cell(self, pos, color='yellow', duration=500):
        """Highlight a specific cell temporarily"""
        if not self.engine.is_valid_position(pos):
            return
            
        grid_h = self.engine.GRID_H
        x, y = pos[1], grid_h - 1 - pos[0]
        
        # Create highlight rectangle
        highlight = Rectangle((x, y), 1, 1, facecolor=color, alpha=0.6, 
                            edgecolor='black', linewidth=3)
        self.ax.add_patch(highlight)
        self.canvas.draw()
        
        # Remove highlight after duration
        def remove_highlight():
            if highlight in self.ax.patches:
                highlight.remove()
                self.canvas.draw()
        
        self.root.after(duration, remove_highlight)
    
    def animate_path_drawing(self, algorithm="both"):
        """Animate path drawing with smooth transitions"""
        # Get current paths based on selected algorithm
        paths_to_draw = []
        
        if (algorithm in ["both", "A*"] and 
            self.engine.last_a_star_result and 
            self.engine.last_a_star_result.get('path') and
            'error' not in self.engine.last_a_star_result):
            path = self.engine.last_a_star_result['path']
            paths_to_draw.append((path, 'blue', 'A*', (0.15, 0.15)))
        
        if (algorithm in ["both", "IDDFS"] and 
            self.engine.last_iddfs_result and 
            self.engine.last_iddfs_result.get('path') and
            'error' not in self.engine.last_iddfs_result):
            path = self.engine.last_iddfs_result['path']
            # Use purple if both algorithms, blue if only IDDFS
            color = 'purple' if (algorithm == "both" and self.engine.last_a_star_result) else 'blue'
            paths_to_draw.append((path, color, 'IDDFS', (-0.15, -0.15)))
        
        if paths_to_draw:
            self.draw_paths_step_by_step(paths_to_draw)
    
    def draw_paths_step_by_step(self, paths_data, step=0):
        """Draw paths step by step for animation effect"""
        max_steps = max(len(path_data[0]) for path_data in paths_data) if paths_data else 0
        
        if step <= max_steps:
            # Clear and redraw base
            self.update_display()
            
            # Draw partial paths
            for path, color, algorithm, offset in paths_data:
                if step < len(path):
                    partial_path = path[:step + 1]
                    if len(partial_path) > 1:
                        self.draw_path(partial_path, color, algorithm, offset)
            
            self.canvas.draw()
            
            # Schedule next step
            if step < max_steps:
                self.root.after(150, lambda: self.draw_paths_step_by_step(paths_data, step + 1))
    
    def on_key_press(self, event):
        """Handle key press events"""
        if event.key == 'q':
            # Ask for confirmation before quitting
            if messagebox.askokcancel("Quit Game", "Are you sure you want to quit the pathfinding game?"):
                self.root.quit()
                self.root.destroy()
    

def main():
    """Main application entry point"""
    root = tk.Tk()
    app = PathfindingGameApp(root)
    
    # Add menu bar
    menubar = tk.Menu(root)
    root.config(menu=menubar)
    
    # File menu
    file_menu = tk.Menu(menubar, tearoff=0)
    menubar.add_cascade(label="Game", menu=file_menu)
    file_menu.add_command(label="New Random Game", command=app.create_random_game)
    file_menu.add_command(label="Reset", command=app.reset_game)
    file_menu.add_separator()
    file_menu.add_command(label="Exit", command=root.quit)
    
    # Help menu
    help_menu = tk.Menu(menubar, tearoff=0)
    menubar.add_cascade(label="Help", menu=help_menu)
    
    def show_about():
        messagebox.showinfo("About", 
            "AI Pathfinding Game\n\n"
            "Compare A* and IDDFS algorithms on a grid-based pathfinding problem.\n\n"
            "Instructions:\n"
            "1. Click on the grid to set START position\n"
            "2. Click again to set GOAL position\n"
            "3. Choose algorithm and click 'Run Pathfinding'\n"
            "4. Compare results and visualize paths!\n\n"
            "Created for AI Assignment - Team Group 183")
    
    help_menu.add_command(label="How to Play", command=show_about)
    
    root.mainloop()


if __name__ == "__main__":
    main()
