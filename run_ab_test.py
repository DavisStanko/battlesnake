#!/usr/bin/env python3
"""
run_ab_test.py — A/B test harness for Battlesnake strategies.

Usage:
    python run_ab_test.py [N]

    N — number of games to play (default: 100)

Environment / config:
    BATTLESNAKE_CLI — path to the battlesnake binary
                      (default: ~/go/bin/battlesnake)
    PYTHON          — python interpreter to use for servers
                      (default: .venv/bin/python if it exists, else python3)
"""

import csv
import os
import re
import signal
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path

# ── configuration ──────────────────────────────────────────────────────────────

STRATEGY_A = "baseline"
STRATEGY_B = "variant"
PORT_A = 8000
PORT_B = 8001

URL_A = f"http://localhost:{PORT_A}"
URL_B = f"http://localhost:{PORT_B}"

DEFAULT_GAMES = 100
STARTUP_GRACE = 2.5  # seconds to wait after launching servers

# Locate the battlesnake CLI binary
BATTLESNAKE_CLI = os.environ.get(
    "BATTLESNAKE_CLI",
    str(Path.home() / "go" / "bin" / "battlesnake"),
)

# Locate the Python interpreter
_venv_python = Path(__file__).parent / ".venv" / "bin" / "python"
PYTHON = os.environ.get(
    "PYTHON",
    str(_venv_python) if _venv_python.exists() else "python3",
)

# ── helpers ────────────────────────────────────────────────────────────────────

def launch_server(strategy: str, port: int) -> subprocess.Popen:
    """Start a snake server in the background and return the Popen handle."""
    env = {**os.environ, "STRATEGY_NAME": strategy, "PORT": str(port)}
    proc = subprocess.Popen(
        [PYTHON, "main.py"],
        env=env,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    return proc


def wait_for_server(url: str, timeout: float = 10.0, interval: float = 0.25) -> bool:
    """Poll a server URL until it responds or the timeout elapses."""
    import urllib.request
    import urllib.error

    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        try:
            urllib.request.urlopen(url, timeout=1)
            return True
        except Exception:
            time.sleep(interval)
    return False


def kill_servers(*procs: subprocess.Popen) -> None:
    """Terminate server processes gracefully, then force-kill if needed."""
    for proc in procs:
        if proc and proc.poll() is None:
            proc.terminate()
    time.sleep(0.5)
    for proc in procs:
        if proc and proc.poll() is None:
            proc.kill()


# Matches: "Game completed after 40 turns. Variant was the winner."
_WINNER_RE = re.compile(r"Game completed after \d+ turns\. (.+?) was the winner\.")
# Matches: "Game completed after N turns. X and Y were tied."
_DRAW_RE = re.compile(r"Game completed after \d+ turns\..* tied\.")


# Matches same-turn mutual elimination: "Game completed after N turns."
# with no survivor (winner line absent, draw line absent)
_COMPLETED_RE = re.compile(r"Game completed after \d+ turns\.")
# Matches connection refused / snake metadata errors
_CONN_ERR_RE = re.compile(r"(connection refused|Error getting snake metadata|dial tcp)", re.I)

MAX_RETRIES = 3
RETRY_DELAY = 1.0  # seconds between retries


def run_game(game_number: int, seed: int) -> str | None:
    """
    Run a single game via the Battlesnake CLI.
    Returns the winner name, "DRAW", or None on failure.
    Retries up to MAX_RETRIES times on transient connection errors.
    """
    for attempt in range(1, MAX_RETRIES + 1):
        result = subprocess.run(
            [
                BATTLESNAKE_CLI, "play",
                "-u", URL_A, "-n", STRATEGY_A,
                "-u", URL_B, "-n", STRATEGY_B,
                "-r", str(seed),
            ],
            capture_output=True,
            text=True,
        )

        output = result.stdout + result.stderr  # CLI writes INFO lines to stderr

        # Transient connection error — retry
        if _CONN_ERR_RE.search(output) and attempt < MAX_RETRIES:
            time.sleep(RETRY_DELAY)
            continue

        if _DRAW_RE.search(output):
            return "DRAW"

        m = _WINNER_RE.search(output)
        if m:
            return m.group(1)

        # Both snakes eliminated on the same turn → implicit draw
        if _COMPLETED_RE.search(output):
            return "DRAW"

        break  # unrecoverable parse failure

    print(f"  [!] Game {game_number} produced no parseable result.", file=sys.stderr)
    return None


def print_table(results: dict, total: int) -> None:
    """Print a formatted summary table to stdout."""
    col = 12
    header = f"{'Strategy':<{col}} {'Wins':>6} {'Losses':>7} {'Draws':>7} {'Win Rate':>10}"
    sep = "-" * len(header)
    print()
    print(sep)
    print(header)
    print(sep)
    for name in (STRATEGY_A, STRATEGY_B):
        w = results[name]["wins"]
        l = results[name]["losses"]
        d = results[name]["draws"]
        played = w + l + d
        rate = (w / played * 100) if played else 0
        print(f"{name:<{col}} {w:>6} {l:>7} {d:>7} {rate:>9.1f}%")
    print(sep)
    print(f"Total games played: {total}")
    print()


def save_csv(rows: list[dict], total_games: int) -> Path:
    """Save per-game results to a timestamped CSV file."""
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    out_dir = Path(__file__).parent / "ab_results"
    out_dir.mkdir(exist_ok=True)
    path = out_dir / f"ab_test_{ts}.csv"

    with path.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["game", "seed", "winner"])
        writer.writeheader()
        writer.writerows(rows)

    return path


# ── main ───────────────────────────────────────────────────────────────────────

def main() -> None:
    n_games = int(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_GAMES

    print(f"Battlesnake A/B Test Harness")
    print(f"  Strategy A: {STRATEGY_A} @ {URL_A}")
    print(f"  Strategy B: {STRATEGY_B} @ {URL_B}")
    print(f"  Games:      {n_games}")
    print(f"  CLI:        {BATTLESNAKE_CLI}")
    print()

    # ── validate CLI ──
    if not Path(BATTLESNAKE_CLI).exists():
        sys.exit(
            f"[ERROR] Battlesnake CLI not found at {BATTLESNAKE_CLI}.\n"
            "Install it with: go install github.com/BattlesnakeOfficial/rules/cli/battlesnake@latest"
        )

    # ── launch servers ──
    proc_a = proc_b = None

    def _cleanup(signum=None, frame=None):
        print("\n[*] Cleaning up servers...")
        kill_servers(proc_a, proc_b)
        sys.exit(1 if signum else 0)

    signal.signal(signal.SIGINT, _cleanup)
    signal.signal(signal.SIGTERM, _cleanup)

    print("[*] Starting servers...")
    proc_a = launch_server(STRATEGY_A, PORT_A)
    proc_b = launch_server(STRATEGY_B, PORT_B)

    print(f"    Waiting for {URL_A} ...", end=" ", flush=True)
    if not wait_for_server(URL_A):
        print("FAILED")
        _cleanup()
    print("OK")

    print(f"    Waiting for {URL_B} ...", end=" ", flush=True)
    if not wait_for_server(URL_B):
        print("FAILED")
        _cleanup()
    print("OK\n")

    # ── run games ──
    results = {
        STRATEGY_A: {"wins": 0, "losses": 0, "draws": 0},
        STRATEGY_B: {"wins": 0, "losses": 0, "draws": 0},
    }
    rows = []
    completed = 0

    # Use a fixed base seed so results are reproducible; each game gets seed+i
    base_seed = 42_000

    try:
        for i in range(1, n_games + 1):
            seed = base_seed + i
            print(f"  Game {i:>4}/{n_games}  seed={seed}  ...", end=" ", flush=True)

            winner = run_game(i, seed)

            if winner == "DRAW":
                results[STRATEGY_A]["draws"] += 1
                results[STRATEGY_B]["draws"] += 1
                print("DRAW")
            elif winner == STRATEGY_A:
                results[STRATEGY_A]["wins"] += 1
                results[STRATEGY_B]["losses"] += 1
                print(f"Winner: {STRATEGY_A}")
            elif winner == STRATEGY_B:
                results[STRATEGY_B]["wins"] += 1
                results[STRATEGY_A]["losses"] += 1
                print(f"Winner: {STRATEGY_B}")
            else:
                print("ERROR (skipped)")
                winner = "ERROR"

            rows.append({"game": i, "seed": seed, "winner": winner or "ERROR"})
            if winner and winner != "ERROR":
                completed += 1

    finally:
        kill_servers(proc_a, proc_b)
        print("\n[*] Servers stopped.")

    # ── report ──
    print_table(results, completed)

    csv_path = save_csv(rows, completed)
    print(f"[*] Results saved to: {csv_path}\n")


if __name__ == "__main__":
    main()
