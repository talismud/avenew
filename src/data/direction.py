# Copyright (c) 2022, LE GOFF Vincent
# All rights reserved.

# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:

# 1. Redistributions of source code must retain the above copyright notice,
#    this list of conditions and the following disclaimer.

# 2. Redistributions in binary form must reproduce the above copyright notice,
#    this list of conditions and the following disclaimer in the documentation
#    and/or other materials provided with the distribution.

# 3. Neither the name of the copyright holder nor the names of its
#    contributors may be used to endorse or promote products derived from
#    this software without specific prior written permission.

# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS
# BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY,
# OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED
# OF THE POSSIBILITY OF SUCH DAMAGE.

"""The exit object, a link."""

from enum import Enum


class Direction(Enum):

    """Direction enumeration."""

    INVALID = "invalid"
    EAST = "east"
    SOUTHEAST = "southeast"
    SOUTH = "south"
    SOUTHWEST = "southwest"
    WEST = "west"
    NORTHWEST = "northwest"
    NORTH = "north"
    NORTHEAST = "northeast"
    DOWN = "down"
    UP = "up"

    @property
    def opposite(self):
        """Return the opposite exit."""
        return _OPPOSITES[self]

    @property
    def aliases(self) -> tuple[str, ...]:
        """Return the aliases for this direction."""
        return _ALIASES[self]

    @staticmethod
    def from_name(name: str) -> "Direction":
        """Get the direction from a given name.

        Aliases are used to find the proper direction.

        If it cannot be found, raises a ValueError.

        Args:
            name (str): the direction name (or alias).

        Returns:
            direction (Direction): the direction if found.

        Raises:
            ValueError if the name cannot be matched.

        """
        name = name.lower()
        found = None
        for direction, aliases in _ALIASES.items():
            if name in aliases:
                found = direction
                break

        if found is None:
            raise ValueError(f"cannot find the direction {name!r}")

        return found


_OPPOSITES = {
    Direction.EAST: Direction.WEST,
    Direction.SOUTHEAST: Direction.NORTHWEST,
    Direction.SOUTH: Direction.NORTH,
    Direction.SOUTHWEST: Direction.NORTHEAST,
    Direction.WEST: Direction.EAST,
    Direction.NORTHWEST: Direction.SOUTHEAST,
    Direction.NORTH: Direction.SOUTH,
    Direction.NORTHEAST: Direction.SOUTHWEST,
    Direction.DOWN: Direction.UP,
    Direction.UP: Direction.DOWN,
    Direction.INVALID: Direction.INVALID,
}


_ALIASES = {
    Direction.EAST: ("east", "e"),
    Direction.SOUTHEAST: ("south-east", "southeast", "se", "s-e"),
    Direction.SOUTH: ("south", "s"),
    Direction.SOUTHWEST: ("south-west", "souhwest", "sw", "s-w"),
    Direction.WEST: ("west", "w"),
    Direction.NORTHWEST: ("north-east", "northeast", "ne", "n-e"),
    Direction.NORTH: ("north", "n"),
    Direction.NORTHEAST: ("north-east", "northeast", "ne", "n-e"),
    Direction.DOWN: ("down", "d"),
    Direction.UP: ("up", "u"),
}
