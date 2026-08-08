# Battlesnake

My competitive Battlesnake API that leverages a multi-variable heuristic engine to outmaneuver opponents and maintain a Top 50 global ranking. 

## Features

- **Heuristic Engine** — evaluates moves based on multiple variables such as danger levels, desire for food, and maintaining safe space.
- **Collision Avoidance** — detects and avoids borders, hazards, and other snakes, including head-to-head collision predictions.
- **Pathfinding** — aims for food when health is low, stays centralized, and chases its own tail to maintain safe areas.
- **Game Mode Support** — includes logic for different modes such as wrapped and constrictor game modes.

## Usage

You can play against or observe this snake on the official [Battlesnake Platform](https://play.battlesnake.com/profile/davisstanko).

To run this Battlesnake locally:

1. Clone the repository and install dependencies:

```bash
pip install -r requirements.txt
```
*(Alternatively, you can use `poetry install`)*

2. Start the Flask server:

```bash
python main.py
```

The server will run locally on port `8080` (or the port specified by the `PORT` environment variable). You can then use the [Battlesnake CLI](https://docs.battlesnake.com/references/cli) to test it locally.

## License

This project is licensed under the [GPL-3.0](LICENSE.md)
GNU General Public License — see the [LICENSE.md](LICENSE.md) file for details.
