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


# Stores game info
class Game:
    def __init__(self, game_id, board_width, board_height, game_mode, wrap, constrictor):
        self.game_id = game_id
        self.board_width = board_width
        self.board_height = board_height
        self.game_mode = game_mode
        self.wrap = wrap
        self.constrictor = constrictor

    # getters
    def get_board_width(self):
        return self.board_width

    def get_board_height(self):
        return self.board_height

    def get_wrap(self):
        return self.wrap

    def get_constrictor(self):
        return self.constrictor

    def print_info(self):
        print(f"Game ID: {self.game_id}")
        print(f"Board Width: {self.board_width}")
        print(f"Board Height: {self.board_height}")
        print(f"Game Mode: {self.game_mode}")
        print(f"Wrap: {self.wrap}")
        print(f"Constrictor: {self.constrictor}")


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
    game_state = request.get_json()

    # create game class
    game_id = game_state["game"]["id"]

    board_width = game_state['board']['width']
    board_height = game_state['board']['height']

    game_mode = game_state["game"]["ruleset"]["name"]

    # check if game mode has wrap
    wrap = game_mode in ["wrapped", "wrapped-constrictor", "spicy-meteors"]

    # check if game mode is constrictor
    constrictor = game_mode in ["constrictor", "wrapped-constrictor"]

    # create game class
    global Current_game
    Current_game = Game(game_id, board_width, board_height,
                        game_mode, wrap, constrictor)

    # Print start message
    print(f"{Back.BLUE}Game START{Style.RESET_ALL}")
    Current_game.print_info()
    return "ok"


# End of game
@app.post("/end")
@app.post("/battlesnake/end")
def end():
    print(f"{Back.BLUE}Game END{Style.RESET_ALL}")
    return "ok"


# Move is called on every turn
@app.post("/move")
@app.post("/battlesnake/move")
def move():
    game_state = request.get_json()

    # Print turn
    print(f"{Back.BLUE}Turn {game_state['turn']}{Style.RESET_ALL}")

    # get info from game class' getters
    board_width = Current_game.get_board_width()
    board_height = Current_game.get_board_height()
    wrap = Current_game.get_wrap()
    constrictor = Current_game.get_constrictor()

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
        print(f"Moves after avoid_borders: {moves}")

    # Avoid snakes
    moves = functions.avoid_snakes(game_state, player_head, moves, snakes, constrictor)
    print(f"Moves after avoid_snakes: {moves}")

    # Head on collision logic
    moves = functions.head_on_collision(game_state, player_head, moves)
    print(f"Moves after head_on_collision: {moves}")

    # Avoid hazards
    moves = functions.avoid_hazards(game_state, player_head, moves, player_health)
    print(f"Moves after avoid_hazards: {moves}")

    # Aim for food
    moves = functions.aim_for_food(game_state, player_head, moves)
    print(f"Moves after aim_for_food: {moves}")

    # Aim for middle
    moves = functions.aim_for_middle(game_state, player_head, moves)
    print(f"Moves after aim_for_middle: {moves}")

    # Chase tail if not contrictor
    if not constrictor:
        moves = functions.chase_tail(game_state, player_head, moves)
        print(f"Moves after chase_tail: {moves}")

    best_move = max(moves, key=lambda key: moves[key][1])
    print(f"Best move: {best_move}")

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

    print(f"\nRunning Battlesnake server at http://{host}:{port}")
    app.env = 'development'
    app.run(host=host, port=port, debug=True)