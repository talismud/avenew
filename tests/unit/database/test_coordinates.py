import pytest

from data.base.coordinates import Coordinates
from data.base.node import Field, Node
from data.exit import Direction
from data.handler.coordinates import CoordinateHandler


class Room(Node):

    barcode: str = Field("not set", unique=True)
    title: str = "not yet"
    coordinates: CoordinateHandler = Field(default_factory=CoordinateHandler)


def test_invalid(db):
    """Coordinates should be invalid by default."""
    db.bind({Coordinates, Room})
    center = Room.create(barcode="center", title="The center")
    assert not center.coordinates


def test_valid_after_update(db):
    """Updating coordinates should make them valid."""
    db.bind({Coordinates, Room})
    center = Room.create(barcode="center", title="The center")
    center.coordinates.update(0, 0, 0)
    assert center.coordinates


def test_invalid_after_set_2(db):
    """Only setting 2 coordinates won't make it valid."""
    db.bind({Coordinates, Room})
    center = Room.create(barcode="center", title="The center")
    center.coordinates.x = 0
    center.coordinates.y = 0
    assert not center.coordinates


def test_valid_after_set_3(db):
    """Setting 3 coordinates should make them valid."""
    db.bind({Coordinates, Room})
    center = Room.create(barcode="center", title="The center")
    center.coordinates.x = 0
    center.coordinates.y = 0
    center.coordinates.z = 0
    assert center.coordinates


def test_update_coordinates(db):
    """Updating one coordinate manually should reflect on the handler."""
    db.bind({Coordinates, Room})
    center = Room.create(barcode="center", title="The center")
    center.coordinates.update(0, 0, 0)
    center.coordinates.x = 2
    assert center.coordinates.x == 2


def test_update_coordinates_from_DB(db):
    """Settng one coordinate manually should reflect in the database."""
    db.bind({Coordinates, Room})
    center = Room.create(barcode="center", title="The center")
    center.coordinates.update(0, 0, 0)
    center.coordinates.x = 2
    db.clear_cache()
    center = Room.get(id=center.id)
    assert center.coordinates.x == 2


def test_distance_from_tuple(db):
    """Measure the distance between locations as tuples."""
    db.bind({Coordinates, Room})
    center = Room.create(barcode="center", title="The center")
    center.coordinates.update(0, 0, 0)

    distances = {
        (1, 0, 0): 1,
        (0, 1, 0): 1,
        (0, 0, 3): 3,
    }

    for tup, distance in distances.items():
        assert center.coordinates.distance(tup) == distance


def test_distance_from_node(db):
    """Measure the distance between locations as rooms (nodes)."""
    db.bind({Coordinates, Room})
    center = Room.create(barcode="center", title="The center")
    center.coordinates.update(0, 0, 0)
    east = Room.create(barcode="east", title="The eastern room")
    east.coordinates.update(1, 0, 0)
    north = Room.create(barcode="north", title="The northern room")
    north.coordinates.update(0, 1, 0)
    up = Room.create(barcode="up", title="The up room")
    up.coordinates.update(0, 0, 3)

    distances = {
        east: 1,
        north: 1,
        up: 3,
    }

    for room, distance in distances.items():
        assert center.coordinates.distance(room) == distance


def test_valid_get_at_from_cache(db):
    """Getting a room (node) at valid coordinates should succeed."""
    db.bind({Coordinates, Room})
    center = Room.create(barcode="center", title="The center")
    center.coordinates.update(0, 0, 0)
    east = Room.create(barcode="east", title="The eastern room")
    east.coordinates.update(1, 0, 0)
    north = Room.create(barcode="north", title="The northern room")
    north.coordinates.update(0, 1, 0)
    assert center.coordinates.get_at(0, 1, 0) is north


def test_invalid_get_at_from_cache(db):
    """Getting a room (node) at invalid coordinates should yield None."""
    db.bind({Coordinates, Room})
    center = Room.create(barcode="center", title="The center")
    center.coordinates.update(0, 0, 0)
    east = Room.create(barcode="east", title="The eastern room")
    east.coordinates.update(1, 0, 0)
    north = Room.create(barcode="north", title="The northern room")
    north.coordinates.update(0, 1, 0)
    assert center.coordinates.get_at(0, 2, 0) is None


def test_valid_get_at_from_DB(db):
    """Getting a room (node) at valid coordinates from DB should succeed."""
    db.bind({Coordinates, Room})
    center = Room.create(barcode="center", title="The center")
    center.coordinates.update(0, 0, 0)
    east = Room.create(barcode="east", title="The eastern room")
    east.coordinates.update(1, 0, 0)
    north = Room.create(barcode="north", title="The northern room")
    north.coordinates.update(0, 1, 0)
    db.clear_cache()
    center = Room.get(id=center.id)
    north = Room.get(id=north.id)
    assert center.coordinates.get_at(0, 1, 0) is north


def test_invalid_get_at_from_DB(db):
    """Getting a room (node) at invalid coordinates from DB should fail."""
    db.bind({Coordinates, Room})
    center = Room.create(barcode="center", title="The center")
    center.coordinates.update(0, 0, 0)
    east = Room.create(barcode="east", title="The eastern room")
    east.coordinates.update(1, 0, 0)
    north = Room.create(barcode="north", title="The northern room")
    north.coordinates.update(0, 1, 0)
    db.clear_cache()
    center = Room.get(id=center.id)
    assert center.coordinates.get_at(0, 2, 0) is None


def test_valid_get_at_after_update_from_DB(db):
    """Getting a room (node) at valid coordinates after update should succeed."""
    db.bind({Coordinates, Room})
    center = Room.create(barcode="center", title="The center")
    center.coordinates.update(0, 0, 0)
    east = Room.create(barcode="east", title="The eastern room")
    east.coordinates.update(1, 0, 0)
    north = Room.create(barcode="north", title="The northern room")
    north.coordinates.update(0, 1, 0)
    db.clear_cache()
    center = Room.get(id=center.id)
    north = Room.get(id=north.id)
    north.coordinates.update(0, 2, 0)
    assert center.coordinates.get_at(0, 2, 0) is north


def test_around_radius(db):
    """Retrieve the rooms (nodes) around coordinates."""
    db.bind({Coordinates, Room})
    center = Room.create(barcode="center", title="The center")
    center.coordinates.update(0, 0, 0)
    east = Room.create(barcode="east", title="The eastern room")
    east.coordinates.update(1, 0, 0)
    north = Room.create(barcode="north", title="The northern room")
    north.coordinates.update(0, 1, 0)
    northeast = Room.create(barcode="northeast", title="The northeastern room")
    northeast.coordinates.update(1, 1, 0)
    distances = center.coordinates.around(1)
    close = [room for _, room in distances]
    assert east in close
    assert north in close
    assert northeast not in close


def test_around_order(db):
    """Retrieve the order of rooms (nodes) around coordinates."""
    db.bind({Coordinates, Room})
    center = Room.create(barcode="center", title="The center")
    center.coordinates.update(0, 0, 0)
    east = Room.create(barcode="east", title="The eastern room")
    east.coordinates.update(1, 0, 0)
    north = Room.create(barcode="north", title="The northern room")
    north.coordinates.update(0, 1, 0)
    northeast = Room.create(barcode="northeast", title="The northeastern room")
    northeast.coordinates.update(1, 1, 0)
    distances = center.coordinates.around(1.5)
    close = [room for _, room in distances]
    assert close.index(east) < close.index(northeast)


def test_project(db):
    """Test to project."""
    db.bind({Coordinates, Room})
    east = Room.create(barcode="east", title="The east")
    east.coordinates.update(1, 0, 0)
    coordinates = (
        (Direction.EAST, 2, 0, 0),
        (Direction.SOUTHEAST, 2, -1, 0),
        (Direction.SOUTH, 1, -1, 0),
        (Direction.SOUTHWEST, 0, -1, 0),
        (Direction.WEST, 0, 0, 0),
        (Direction.NORTHWEST, 0, 1, 0),
        (Direction.NORTH, 1, 1, 0),
        (Direction.NORTHEAST, 2, 1, 0),
        (Direction.DOWN, 1, 0, -1),
        (Direction.UP, 1, 0, 1),
    )

    for direction, x, y, z in coordinates:
        assert east.coordinates.project(direction) == (x, y, z)
