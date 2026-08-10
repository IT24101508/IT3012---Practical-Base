# visual_grid_game.py
import random
import tkinter as tk


class VisualGridHuntGame:
    """A flexible Pacman-style grid environment with support for configurable opponents and larger scales."""

    def __init__(self, width=10, height=10, num_food=10, num_opponents=2, custom_walls=None):
        self.width = width
        self.height = height
        self.agent_pos = [0, 0]  # Starting position (x, y)
        self.facing = "Up" 

        if custom_walls is not None:
            self.walls = set(custom_walls)
        else:
            # Generate some default scattered walls for a larger grid
            self.walls = {(2, 2), (2, 3), (5, 5), (6, 5), (3, 7)}

        # Dynamically generate random food positions avoiding walls and agent start
        self.food_positions = set()
        while len(self.food_positions) < num_food:
            fx = random.randint(0, self.width - 1)
            fy = random.randint(0, self.height - 1)
            pos_tuple = (fx, fy)

            if pos_tuple != (0, 0) and pos_tuple not in self.walls:
                self.food_positions.add(pos_tuple)

        self.toxic_traps = set()
        num_traps = 5  # Number of traps

        while len(self.toxic_traps) < num_traps:
            tx = random.randint(0, self.width - 1)
            ty = random.randint(0, self.height - 1)
            trap = (tx, ty)

            if (trap != (0, 0) and
                    trap not in self.walls and
                    trap not in self.food_positions):
                self.toxic_traps.add(trap)

        # Generate adversarial opponents
        self.opponents = []
        while len(self.opponents) < num_opponents:
            ox = random.randint(0, self.width - 1)
            oy = random.randint(0, self.height - 1)
            op_pos = [ox, oy]

            if (tuple(op_pos) != (0, 0) and
                    tuple(op_pos) not in self.walls and
                    tuple(op_pos) not in self.food_positions and
                    tuple(op_pos) not in self.toxic_traps):
                self.opponents.append(op_pos)

        self.score = 0
        self.steps = 0
        self.collision = False

    def get_percept(self) -> dict:
        """ Partial observability: The agent only knows what is at its current location and whether there is a wall directly in front of it."""

        x, y = self.agent_pos

        # Determine the cell directly ahead
        next_x, next_y = x, y

        if self.facing == "Up":
           next_y += 1
        elif self.facing == "Down":
           next_y -= 1
        elif self.facing == "Left":
           next_x -= 1
        elif self.facing == "Right":
           next_x += 1

        # Check whether the next cell is outside the grid
        outside_grid = (
            next_x < 0 or next_x >= self.width or
            next_y < 0 or next_y >= self.height
        )

        wall_ahead = outside_grid or (next_x, next_y) in self.walls

        return {
           "wall_ahead": wall_ahead,
           "food_here": (x, y) in self.food_positions,
           "toxin_here": (x, y) in self.toxic_traps,
           "collision": self.collision
        }

    def execute_action(self, action: str):
        self.steps += 1

        if action == "Suck":
           if tuple(self.agent_pos) in self.food_positions:
              self.food_positions.remove(tuple(self.agent_pos))
              self.score += 20
           return

        if action == "Left":
           directions = ["Up", "Left", "Down", "Right"]
           index = directions.index(self.facing)
           self.facing = directions[(index + 1) % 4]
           return
        
        if action == "Right":
           directions = ["Up", "Right", "Down", "Left"]
           index = directions.index(self.facing)
           self.facing = directions[(index + 1) % 4]
           return
        new_pos = list(self.agent_pos)

        if action == "Forward":

           if self.facing == "Up":
              new_pos[1] = min(
                  self.height - 1,
                  new_pos[1] + 1
              )

           elif self.facing == "Down":
                new_pos[1] = max(
                     0,
                     new_pos[1] - 1
                )

           elif self.facing == "Left":
                new_pos[0] = max(
                    0,
                    new_pos[0] - 1
                )

           elif self.facing == "Right":
                new_pos[0] = min(
                    self.width - 1,
                    new_pos[0] + 1
                )

        if tuple(new_pos) in self.walls:
           self.score -= 5
        else:
           self.agent_pos = new_pos

        tuple_pos = tuple(self.agent_pos)

        if tuple_pos in self.food_positions:
           self.food_positions.remove(tuple_pos)
           self.score += 20

        if tuple_pos in self.toxic_traps:
           self.score -= 15

        for op in self.opponents:

            move = random.choice(
                ["Up", "Down", "Left", "Right", "Stay"]
            )

            if move == "Up" and op[1] < self.height - 1:
               op[1] += 1

            elif move == "Down" and op[1] > 0:
               op[1] -= 1

            elif move == "Left" and op[0] > 0:
               op[0] -= 1

            elif move == "Right" and op[0] < self.width - 1:
                op[0] += 1

            if op == self.agent_pos:
                self.score -= 50
                self.collision = True

    def is_done(self) -> bool:
        return len(self.food_positions) == 0 or self.steps >= 60 or self.collision

class ModelBasedAgent:
    """Model-Based Agent with internal memory."""

    def __init__(self):
        # Internal memory
        self.visited_cells = {(0, 0)}

        self.x = 0
        self.y = 0

        # Current facing direction
        self.facing = "Up"

        # Remember previous percept and action
        self.last_percept = None
        self.last_action = None
    def get_next_position(self):
        """Calculate the cell directly ahead."""

        next_x = self.x
        next_y = self.y

        if self.facing == "Up":
            next_y += 1
        elif self.facing == "Down":
            next_y -= 1
        elif self.facing == "Left":
            next_x -= 1
        elif self.facing == "Right":
            next_x += 1

        return (next_x, next_y)
    def turn_left(self):
        directions = ["Up", "Left", "Down", "Right"]
        index = directions.index(self.facing)
        self.facing = directions[(index + 1) % 4]

    def turn_right(self):
        directions = ["Up", "Right", "Down", "Left"]
        index = directions.index(self.facing)
        self.facing = directions[(index + 1) % 4]


    def sense_and_act(self, percept):

        self.last_percept = percept

        current_position = (self.x, self.y)

        # Remember current cell
        self.visited_cells.add(current_position)

        # IF food_here THEN Suck
        # -------------------------------
        if percept["food_here"]:
            action = "Suck"

        else:

            # Find cell in front of the agent
            next_cell = self.get_next_position()

            if percept["wall_ahead"]:

                self.turn_right()
                action = "Right"

            elif next_cell in self.visited_cells:

                self.turn_right()
                action = "Right"

            else:

                action = "Forward"

                # Update internal position
                if self.facing == "Up":
                    self.y += 1
                elif self.facing == "Down":
                    self.y -= 1
                elif self.facing == "Left":
                    self.x -= 1
                elif self.facing == "Right":
                    self.x += 1

                # Remember new cell
                self.visited_cells.add((self.x, self.y))   

        # Remember last action
        self.last_action = action

        return action

class GridGameGUI:
    """Tkinter wrapper that dynamically scales cell sizes to keep larger grids on screen."""

    def __init__(self, root, width=10, height=10, num_food=12, num_opponents=2, walls=None):
        self.root = root
        self.root.title("IT3012 - Scalable Multi-Agent Grid Hunt")

        self.env = VisualGridHuntGame(width=width, height=height, num_food=num_food, num_opponents=num_opponents,
                                      custom_walls=walls)
        self.agent = ModelBasedAgent()

        # Dynamically calculate cell size so the total canvas fits nicely within a 600x600 window ceiling
        max_canvas_dim = 600
        self.cell_size = max(20, min(max_canvas_dim // self.env.width, max_canvas_dim // self.env.height))

        canvas_w = self.env.width * self.cell_size
        canvas_h = self.env.height * self.cell_size

        self.canvas = tk.Canvas(root, width=canvas_w, height=canvas_h, bg="white")
        self.canvas.pack()

        self.label = tk.Label(root, text="Score: 0 | Steps: 0", font=("Arial", 14))
        self.label.pack(pady=10)

        self.btn = tk.Button(root, text="Start Simulation", command=self.run_loop, font=("Arial", 12), bg="#000066",
                             fg="white")
        self.btn.pack(pady=5)

        self.draw_grid()

    def draw_grid(self):
        self.canvas.delete("all")

        for x in range(self.env.width):
            for y in range(self.env.height):
                x1 = x * self.cell_size
                y1 = (self.env.height - 1 - y) * self.cell_size
                x2 = x1 + self.cell_size
                y2 = y1 + self.cell_size

                color = "#f1f5f9" if (x, y) not in self.env.walls else "#64748b"
                self.canvas.create_rectangle(x1, y1, x2, y2, fill=color, outline="#cbd5e1")

                # Only draw text if cell is large enough
                if self.cell_size >= 40 and (x, y) in self.env.walls:
                    self.canvas.create_text(x1 + self.cell_size / 2, y1 + self.cell_size / 2, text="W", fill="white",
                                            font=("Arial", 8, "bold"))

        for fx, fy in self.env.food_positions:
            offset = self.cell_size * 0.25
            x1 = fx * self.cell_size + offset
            y1 = (self.env.height - 1 - fy) * self.cell_size + offset
            self.canvas.create_oval(x1, y1, x1 + self.cell_size * 0.5, y1 + self.cell_size * 0.5, fill="#f59e0b",
                                    outline="#d97706")

        
        for tx, ty in self.env.toxic_traps:
           offset = self.cell_size * 0.25
           x1 = tx * self.cell_size + offset
           y1 = (self.env.height - 1 - ty) * self.cell_size + offset
           self.canvas.create_oval(x1, y1, x1 + self.cell_size * 0.5, y1 + self.cell_size * 0.5, fill="#800080", outline="#4B0082"
    )

        for ox, oy in self.env.opponents:
            offset = self.cell_size * 0.2
            x1 = ox * self.cell_size + offset
            y1 = (self.env.height - 1 - oy) * self.cell_size + offset
            self.canvas.create_rectangle(x1, y1, x1 + self.cell_size * 0.6, y1 + self.cell_size * 0.6, fill="#990000",
                                         outline="#7a0000")

        ax, ay = self.env.agent_pos
        offset = self.cell_size * 0.15
        x1 = ax * self.cell_size + offset
        y1 = (self.env.height - 1 - ay) * self.cell_size + offset
        self.canvas.create_oval(x1, y1, x1 + self.cell_size * 0.7, y1 + self.cell_size * 0.7, fill="#000066",
                                outline="#1e3a8a")

    def run_loop(self):
        self.btn.config(state="disabled")

        def step():
            if not self.env.is_done():
                percept = self.env.get_percept()
                action = self.agent.sense_and_act(percept)

                # Execute the action in the environment
                self.env.execute_action(action)

                self.draw_grid()
                self.label.config(text=f"Score: {self.env.score} | Steps: {self.env.steps} | Action: {action} | Memory: {len(self.agent.visited_cells)}" )
                self.root.after(250, step)
            else:
                end_text = f"Collision! Game Over! Final Score: {self.env.score}" if self.env.collision else f"Finished! Final Score: {self.env.score}"
                self.label.config(text=end_text)
                self.btn.config(state="normal")

        step()


if __name__ == "__main__":
    root = tk.Tk()
    # Try a larger grid size like 12x12 with 15 food and 3 opponents!
    app = GridGameGUI(root, width=12, height=12, num_food=15, num_opponents=0)
    root.mainloop()
