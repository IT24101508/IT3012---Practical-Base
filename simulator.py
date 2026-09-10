from visual_grid_game import VisualGridHuntGame
from agent import SearchAgent


def run_grid_hunt():

    env = VisualGridHuntGame()
    agent = SearchAgent()

    agent.active_algo = 'BFS'

    print("=== Search Agent Grid Hunt Started ===")

    while not env.is_done():

        percept = env.get_percept()

        action = agent.sense_and_act(percept)

        env.execute_action(action)

        print(
            f"Pos: {env.agent_pos} | "
            f"Action: {action} | "
            f"Food Left: {len(env.food_positions)} | "
            f"Score: {env.score}"
        )

    print(
        f"\nGame Over! Final Score: "
        f"{env.score} after {env.steps} steps."
    )


if __name__ == "__main__":
    run_grid_hunt()