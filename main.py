import importlib
import os

from colorama import Back, Style
from flask import Flask, request

# ---------------------------------------------------------------------------
# Strategy loader
# ---------------------------------------------------------------------------
# Set STRATEGY_NAME env var to pick a strategy, e.g.:
#   STRATEGY_NAME=baseline python main.py
#   STRATEGY_NAME=variant python main.py
# Defaults to "baseline" when unset.
_strategy_name = os.environ.get("STRATEGY_NAME", "baseline")
try:
    strategy = importlib.import_module(f"strategies.strategy_{_strategy_name}")
except ModuleNotFoundError as exc:
    raise SystemExit(
        f"[ERROR] Unknown strategy '{_strategy_name}'. "
        f"Make sure strategies/strategy_{_strategy_name}.py exists."
    ) from exc

print(f"[Battlesnake] Loaded strategy: {_strategy_name}")

# ---------------------------------------------------------------------------
# Flask app
# ---------------------------------------------------------------------------
app = Flask("Battlesnake")

DEBUG = False


def debug_print(*args, **kwargs):
    if DEBUG:
        print(*args, **kwargs)


# Stores game info
class Game:
    def __init__(self, game_id, board_width, board_height, game_mode, wrap, constrictor):
        self.game_id = game_id
        self.board_width = board_width
        self.board_height = board_height
        self.game_mode = game_mode
        self.wrap = wrap
        self.constrictor = constrictor

    def get_board_width(self):
        return self.board_width

    def get_board_height(self):
        return self.board_height

    def get_wrap(self):
        return self.wrap

    def get_constrictor(self):
        return self.constrictor

    def print_info(self):
        debug_print(f"Game ID: {self.game_id}")
        debug_print(f"Board Width: {self.board_width}")
        debug_print(f"Board Height: {self.board_height}")
        debug_print(f"Game Mode: {self.game_mode}")
        debug_print(f"Wrap: {self.wrap}")
        debug_print(f"Constrictor: {self.constrictor}")


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

# Battlesnake metadata — pulled from the active strategy so each variant can
# have its own colour/head/tail without touching main.py.
@app.get("/")
@app.get("/battlesnake/")
def info():
    return strategy.INFO


# Start of game
@app.post("/start")
@app.post("/battlesnake/start")
def start():
    game_state = request.get_json()

    game_id = game_state["game"]["id"]
    board_width = game_state["board"]["width"]
    board_height = game_state["board"]["height"]
    game_mode = game_state["game"]["ruleset"]["name"]
    wrap = game_mode in ["wrapped", "wrapped-constrictor", "spicy-meteors"]
    constrictor = game_mode in ["constrictor", "wrapped-constrictor"]

    global Current_game
    Current_game = Game(game_id, board_width, board_height, game_mode, wrap, constrictor)

    debug_print(f"{Back.BLUE}Game START{Style.RESET_ALL}")
    Current_game.print_info()
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
    debug_print(f"{Back.BLUE}Turn {game_state['turn']}{Style.RESET_ALL}")

    wrap = Current_game.get_wrap()
    constrictor = Current_game.get_constrictor()

    best_move = strategy.choose_move(game_state, wrap, constrictor)
    debug_print(f"Best move: {best_move}")
    return {"move": best_move}


@app.after_request
def identify_server(response):
    response.headers["Server"] = "BattlesnakeOfficial/starter-snake-python"
    return response


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    host = "0.0.0.0"
    port = int(os.environ.get("PORT", "8000"))

    print(f"\nRunning Battlesnake server at http://{host}:{port}")
    print(f"Strategy: {_strategy_name}")
    app.env = "development" if DEBUG else "production"
    app.run(host=host, port=port, debug=DEBUG)