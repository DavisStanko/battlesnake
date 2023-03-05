# My Main Battlesnake

## What is Battlesnake?

Battlesnake is a multiplayer snake game where your snake is controlled by code. It is not limited just to Python and can be set up easily and for free using [replit](https://replit). Get started at [play.battlesnake.com](https://play.battlesnake.com).

## Behavior

The snake currently does the following when prompted to move:

1. Avoids moves that result in instant death if possible (ex. moving into itself, moving out of bounds, or moving into and opponents body).
    - If there are no safe moves it moves down (helps to differentiate between purposeful moves and errors since errors make the snake move up).
    - If there is one safe move it moves there.
    - If a snakes tail is guaranteed to move out of the way (because they can't eat this turn) then the tile occupied by the tail is considered safe.
    - If the game mode supports wall wrapping, the border is considered safe.

2. Avoids possible head on collisions with bigger or equally sized snakes.
    - Head on collisions are not covered by step one as all snakes move at once. Therefore it's necessary to look into where the opposing snakes heads *could* end up and avoid that if collision would kill us.

3. Avoids hazard sauce if possible.
    - Hazard sauce causes snakes to lose 16hp instead of the normal 1hp per turn.

4. Attempts possible head on collisions with smaller snakes.
    - If there is a possibility of killing a snake via head on collisions: take it. The kill is not guaranteed as the opponent could move elsewhere.

5. Find the closest apple and move towards it.
    - Apples reset hp to 100 and extend the snakes length by 1 tile.

## Next Steps

1. Don't move into dead ends.
    - Currently when there are no apples on screen the snake opts to move randomly around the safe moves available. Furthermore, even when there are apples on screen, the snake moves without regard to its surroundings. This leads it to sometimes choosing moves that lead to immanent (but not immediate) death.

2. Choose best option when attempting to kill a snake via head on collision.
    - When approaching a snake diagonally there are two possible head on collisions. Moreover, when in the range of multiple snakes there can be up to three possible head on collisions. In the snakes current form, if there are multiple chances of killing a snake via head on collision it will just pick the first instead of the best.

3. Pathfinding in wrap enabled game modes
    - As it stands, the snake does not consider potential shortcuts that involve wrapping through the wall when heading for apples.
    - Furthermore, the snake does not check to see if wrapping through the wall is safe, treating it only as a last resort.

4. Deal with hazard sauce better.
    - Currently the snake will avoid hazard sauce at all costs regardless of whether or not there is an incentive to enter. Furthermore, it can't find it's way out easily once deep inside the sauce.

5. Purposefully kill other snakes?
    - The snake does not account for situations where other snakes are able to be trapped. Killing other snakes would end the game sooner and reduce the risk of them killing us later on.

6. Change snake philosophy.
    - Always moving towards the nearest apple is neither aggressive nor defensive. While it does mean that dying from a lack of health is exceedingly unlikely, it does nothing to prevent other snakes from trapping us.

## License

This project is licensed under the [GPL-3.0](LICENSE.md)
GNU General Public License - see the [LICENSE.md](LICENSE.md) file for details.
