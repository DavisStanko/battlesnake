import importlib
import os

from colorama import Back, Style
from flask import Flask, request

# ---------------------------------------------------------------------------
# Strategy loader
# ---------------------------------------------------------------------------
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


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

@app.get("/")
@app.get("/battlesnake/")
def info():
    return strategy.INFO


@app.post("/start")
@app.post("/battlesnake/start")
def start():
    debug_print(f"{Back.BLUE}Game START{Style.RESET_ALL}")
    return "ok"


@app.post("/end")
@app.post("/battlesnake/end")
def end():
    debug_print(f"{Back.BLUE}Game END{Style.RESET_ALL}")
    return "ok"


@app.post("/move")
@app.post("/battlesnake/move")
def move():
    game_state = request.get_json()
    debug_print(f"{Back.BLUE}Turn {game_state['turn']}{Style.RESET_ALL}")

    # Derive game flags directly from the request payload (stateless)
    game_mode = game_state["game"]["ruleset"]["name"]
    wrap = game_mode in ["wrapped", "wrapped-constrictor", "spicy-meteors"]
    constrictor = game_mode in ["constrictor", "wrapped-constrictor"]

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
