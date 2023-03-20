import string

import pytest

from data.generator import Generator
from tools.generator import RandomGenerator

class LittleGenerator(RandomGenerator):

    """A little generator with only three patterns and no rules."""

    patterns = (
        "01",
        "01",
        "AB",
    )


def test_generate_without_rules(db):
    db.bind({Generator})
    codes = []
    for _ in range(8):
        code = LittleGenerator.generate()
        assert len(code) == 3
        assert code[0] in "01"
        assert code[1] in "01"
        assert code[2] in "AB"
        assert code not in codes
        codes.append(code)


def test_generate_overflow_without_rules(db):
    db.bind({Generator})
    for _ in range(8):
        LittleGenerator.generate()

    with pytest.raises(ValueError):
        LittleGenerator.generate()


def test_record_and_generate_without_rules(db):
    db.bind({Generator})
    prior = "01A"
    LittleGenerator.record(prior)
    codes = []
    for _ in range(7):
        code = LittleGenerator.generate()
        assert len(code) == 3
        assert code[0] in "01"
        assert code[1] in "01"
        assert code[2] in "AB"
        assert code not in codes
        assert code != prior
        codes.append(code)


def test_record_and_generate_overflow_without_rules(db):
    db.bind({Generator})
    LittleGenerator.record("01A")
    for _ in range(7):
        LittleGenerator.generate()

    with pytest.raises(ValueError):
        LittleGenerator.generate()


class LittleGeneratorWithDash(RandomGenerator):

    """A little generator with only three patterns and no rules."""

    patterns = (
        "01",
        "01",
        "-",
        "AB",
    )


def test_generate_without_rules(db):
    db.bind({Generator})
    codes = []
    for _ in range(8):
        code = LittleGeneratorWithDash.generate()
        assert len(code) == 4
        assert code[0] in "01"
        assert code[1] in "01"
        assert code[2] == "-"
        assert code[3] in "AB"
        assert code not in codes
        codes.append(code)


class PhoneNumberGenerator(RandomGenerator):

    """A random phone generator.

    A phone number shouldn't have more than twice the same digit in a row.

    """

    patterns = (
        string.digits,
        string.digits,
        string.digits,
        "-",
        string.digits,
        string.digits,
        string.digits,
        string.digits,
    )

    @classmethod
    def is_allowed(cls, code: str) -> bool:
        """Return whether this code is allowed (only check the end)."""
        allowed = True
        if len(code) >= 3:
            last = code[-1]
            allowed = not code.endswith(last * 3)

        return allowed


def test_generate_with_rules(db):
    db.bind({Generator})
    numbers = []
    for _ in range(100):
        number = PhoneNumberGenerator.generate()
        assert number not in numbers
        numbers.append(number)

    for number in numbers:
        for i, digit in enumerate(number):
            assert not number[i:].startswith(digit * 3)


class PhoneNumberGeneratorWithChecks(RandomGenerator):

    """A random phone generator.

    A phone number shouldn't have more than twice the same digit in a row.

    """

    patterns = (
        string.digits,
        string.digits,
        string.digits,
        "-",
        string.digits,
        string.digits,
        string.digits,
        string.digits,
    )

    checks = ("no_three_following_digits", "no_more_than_four_same_digits")

    @classmethod
    def check_no_three_following_digits(cls, code: str) -> bool:
        """Return whether this code is allowed (only check the end)."""
        allowed = True
        if len(code) >= 3:
            last = code[-1]
            allowed = not code.endswith(last * 3)

        return allowed

    @classmethod
    def check_no_more_than_four_same_digits(cls, code: str) -> bool:
        """check that the same digit is present no more than 4 times."""
        return all(code.count(char) < 4 for char in code if char.isdigit())


def test_generate_with_checks(db):
    db.bind({Generator})
    numbers = []
    for _ in range(100):
        number = PhoneNumberGeneratorWithChecks.generate()
        assert number not in numbers
        numbers.append(number)

    for number in numbers:
        for i, digit in enumerate(number):
            assert not number[i:].startswith(digit * 3)
            if digit.isdigit():
                assert number.count(digit) < 4
