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

# Forbidden combinations.
FORBIDDEN = [f"{i}{i + 1}{i + 2}" for i in range(0, 8)]
FORBIDDEN += [f"{i}{i - 1}{i - 2}" for i in range(2, 10)]


class PhoneNumberGenerator(RandomGenerator):

    patterns = (
        "5",
        "5",
        "9",
        "-",
        "23456789",
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
        "no_more_than_three_same_digits",
        "no_scale_patterns",
        "no_x11_in_central_office_code",
    )

    @classmethod
    def check_no_three_following_digits(cls, code: str) -> bool:
        """Check that no three numbers follow in a row."""
        code = code.replace("-", "")
        allowed = True
        if len(code) >= 3:
            last = code[-1]
            allowed = not code.endswith(last * 3)

        return allowed

    @classmethod
    def check_no_more_than_three_same_digits(cls, code: str) -> bool:
        """Check that the same digit is present no more than 3 times."""
        code = code.replace("-", "")
        return code.count(code[-1]) < 4 if code else True

    @classmethod
    def check_no_scale_patterns(cls, code: str) -> bool:
        """Avoid scale patterns (123, 321...)."""
        code = code.replace("-", "")
        return all(not code.endswith(scale) for scale in FORBIDDEN)

    @classmethod
    def check_no_x11_in_central_office_code(cls, code: str) -> bool:
        """The Central Office Code shouldn't end with 11."""
        return not (len(code) == 3 and code.endswith("11"))
