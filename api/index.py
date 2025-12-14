import functions
import os
from colorama import Back, Style

from flask import Flask
from flask import request

# Danger levels
CERTAIN_DEATH = 4
PROBABLE_DEATH = 3
POSSIBLE_DEATH = 2
HARM = 1

# Desire levels
KILL_DESIRE = 1000
FOOD_DESIRE = 100
MIDDLE_DESIRE = 10
TAIL_DESIRE = 1


app = Flask("Battlesnake")

# Debug flag 
DEBUG = False

def debug_print(*args, **kwargs):
    if DEBUG:
        print(*args, **kwargs)


# Battlesnake metadata (Name, Author, Color, Head, Tail)
@app.get("/")
@app.get("/battlesnake/")
def info():
    return {
        "apiversion": "1",
        "author": "Davis Stanko",
        "color": "#ff0000",
        "head": "dragon",
        "tail": "dragon",
    }


# Start of game
@app.post("/start")
@app.post("/battlesnake/start")
def start():
    # Stateless: no need to store game state
    debug_print(f"{Back.BLUE}Game START{Style.RESET_ALL}")
    return "ok"


# End of game
@app.post("/end")
@app.post("/battlesnake/end")
def end():
    debug_print(f"{Back.BLUE}Game END{Style.RESET_ALL}")
    return "ok"


# Move is called on every turn
@app.post("/move")
@app.post("/battlesnake/move")
def move():
    game_state = request.get_json()

    # Print turn
    debug_print(f"{Back.BLUE}Turn {game_state['turn']}{Style.RESET_ALL}")

    # Extract game info directly from the request payload (stateless)
    board_width = game_state['board']['width']
    board_height = game_state['board']['height']
    game_mode = game_state["game"]["ruleset"]["name"]
    
    # Check if game mode has wrap
    wrap = game_mode in ["wrapped", "wrapped-constrictor", "spicy-meteors"]
    
    # Check if game mode is constrictor
    constrictor = game_mode in ["constrictor", "wrapped-constrictor"]

    # reset list of valid moves
    # direction, danger level, desire level
    moves = {"right": (0, 0), "left": (0, 0), "up": (0, 0), "down": (0, 0)}

    # locate the head of the snake
    player_head = game_state["you"]["body"][0]

    # get player health
    player_health = game_state["you"]["health"]

    # get snake body part coordinates
    snakes = game_state['board']['snakes']

    # Avoid borders if wrap is not enabled
    if wrap is False:
        moves = functions.avoid_borders(player_head, board_width, board_height, moves)
        debug_print(f"Moves after avoid_borders: {moves}")

    # Avoid snakes
    moves = functions.avoid_snakes(game_state, player_head, moves, snakes, constrictor)
    debug_print(f"Moves after avoid_snakes: {moves}")

    # Head on collision logic
    moves = functions.head_on_collision(game_state, player_head, moves)
    debug_print(f"Moves after head_on_collision: {moves}")

    # Avoid hazards
    moves = functions.avoid_hazards(game_state, player_head, moves, player_health)
    debug_print(f"Moves after avoid_hazards: {moves}")

    # Aim for food
    moves = functions.aim_for_food(game_state, player_head, moves)
    debug_print(f"Moves after aim_for_food: {moves}")

    # Aim for middle
    moves = functions.aim_for_middle(game_state, player_head, moves)
    debug_print(f"Moves after aim_for_middle: {moves}")

    # Chase tail if not contrictor
    if not constrictor:
        moves = functions.chase_tail(game_state, player_head, moves)
        debug_print(f"Moves after chase_tail: {moves}")

    best_move = max(moves, key=lambda key: moves[key][1])
    debug_print(f"Best move: {best_move}")

    # Move
    return {"move": best_move}


@app.after_request
def identify_server(response):
    response.headers["Server"] = "BattlesnakeOfficial/starter-snake-python"
    return response


# Start server when `python main.py` is run
if __name__ == "__main__":
    host = "0.0.0.0"
    port = int(os.environ.get("PORT", "8080"))

    if DEBUG:
        print(f"\nRunning Battlesnake server at http://{host}:{port}")
    # Disable Flask debug mode in prod unless explicitly debugging
    app.env = 'development' if DEBUG else 'production'
    app.run(host=host, port=port, debug=DEBUG)
