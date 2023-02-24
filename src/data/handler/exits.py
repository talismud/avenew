# Copyright (c) 2023, LE GOFF Vincent
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

"""Exit handler, to store room exits."""

from typing import Optional, Set, Tuple, TYPE_CHECKING

from data.base.link import Link
from data.handler.abc import BaseHandler
from data.exit import Exit, Direction

if TYPE_CHECKING:
    from data.character import Character
    from data.room import Room


class ExitHandler(BaseHandler):

    """A handler for exits."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.exits = None

    def __getstate__(self):
        return self.exits

    def __setstate__(self, exits):
        self.exits = exits

    def __iter__(self):
        self.load_exits()
        return iter(self.all)

    @property
    def all(self) -> tuple[Exit]:
        """Only return linked exits in the direction order."""
        self.load_exits()
        exits = []
        for direction in Direction:
            exit = self.exits.get(direction)
            if exit:
                exits.append(exit)

        return tuple(exits)

    def get_visible_by(self, character: "Character") -> tuple[Exit]:
        """Only return visible exits by this character."""
        return [exit for exit in self.all if exit.can_see(character)]

    def add(
        self,
        direction: Direction,
        destination: "Room",
        name: str,
        aliases: Optional[set[str]] = None,
        back: bool = True,
    ) -> Exit:
        """Add a new exit, if no exit exists in this direction.

        Args:
            direction (Direction): the direction in which to build this exit.
            destination (Room): the destination of this exit.
            name (str): the exit's name.
            aliases (set, optional): the optional aliases of this exit.
            back (bool, optional): if `true` (the default, creates
                    an exit in the destination linking back to
                    the current room.

        If an exit already exists in this direction, raisess a ValueError.

        """
        self.load_exits()
        if self.exits.get(direction):
            raise ValueError(
                f"an exit already exists in the direction: {direction}"
            )

        origin, _ = self.model
        exit = Exit.create(
            direction=direction,
            origin=origin,
            destination=destination,
            name=name,
            aliases=aliases,
        )
        self.exits[direction] = exit
        self.save()

        if back:
            destionation.exits.load_exits()
            opposite = direction.opposite
            if opposite not in direction.exits.exits:
                direction.exits.add(
                    opposite, origin, str(opposite), back=False
                )

        return exit

    def load_exits(self):
        """Load, if necessary, this room's exit."""
        if self.exits is None:
            room, _ = self.model
            query = (
                (Exit.table.origin_id == room.id)
                & (Exit.table.destination_id.isnot(None))
            )
            exits = Exit.select(query)
            self.exits = {exit.direction: exit for exit in exits}
