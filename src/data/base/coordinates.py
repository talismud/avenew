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

"""Coordinates data model.

Coordinates can be added on any node in your game.  Doing so
is just a matter of altering the node data class.  For rooms
(which can have a coordinates), just edit `data/room.py`:

```python
# ...
from data.base.node import Field, Node
from data.handler.coordinates import CoordinateHandler


class Room(Node):

    # ...
    coordinates: CoordinateHandler = Field(default_factory=CoordinateHandler)
```

You can then manipulate the `coordinates` attribute on rooms.
Coordinates don't have to be valid and they are not by default.  You can
update them easily.  Assuming you have a variable `room`
containing a valid room:

```python
room.coordinates.update(0, 0, 0) # x=0, y=0, z=0
# Which is equivalent to:
room.x = 0
room.y = 0
room.z = 0
# You can also retrieve all the rooms in a given raduis:
around = room.coordinates.around(2) # Will return all rooms in a 2-room radius
# You can also get the room at given coordinates:
other = room.coordinates.get_at(2, 0, 0) # x=2, y=0, z=0
if other is not None: # The room doesn't exist there.
    # ...
# Or mesure the distance between two rooms with valid coordinates:
distance = room.coordinates.distance(other)
# To check whether a room has valid coordinates, just do:
if room.coordinates: # Valid
    # ...
```

"""

from typing import Callable

from data.base.model import Field, Model


class Coordinates(Model):

    """Coordinates for nodes."""

    id: int = Field(primary_key=True)
    valid: bool
    x: float
    y: float
    z: float
    model: int = Field(unique=True)


def closure(
    modifications: dict[str, int | float]
) -> Callable[[float, float, float, float], tuple[float, float, float]]:
    """Create a closure for coordinates with modifications.

    This is mostly functional: it will return a closure as a callable
    taking the multiplier and original coordinates as parameters,
    returning the modified coordinates.

    Args:
        modificaitons (dict): dictionary of modifications.

    Returns:
        closure (callable): a callable that takes the multiplier,
                x y and z coordinates and returns
                the modified coordinates.

    """

    def inner(
        multiplier: int | float, x: int | float, y: int | float, z: int | float
    ) -> tuple[int | float, int | float, int | float]:
        coordinates = {"x": x, "y": y, "z": z}
        for axis, mod in modifications.items():
            coordinates[axis] = coordinates[axis] + multiplier * mod
        return tuple(coordinates.values())

    names = []
    for axis, mod in modifications.items():
        if mod > 0:
            name = f"+{mod}"
        else:
            name = str(mod)
        names.append(f"{axis}{name}")
    names = ", ".join(names)
    inner.__qualname__ = f"closure for {names}"
    return inner
