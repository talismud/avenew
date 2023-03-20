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

"""Module containing the RandomGenerator class.

A random generator is used to create unique, semi-random numbers
following specific constraints.  To use it, create a subclass of
`tools.generator.RandomGenerator` with rules.

Here is an example of a phone number generator that should generate
7 numbers with a dash between the third and fourth.  A phone number
cannot contain three times the same digit in a row:

```
import string
from tool.generator import RandomGenerator

class PhoneNumberGenerator(RandomGenerator):

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
        '''Return whether this code is allowed (only check the end).'''
        allowed = True
        if len(code) >= 3:
            last = code[-1]
            allowed = not code.endswith(last * 3)

        return allowed
```

It is then simple to use:

```
from ... import PhoneNumberGenerator

unique = PhoneNumberGenerator.generate()
# > 551-3722
unique = PhoneNumberGenerator.generate()
# > 200-7715
```

Note: a phone number like "111-XXXX" will never be generated, because
it would break the rules.

The `patterns` class attribute should contain a collection of valid
characters for every letter in the code to be generated.  Here,
we have set it to 3 digits, followed by a dash, followed by four digits.
To explain the rules, we set the `next_allowed` method.  It receives
the code being generated (a string of characters of length lower than
the list of patterns) and the set of possibilities.  The set of possibilities
should be altered and returned and a random character from this set
will be chosen.  Hence:

1.  When we call `PhoneNumberGenerator.generate()`, the first character
    is chosen randomly from the first patterns.  Let's say it's "5".
2.  Next, we find the available patterns for the next character:
    all digits are valid.  So we try several codes: what we have
    generated so far ("5") plus all the available options
    ("51", "52", "53"...).  We call `RandomPhoneGenerator.is_allowed()`
    on all of them and only keep the options that
    return `True`.  We randomly select a valid option (say "55").
3.  We repeat the same process: allowed patterns are all digits
    for the next character.  But when we try to see if
    `PhoneNumberGenerator.is_allowed("555")`, we get `False`, indicating
    this is not a valid option.  So we remove "5" from the list of valid
    choices for the next character.  We then select a random number
    from 0 to 4 or 6 to 9.  Let's say "9", so our code for the time
    being is "559".
4.  ... and so on until we have 10 digits.  Notice that
    we didn't take into consideration the dash which
    should be ignored when our rule is selected, but it's easy to add.

Finally, notice that codes shouldn't repeat: once a code is generated,
it cannot be generated again.  Behind the scenes, the generated code
is stored in the database, along with specific portions
of the code.  This is done automatically.

"""

from random import choice

from data.generator import Generator


class RandomGenerator:

    """A random generator of strings following a pattern and set of rules.

    The patterns should be described in the `patterns` class attribute
    as a tuple.  Each element of the tuple should contain the string
    of possible choices for this character.

    The rules can then be customized by overriding the `is_allowed`
    class method.  See the full help in the module.

    """

    patterns = ()
    checks = ()

    @classmethod
    def is_allowed(cls, code: str) -> bool:
        """Return whether this code is allowed.

        It is only necessary to check the end of the code since
        the code is built (with valid parts) from left to right.
        Only the last character of the code is in doubt.

        You can override this method to add rules, but it is advisable
        to define checks (see class help).

        Simply returns `False` if this code isn't valid to implement rules.

        Args:
            code (str): the proposed code (a string).

        Returns:
            allowed (bool): whether this is a valid choice.

        """
        checks = []
        for name in cls.checks:
            method_name = f"check_{name}"
            method = getattr(cls, method_name, None)
            if method is None:
                raise ValueError(
                    "one of the configured checks for this generator, "
                    f"{name!r}, doesn't have a matching method "
                    f"{method_name!r}.  Please add one as a classmethod "
                    "taking one argument besides `cls` (the code to check) "
                    "and returning a boolean"
                )

            checks.append(method(code))

        return all(checks)

    @classmethod
    def generate(cls):
        """Generate a random and unique number.

        The process to generate random numbers is described in the module
        itself.  Existing codes are retrieved from the database.
        Therefore, N read queries will be performed, where N is the number
        of patterns (the number of characters to be generated).
        When choosing a full code however, several write queries
        can be sent to write portions of the generated code.

        """
        code = ""
        trail = []
        while len(code) != len(cls.patterns):
            choices = cls._check_next_from_DB(code)

            # Test allowed options (check the rules).
            for part in tuple(choices):
                if not cls.is_allowed(code + part):
                    choices.discard(part)

            if len(choices) == 0:
                raise ValueError(
                    "no valid code can be generated.  "
                    "This indicates the set of possible patterns "
                    "is used up entirely"
                )

            # Find a random part.  We don't rely on `set.pop`.
            next_part = choice(tuple(choices))
            choices.discard(next_part)
            trail.append((code, choices))
            code += next_part

        cls._save_trail(trail)
        return code

    @classmethod
    def record(cls, code: str):
        """Record a code that shouldn't be generated afterwards.

        Args:
            code (str): the code to record.

        In order to check the validity of this code, the database is read
        for each part.

        Raises:
            ValueError: the code is invalid.

        """
        valid = ""
        trail = []
        while len(valid) != len(cls.patterns):
            choices = cls._check_next_from_DB(valid)

            # Test allowed options (check the rules).
            for part in tuple(choices):
                if not cls.is_allowed(valid + part):
                    choices.discard(part)

            next_part = code[len(valid)]
            if next_part not in choices:
                raise ValueError(
                    f"the next character [{len(valid)}] is not valid: "
                    f"it should be {next_part!r} but only "
                    f"{choices} are allowed"
                )

            choices.discard(next_part)
            trail.append((valid, choices))
            valid += next_part

        cls._save_trail(trail)

    @classmethod
    def _check_next_from_DB(cls, code: str) -> set[str]:
        choices = Generator.select(
            (Generator.table.name == cls.__name__)
            & (Generator.table.current == code)
        )

        if choices:
            choices = set(choices[0].next)
        else:
            choices = set(cls.patterns[len(code)])

        return choices

    @classmethod
    def _save_trail(cls, trail: list[tuple[str, set[str]]]) -> None:
        for code, choices in reversed(trail):
            pattern = cls.patterns[len(code)]

            if len(pattern) > 1:
                # That is forbidden.  But only if there are more than
                # one patterns (otherwise, it's not necessary).
                choices = "".join(sorted(choices))
                exists = Generator.select(
                    (Generator.table.name == cls.__name__)
                    & (Generator.table.current == code)
                )
                if exists:
                    exists[0].next = choices
                else:
                    Generator.create(
                        name=cls.__name__, current=code, next=choices
                    )

            if choices:
                break
