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

from string import digits

from tools.generator import RandomGenerator

"""Module containing the phone number generator."""


class PhoneNumberGenerator(RandomGenerator):

    patterns = (
        "5",
        "5",
        "6789",
        "-",
        digits,
        digits,
        digits,
        "-",
        digits,
        digits,
        digits,
        digits,
    )

    checks = (
        "no_three_following_digits",
        "no_more_than_four_same_digits",
        "no_scale_patterns",
    )

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

    @classmethod
    def check_no_scale_patterns(cls, code: str) -> bool:
        """Avoid scale patterns (123, 321...)."""
        code = code.replace("-", "")
        forbidden = [f"{i}{i + 1}{i + 2}" for i in range(1, 8)]
        forbidden += [f"{i}{i - 1}{i - 2}" for i in range(3, 10)]
        return all(scale not in code for scale in forbidden)
