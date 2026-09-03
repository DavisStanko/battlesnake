# Battlesnake

My competitive Battlesnake API that leverages a multi-variable heuristic engine to outmaneuver opponents and maintain a Top 50 global ranking. 

<p align="center">
  <img src="demo.gif" alt="Battlesnake screenshot" />
</p>

## Features

- **Heuristic Engine** — evaluates moves based on multiple variables such as danger levels, desire for food, and maintaining safe space.
- **Collision Avoidance** — detects and avoids borders, hazards, and other snakes, including head-to-head collision predictions.
- **Pathfinding** — aims for food when health is low, stays centralized, and chases its own tail to maintain safe areas.
- **Game Mode Support** — includes logic for different modes such as wrapped and constrictor game modes.

## Usage

You can play against or observe this snake on the official [Battlesnake Platform](https://play.battlesnake.com/profile/davisstanko).

## Local Development

### 1. Setup

Create and activate a Python virtual environment, install dependencies, and install the Battlesnake CLI:

```bash
# Create and activate virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install Python dependencies
pip install -r requirements.txt

# Install Battlesnake CLI (requires Go)
go install github.com/BattlesnakeOfficial/rules/cli/battlesnake@latest
```

### 2. Running the Server

Start the snake server on port `8000` (or any custom port using the `PORT` environment variable):

```bash
PORT=8000 python main.py
```

### 3. Running Test Games

Once the server is running on port 8000, you can run test games using the Battlesnake CLI in various modes:

* **Headless (CLI output only):**
  ```bash
  battlesnake play --url http://localhost:8000
  ```

* **Terminal Visualizer (ASCII map with colors):**
  ```bash
  battlesnake play --url http://localhost:8000 -v -c --delay 200
  ```

* **GUI / Browser Visualizer:**
  ```bash
  battlesnake play --url http://localhost:8000 --browser --delay 200
  ```

## License

This project is licensed under the [GPL-3.0](LICENSE.md)
GNU General Public License — see the [LICENSE.md](LICENSE.md) file for details.

