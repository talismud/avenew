import pytest

from data.base.coordinates import Coordinates
from data.base.model import Field
from data.direction import Direction
from data.exit import Exit
from data.handler.coordinates import CoordinateHandler
from data.room import Room


class RoomWithCoordinates(Room):

    coordinates: CoordinateHandler = Field(default_factory=CoordinateHandler)


def test_next_barcode(db):
    db.bind({Room})
    barcodes = (
        ("demo_1", "demo_2"),
        ("demo_3", "demo_2"),
        ("demo_", "demo_2"),
        ("harl:1", "harl:2"),
        ("harl:2", "harl:3"),
    )

    for barcode, next_barcode in barcodes:
        room = Room.create(barcode=barcode)
        assert room.find_next_barcode(barcode) == next_barcode


def test_create_neighbor(db):
    db.bind({Exit, Room})
    room = Room.create(barcode="demo_1")
    other = room.create_neighbor(Direction.EAST)
    assert other.barcode == "demo_2"


def test_create_neighbor_with_coordinates(db):
    db.bind({Coordinates, Exit, RoomWithCoordinates})
    room = RoomWithCoordinates.create(barcode="demo_1")
    room.coordinates.update(0, 0, 0)
    other = room.create_neighbor(Direction.EAST)
    assert other.coordinates.x == 1
    assert other.coordinates.y == 0
    assert other.coordinates.z == 0
