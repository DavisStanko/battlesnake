"""
Baseline strategy for Battlesnake.

This module exposes a single entry point:

    choose_move(game_state, wrap, constrictor) -> str

It delegates to the shared heuristics in functions.py without altering any
game-logic behaviour — this is a pure structural extraction.
"""

import sys
import os

# Allow importing from the project root when this module is loaded directly
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import functions

# ---------------------------------------------------------------------------
# Strategy metadata (returned by the /info endpoint when this strategy is active)
# ---------------------------------------------------------------------------
INFO = {
    "apiversion": "1",
    "author": "Davis Stanko",
    "color": "#ff0000",
    "head": "dragon",
    "tail": "dragon",
}


def choose_move(game_state: dict, wrap: bool, constrictor: bool) -> str:
    """
    Decide the best move for the current turn.

    Parameters
    ----------
    game_state : dict
        The full JSON payload from the Battlesnake engine.
    wrap : bool
        Whether the current game mode has board wrapping enabled.
    constrictor : bool
        Whether the current game mode is constrictor (no food, shrinking safe zone).

    Returns
    -------
    str
        One of "up", "down", "left", "right".
    """
    board_width = game_state["board"]["width"]
    board_height = game_state["board"]["height"]

    # direction → (danger_level, desire_level)
    moves = {"right": (0, 0), "left": (0, 0), "up": (0, 0), "down": (0, 0)}

    player_head = game_state["you"]["body"][0]
    player_health = game_state["you"]["health"]
    snakes = game_state["board"]["snakes"]

    # Avoid borders if wrap is not enabled
    if not wrap:
        moves = functions.avoid_borders(player_head, board_width, board_height, moves)

    # Avoid snakes (including self)
    moves = functions.avoid_snakes(game_state, player_head, moves, snakes, constrictor)

    # Head-on collision logic
    moves = functions.head_on_collision(game_state, player_head, moves)

    # Avoid hazards
    moves = functions.avoid_hazards(game_state, player_head, moves, player_health)

    # Aim for food
    moves = functions.aim_for_food(game_state, player_head, moves)

    # Aim for middle of the board
    moves = functions.aim_for_middle(game_state, player_head, moves)

    # Chase our own tail to avoid dead ends (disabled in constrictor)
    if not constrictor:
        moves = functions.chase_tail(game_state, player_head, moves)

    best_move = max(moves, key=lambda key: moves[key][1])
    return best_move
