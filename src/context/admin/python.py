# Copyright (c) 2022, LE GOFF Vincent
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

"""Display a Python console for administrators."""

from code import InteractiveConsole
from io import StringIO
import sys

from context.base import Context
from tools.picklable import picklable_dict


class Py(Context):

    """Context displaying a Python console for administrators.

    Input:
        <python code>: Python code to execute.

    """

    text = """
        TalisMUD Python console.
        Python {version} on {platform}.

        Type `q` to leave this console and go back to the game.

        You can also use these variables (plus any you create):
            self: the character calling this Python console.
    """

    def __init__(self, session, character, options):
        super().__init__(session, character, options)
        self.buffer = ""
        self.console = None
        self.completed = True

    def __getstate__(self):
        state = dict(self.__dict__)
        state.pop("console", None)
        variables = dict(state["options"].get("variables", {}))
        variables.pop("__builtins__", None)
        state["options"]["variables"] = picklable_dict(variables)
        return state

    def greet(self) -> str:
        """Return the text when greeting the character in this context."""
        return self.text.format(version=sys.version, platform=sys.platform)

    def leave(self):
        """Leave this context."""
        self.msg("Closing the Python console.")

    def input_q(self):
        """When the user enters 'q', quit this conext."""
        self.session.character.contexts.remove(self)
        return True

    def press_return(self):
        """Return is pressed without any input."""
        return self.other_input("")

    def other_input(self, line: str):
        """Handle user input."""
        # Create a console, if there's none.
        if getattr(self, "console", None) is None:
            variables = self.options.get("variables", {})
            variables["self"] = self.character
            variables.update(type(self).service.parent.console.locals)
            self.console = InteractiveConsole(variables)
            # Push the buffer.
            self.console.push(self.buffer)

        if self.buffer:
            self.buffer += "\n"
        self.buffer += line

        # Wrap the standard output and error in a StringIO.
        out = StringIO()
        stdout, stderr = sys.stdout, sys.stderr
        sys.stdout = out
        sys.stderr = out

        # Try to execute the line.
        self.completed = True
        more = self.console.push(line)
        sys.stdout = stdout
        sys.stderr = stderr
        if more:
            self.completed = False
        else:
            self.buffer = ""

        out.seek(0)
        self.msg(f"{out.read()}")
        self.character.contexts.save()

        return True

    def get_prompt(self):
        """Return the prompt to be displayed."""
        return ">>>" if self.completed else "..."
