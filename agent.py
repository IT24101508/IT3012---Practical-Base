import random
from collections import deque
import heapq


class GreedyGridAgent:
    """A simple agent that tries to move around systematically to clear the grid."""

    def __init__(self):
        self.actions_pool = ['Up', 'Down', 'Left', 'Right']

    def sense_and_act(self, percept: dict) -> str:
        pos = percept['agent_pos']
        return random.choice(self.actions_pool)


class SearchAgent:

    def __init__(self):
        self.reached = set()
        self.plan = []
        self.active_algo = 'BFS'

    # =========================================================
    # BFS - FIFO Queue
    # =========================================================
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

    # =========================================================
    # DFS - LIFO Stack
    # =========================================================
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

    # =========================================================
    # UCS - Priority Queue
    # =========================================================
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

    # =========================================================
    # CREATE AND EXECUTE PLAN
    # =========================================================
    def sense_and_act(self, percept):

        # If there is already a plan,
        # execute the next action
        if self.plan:

            return self.plan.pop(0)

        # -----------------------------------------------------
        # No plan -> create a new plan
        # -----------------------------------------------------

        current = tuple(percept['agent_pos'])
        food = percept['all_food']

        # No food remaining
        if not food:
            return 'Suck'

        # -----------------------------------------------------
        # Find closest food
        # -----------------------------------------------------

        target = min(
            food,
            key=lambda pos:
            abs(pos[0] - current[0]) +
            abs(pos[1] - current[1])
        )

        # -----------------------------------------------------
        # Get environment information
        # -----------------------------------------------------

        walls = set(percept['walls'])

        width, height = percept['grid_size']

        # -----------------------------------------------------
        # Generate valid neighboring cells
        # -----------------------------------------------------

        def get_neighbors(state):

            x, y = state

            neighbors = [
                (x + 1, y),  # Right
                (x - 1, y),  # Left
                (x, y + 1),  # Up
                (x, y - 1)   # Down
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

        else:

            path = None

        # -----------------------------------------------------
        # If no path exists
        # -----------------------------------------------------

        if path is None:

            return 'Right'

        # -----------------------------------------------------
        # Convert positions into actions
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

        # -----------------------------------------------------
        # Execute first action
        # -----------------------------------------------------

        if self.plan:

            return self.plan.pop(0)

        return 'Suck'