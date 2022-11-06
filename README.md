# My Main Battlesnake

## What is Battlesnake?

Battlesnake is a multiplayer snake game where your snake is controlled by code. It is not limited just to Python and can be set up easily and for free using [replit](https://replit). Get started at [play.battlesnake.com](https://play.battlesnake.com).

## Behavior

The snake currently does the following when prompted to move:

1. Decides against moves that result in instant death if possible (ex. moving into itself, moving out of bounds, or moving into and opponents body).
    - If there are no safe moves it moves down (helps to differentiate between purposeful move and error since errors make the snake move up).
    - If there is one safe move it moves there.
    - If there are multiple safe moves, it continues its' calculations.
    - If a snakes tail is guaranteed to move out of the way (because they can't eat this turn) then the tile occupied by the tail is considered safe.
2. Avoids possible head on collisions with bigger or equally sized snakes.
    - Head on collisions are not covered by step one as all snakes move at once. Therefore we need to look into where the opposing snakes head *could* end up and avoid that if collision would kill us.
3. Attempts possible head on collisions with smaller snakes.
    - If there is a possibility of killing a snake via head on collisions: take it. The kill is not guaranteed as the opponent could move elsewhere.
4. Finds the closest apple
5. Moves towards the closest apple.

## Next Steps

### Important

0. Deal with multiple "safe" moves where the only choices are possible deadly head on collisions.
    - **Theoretically this has been fixed but it has yet to be tested in a real game as this situation is rare.**
    - In the event where there are multiple moves that aren't guaranteed death, the snake attempts to find the best move. In doing so, it removes moves that could result in deadly head on collisions. However, it is possible that there are no safe moves left. In this case, the snake just moves down. This is not a good solution and needs to be fixed.

1. Don't move into dead ends.
    - Currently when there are no apples on screen the snake opts to move randomly around the safe moves available. Furthermore, even when there are apples on screen, the snake moves without regard to its surroundings. This leads it to sometimes chose moves that lead to immanent (but not immediate) death.

2. Choose best option when attempting to kill a snake via head on collision.
    - When approaching a snake diagonally there are two possible head on collisions. Moreover, when in the range of multiple snakes there can be up to three possible head on collisions. In the snakes current form, if there are multiple chances of killing a snake via head on collision it will just pick the first instead of the best.

### Things to consider

1. Deal with hazard sauce.
    - Battlesnake has multiple game modes. Currently, my snake was developed only for the standard mode. However, it would be interesting to adapt to modes with more variables such as hazard sauce.

2. Purposefully kill other snakes?
    - The snake does not account for situations where other snakes are able to be trapped. Killing other snakes would end the game sooner and reduce the risk of them killing us later on.

3. Change snake philosophy.
    - Always moving towards the nearest apple is neither aggressive nor defensive. While it does mean that dying from a lack of health is exceedingly unlikely, it does nothing to prevent other snakes from trapping us.

## License

This project is licensed under the [GPL-3.0](LICENSE.md)
GNU General Public License - see the [LICENSE.md](LICENSE.md) file for
details.
