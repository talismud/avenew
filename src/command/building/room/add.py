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

from command import Command
from command.building.room.main import Room
from data.direction import Direction


class Add(Command):

    """Command to add a new room in a given direction.

    Usage:
      room add <direction>
      radd <direction>

    """

    parent = Room
    global_alias = "radd"
    args = Command.new_parser()
    direction = args.add_argument("word", dest="direction")
    names = ", ".join(
        direction.value
        for direction in Direction
        if direction is not Direction.INVALID
    )
    direction.msg_mandatory = "You should specify a direction: {names}."
    options = args.add_argument("options", optional=True)
    options.add_option("title", "t", default="A new room")
    options.add_option("barcode", "b", default=None)

    def run(self, direction: str, title: str, barcode: str | None):
        """Run the command."""
        try:
            direction = Direction.from_name(direction)
        except ValueError:
            self.msg(f"The direction {direction!r} cannot be found.")
            return

        room = self.character.location
        if room.exits.has(direction):
            self.msg(
                f"The room {room.barcode} already has an exit "
                f"in the {direction.name} direction."
            )
            return

        if barcode:
            already = type(room).get(barcode=barcode, raise_not_found=False)
            if already is not None:
                self.msg(f"The barcode {barcode} is already in use.")
                return

        destination = room.create_neighbor(
            direction, barcode=barcode, title=title
        )
        self.msg(
            f"The room {destination.barcode} was created in "
            f"the {direction.value} direction."
        )
