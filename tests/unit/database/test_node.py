import pytest

from data.base.node import Node


class User(Node):

    name: str = "not yet"


class Account(Node):

    pass


def test_create(db):
    db.bind({User})
    vincent = User.create(name="Vincent")
    assert vincent.id
    assert vincent.name == "Vincent"


def test_count(db):
    db.bind({User})
    assert User.count() == 0


def test_create_and_count(db):
    db.bind({User, Account})
    for i in range(3):
        User.create(name=str(i))
        Account.create()

    assert User.count() == 3


def test_create_and_retrieve_from_cache(db):
    db.bind({User})
    vincent = User.create(name="Vincent")
    user = User.get(id=vincent.id)
    assert user is vincent


def test_create_and_retrieve_from_db(db):
    db.bind({User})
    vincent = User.create(name="Vincent")
    db.cache.clear()
    user = User.get(id=vincent.id)
    assert user is not vincent
    assert user.id == vincent.id
    assert user.name == vincent.name


def test_create_and_update(db):
    db.bind({User})
    vincent = User.create(name="Vincent")
    vincent.name = "Mark"
    assert vincent.name == "Mark"


def test_create_and_updateand_receive_from_cache(db):
    db.bind({User})
    vincent = User.create(name="Vincent")
    vincent.name = "Mark"
    user = User.get(id=vincent.id)
    assert user.name == "Mark"


def test_create_and_updateand_receive_from_db(db):
    db.bind({User})
    vincent = User.create(name="Vincent")
    vincent.name = "Mark"
    db.cache.clear()
    user = User.get(id=vincent.id)
    assert user.name == "Mark"


def test_create_and_delete_and_retrieve_From_cache(db):
    db.bind({User})
    vincent = User.create(name="Vincent")
    User.delete(vincent)

    with pytest.raises(ValueError):
        User.get(id=vincent.id)


def test_create_and_delete_and_retrieve_From_db(db):
    db.bind({User})
    vincent = User.create(name="Vincent")
    User.delete(vincent)
    db.cache.clear()

    with pytest.raises(ValueError):
        User.get(id=vincent.id)


def test_create_and_get_all(db):
    db.bind({User})
    vincent = User.create(name="Vincent")
    vanessa = User.create(name="Vanessa")
    anthony = User.create(name="Anthony")
    results = User.all()
    assert vincent in results
    assert vanessa in results
    assert anthony in results
