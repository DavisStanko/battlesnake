# My Battlesnake

## What is Battlesnake?

Battlesnake is a multiplayer snake game where your snake is controlled by code. Get started at [play.battlesnake.com](https://play.battlesnake.com).

## Behavior

This snake is a heuristics snake, meaning that unlike tree seach snakes it takes very little time to think of a move. The snake currently makes it's move calculations based on a danger/desire system. Moves are given a danger and desire score each turn. The move with the lowest danger score is chosen. If there are multiple moves with the same danger score, the desire score is used as a tie breaker.

### Danger

The danger scored is set to a specific level based on the situation. The levels are as follows:

- **LEVEL 5** (Certain death).
  - Moving out of bounds in game modes that don't support wall wrapping.
  - Moving into self.
  - Moving into hazrd sauce when hp is less than the hazard sauce damage.

- **LEVEL 4** (Probable death).
  - Moving into another snake's body.
  - (The opponent snake could die before we do, thus freeing up the tilee. However, this is unlikely.)

- **LEVEL 3** (Likely death).
  - Moving into a possible head on collision with a larger snake.
    - (The opponent snake could move elsewhere, thus avoiding the collision but it's better to be safe than sorry.)

- **LEVEL 2** (Risk of future death).
  - Moving into hazard sauce when hp is greater than the hazard sauce damage.

- **LEVEL 1** (Placeholder).
  - Currently unused.

### Desire

Unlike the danger score, the desire score is additive meaning that multiple desires can be applied to a single move. A desire of 6 can technically be achieved if all desires are applied to a single move. The desires are as follows:

- **LEVEL 3** (Highest desire).
  - Moving towards the nearest apple.

- **LEVEL 2** (Medium desire).
  - Moving into a possible head on collision with a smaller snake.
    - (The opponent snake could move elsewhere, thus avoiding the collision but it's nice to be aggressive.)

- **LEVEL 1** (Lowest desire).
  - Moving towards the middle of the board.
    - Taking control of the middle of the board is a good strategy in most game modes. Especially in in the contrictor mode where head on collisions always result in death and there is no food.

## Next Steps

1. Don't move into dead ends.
    - Currently the desires do not take dead ends into account. This means that the snake will happily move into a dead end if it is in the direction of the closest apple.

2. Pathfinding in wrap enabled game modes
    - As it stands, the snake does not consider potential shortcuts that involve wrapping through the wall when heading for apples.
    - Furthermore, the snake does not properly check for collisions when wrapping through the wall.

3. Purposefully kill other snakes?
    - The snake does not account for situations where other snakes are able to be trapped. Killing other snakes would end the game sooner and reduce the risk of them killing us later on.

4. Better pathfinding.
    - Searching is done with a rudimentry BFS search with a depth of 1. This means that the snake doesn't notice blocked paths until it is too late. A better search algorithm would be able to see blocked paths further ahead.

## License

This project is licensed under the [GPL-3.0](LICENSE.md)
GNU General Public License - see the [LICENSE.md](LICENSE.md) file for details.
