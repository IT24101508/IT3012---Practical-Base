import random
from collections import deque
import heapq
import math


class GreedyGridAgent:
    """A simple agent that tries to move around systematically to clear the grid."""

    def __init__(self):
        self.actions_pool = ['Up', 'Down', 'Left', 'Right']

    def sense_and_act(self, percept: dict) -> str:
        return random.choice(self.actions_pool)


class SearchAgent:

    def __init__(self):
        self.reached = set()
        self.plan = []
        self.active_algo = 'AStar'

    # ---------------------------------------------------------
    # HEURISTICS
    # ---------------------------------------------------------

    def manhattan_distance(self, pos, goal):
        return abs(pos[0] - goal[0]) + abs(pos[1] - goal[1])

    def euclidean_distance(self, pos, goal):
        return math.sqrt(
            (pos[0] - goal[0]) ** 2 +
            (pos[1] - goal[1]) ** 2
        )

    # ---------------------------------------------------------
    # BFS
    # ---------------------------------------------------------

    def bfs_search(self, start, goal, get_neighbors):

        frontier = deque([(start, [])])
        self.reached = {start}

        while frontier:

            state, path = frontier.popleft()

            if state == goal:
                return path

            for neighbor in get_neighbors(state):

                if neighbor not in self.reached:

                    self.reached.add(neighbor)

                    frontier.append(
                        (neighbor, path + [neighbor])
                    )

        return None

    # ---------------------------------------------------------
    # DFS
    # ---------------------------------------------------------

    def dfs_search(self, start, goal, get_neighbors):

        frontier = [(start, [])]
        self.reached = {start}

        while frontier:

            state, path = frontier.pop()

            if state == goal:
                return path

            for neighbor in get_neighbors(state):

                if neighbor not in self.reached:

                    self.reached.add(neighbor)

                    frontier.append(
                        (neighbor, path + [neighbor])
                    )

        return None

    # ---------------------------------------------------------
    # UCS
    # ---------------------------------------------------------

    def ucs_search(self, start, goal, get_neighbors):

        frontier = [(0, start, [])]
        self.reached = {start}

        while frontier:

            cost, state, path = heapq.heappop(frontier)

            if state == goal:
                return path

            for neighbor, step_cost in get_neighbors(state):

                if neighbor not in self.reached:

                    self.reached.add(neighbor)

                    heapq.heappush(
                        frontier,
                        (
                            cost + step_cost,
                            neighbor,
                            path + [neighbor]
                        )
                    )

        return None

    # ---------------------------------------------------------
    # A* SEARCH
    # ---------------------------------------------------------

    def astar_search(
        self,
        start_pos,
        goal_pos,
        walls,
        grid_size,
        heuristic_type='manhattan'
    ):

        frontier = []

        # FIX:
        # Use ONE variable name consistently.
        reached_states = set()

        width, height = grid_size

        # Heuristic for start
        if heuristic_type == 'manhattan':
            h_cost = self.manhattan_distance(
                start_pos,
                goal_pos
            )
        else:
            h_cost = self.euclidean_distance(
                start_pos,
                goal_pos
            )

        # g(n) = 0 for start
        g_cost = 0

        # f(n) = g(n) + h(n)
        f_cost = g_cost + h_cost

        # (f, g, position, path)
        heapq.heappush(
            frontier,
            (
                f_cost,
                g_cost,
                start_pos,
                []
            )
        )

        while frontier:

            f_cost, g_cost, current_pos, path_taken = heapq.heappop(
                frontier
            )

            # Goal reached
            if current_pos == goal_pos:

                self.reached = reached_states

                return path_taken

            # Already expanded
            if current_pos in reached_states:
                continue

            # Mark as expanded
            reached_states.add(current_pos)

            x, y = current_pos

            # Generate neighbors
            neighbors = [
                (x + 1, y),      # Right
                (x - 1, y),      # Left
                (x, y + 1),      # Up
                (x, y - 1)       # Down
            ]

            for neighbor in neighbors:

                nx, ny = neighbor

                # Check if neighbor is valid
                if (
                    0 <= nx < width
                    and
                    0 <= ny < height
                    and
                    neighbor not in walls
                    and
                    neighbor not in reached_states
                ):

                    # g(n)
                    g_new = g_cost + 1

                    # h(n)
                    if heuristic_type == 'manhattan':

                        h_new = self.manhattan_distance(
                            neighbor,
                            goal_pos
                        )

                    else:

                        h_new = self.euclidean_distance(
                            neighbor,
                            goal_pos
                        )

                    # f(n)
                    f_new = g_new + h_new

                    heapq.heappush(
                        frontier,
                        (
                            f_new,
                            g_new,
                            neighbor,
                            path_taken + [neighbor]
                        )
                    )

        # No path found
        self.reached = reached_states

        return None

    # ---------------------------------------------------------
    # CREATE AND EXECUTE PLAN
    # ---------------------------------------------------------

    def sense_and_act(self, percept):

        # If there is already a plan,
        # execute the next action
        if self.plan:
            return self.plan.pop(0)

        # Current position
        current = tuple(percept['agent_pos'])

        # Get food
        food = percept['all_food']

        # No food remaining
        if not food:
            return 'Suck'

        # Find closest food
        target = min(
            food,
            key=lambda pos:
            self.manhattan_distance(pos, current)
        )

        # Environment information
        walls = set(percept['walls'])

        width, height = percept['grid_size']

        # -----------------------------------------------------
        # Generate valid neighbors
        # -----------------------------------------------------

        def get_neighbors(state):

            x, y = state

            neighbors = [
                (x + 1, y),      # Right
                (x - 1, y),      # Left
                (x, y + 1),      # Up
                (x, y - 1)       # Down
            ]

            return [
                pos
                for pos in neighbors
                if (
                    0 <= pos[0] < width
                    and
                    0 <= pos[1] < height
                    and
                    pos not in walls
                )
            ]

        # -----------------------------------------------------
        # Select search algorithm
        # -----------------------------------------------------

        if self.active_algo == 'BFS':

            path = self.bfs_search(
                current,
                target,
                get_neighbors
            )

        elif self.active_algo == 'DFS':

            path = self.dfs_search(
                current,
                target,
                get_neighbors
            )

        elif self.active_algo == 'UCS':

            def ucs_neighbors(state):

                return [
                    (neighbor, 1)
                    for neighbor in get_neighbors(state)
                ]

            path = self.ucs_search(
                current,
                target,
                ucs_neighbors
            )

        elif self.active_algo == 'AStar':

            path = self.astar_search(
                current,
                target,
                walls,
                (width, height),
                heuristic_type='manhattan'
            )

        else:

            path = None

        # -----------------------------------------------------
        # No path found
        # -----------------------------------------------------

        if path is None:
            return 'Right'

        # -----------------------------------------------------
        # Convert path positions to actions
        # -----------------------------------------------------

        previous = current

        for position in path:

            if position[0] > previous[0]:

                self.plan.append('Right')

            elif position[0] < previous[0]:

                self.plan.append('Left')

            elif position[1] > previous[1]:

                self.plan.append('Up')

            elif position[1] < previous[1]:

                self.plan.append('Down')

            previous = position

        # Execute first action
        if self.plan:
            return self.plan.pop(0)

        return 'Suck'


# ---------------------------------------------------------
# TESTING
# ---------------------------------------------------------

if __name__ == "__main__":

    agent = SearchAgent()

    start = (0, 0)
    goal = (3, 4)

    print(
        "Manhattan Distance:",
        agent.manhattan_distance(start, goal)
    )

    print(
        "Euclidean Distance:",
        agent.euclidean_distance(start, goal)
    )