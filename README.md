# My Main Battlesnake

### What is Battlesnake?

Battlesnake is a multiplayer snake game where your snake is controlled by code. It is not limited just to Python and can be set up easily and for free using [replit](https://replit). Get started at [play.battlesnake.com](https://play.battlesnake.com).

## Behavior

The snake currently does the following when prompted to move:

1. Decides against moves that result in instant death if possible (ex. moving into itself, moving out of bounds, or moving into and opponents body).
    - If there are no safe moves it moves down just in case (read why in the next steps section).
    - If there is one safe move it moves there.
    - If there are multiple safe moves, it continues its' calculations.
2. Avoids possible head on collisions with bigger or equally sized snakes.
    - Head on collisions are not covered by step one as all snakes move at once. Therefore we need to look into where the opposing snakes head *could* end up and avoid that if collision would kill us.
3. Finds the closest apple
4. Move towards the closest apple.

## Next Steps

1. Purposefully turn into smaller snakes heads.
    - The code to avoid other snakes head could be reused to opt to attempt to collide head on with other snakes when the collision would result in their death. However, this collision rarely be guaranteed as the other snake could have it's own collision avoidance system.

2. Deal with hazard sauce.
    - Battlesnake has multiple game modes. Currently, my snake was developed only for the standard mode. However, it would be interesting to adapt to modes with more variables such as hazard sauce.

3. Don't move into dead ends.
    - Currently when there are no apples on screen the snake opts to move randomly around the safe moves available. Furthermore, even when there are apples on screen, the snake moves without regard to its surroundings. This leads it to sometimes chose moves that lead to immanent (but not immediate) death.

4. Purposefully kill other snakes?

    - The snake does not account for situations where other snakes are able to be trapped. Killing other snakes would end the game sooner and reduce the risk of them killing us later on.

5. Change snake philosophy.
    - Always moving towards the nearest apple is neither aggressive nor defensive. While it does mean that dying from a lack of health is exceedingly unlikely, it does nothing to prevent other snakes from trapping us.


## License

This project is licensed under the [GPL-3.0](LICENSE.md)
GNU General Public License - see the [LICENSE.md](LICENSE.md) file for
details.
