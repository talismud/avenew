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
from typing import TYPE_CHECKING

from data.base.link import Field, Link

if TYPE_CHECKING:
    from data.character import Character
    from data.room import Room


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


class Exit(Link):

    """Link to represent a one-way exit between two rooms."""

    direction: Direction = Direction.INVALID
    name: str = "not set"
    aliases: set[str] = Field(default_factory=set)

    @property
    def origin(self):
        return type(self).get(id=self.origin_id)

    @property
    def destination(self):
        destination_id = self.destination_id
        return type(self).get(id=destination_id) if destination_id else None

    def can_see(self, character: "Character") -> bool:
        """Return whether this exit can be seen by this character.

        Args:
            character (Character): the character trying to see this exit.

        """
        return True

    def get_name_for(self, character: "Character") -> str:
        """Return the exit name for this character.

        Args:
            character (Character): the character seeing this exit.

        """
        return self.name
