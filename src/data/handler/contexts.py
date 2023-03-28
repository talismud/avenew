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

"""Context handler, to store contexts on the character."""

from context.base import Context, CONTEXTS
from data.handler.abc import BaseHandler


class ContextHandler(BaseHandler):

    """An extended list of contexts for a character."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._contexts = []

    def __iter__(self):
        self._put_at_least_one()
        contexts = [ctx for ctx in self._contexts if ctx is not ...]
        return iter(contexts)

    def __str__(self):
        active = self.active
        names = [f"{'*' if ctx is active else ''}{ctx!r}" for ctx in self]
        return f"[{' ,'.join(names)}]"

    @property
    def active(self):
        """Return the active context."""
        self._put_at_least_one()
        index = self._contexts.index(...)

        # Ellipsis is before the active context.
        return self._contexts[index + 1]

    def add(
        self,
        context_path: str,
        options: dict | None = None,
        active: bool = True,
        silent: bool = False,
    ):
        """Add a new context at the top of the stack.

        This context will become the active one if `active` is set
        to `True` (the default).

        Args:
            context_path (str): the path leading to the context.
            options (dict, optional): the context options.
            active (bool, optional): whether this context should become
                the active one (`True` by default).
            silent (bool): if set to `True`, do not call the new context's
                    `enter` method, which might display text.

        """
        self._put_at_least_one()
        context_cls = CONTEXTS.get(context_path)
        if context_cls is None:
            raise ValueError(f"can't find this context: {context_path!r}")

        # Create the new context, so an exception wouldn't save anything.
        character, _ = self.model
        if character is None:
            raise ValueError("no character defined for this context stack")

        new_context = context_cls(None, character, options)

        # Call `enter`.
        if not silent:
            new_context.enter()

        # Remove the active context if appropriate.
        if active:
            while ... in self._contexts:
                self._contexts.remove(...)

        # Add the new context.
        self._contexts.insert(0, new_context)

        # Set this new context to active if appropriate.
        if active:
            self._contexts.insert(0, ...)

        self.save()
        return new_context

    def remove(self, context: Context, silent: bool = False):
        """Remove a context from the context stack.

        To remove a context, specify the context to remove (the context
        object) as argumment.

        If the removed context is the active one, the next in the stack
        will become active.

        Args:
            contexx (Context): the context to remove.
            silent (bool): if set to `True`, do not call the context's
                    `leave` method, which might display text.


        If no context match, raise a ValueError exception.

        """
        self._put_at_least_one()
        if context in self._contexts:
            if not silent:
                context.leave()

            index = self._contexts.index(context)
            del self._contexts[index]
            self.save()
        else:
            raise ValueError("this context isn't present in the context stack")

    def handle_input(self, user_input: str):
        """Find the proper context and send the input to it.

        Args:
            user_input (str): the input to process.

        This method is responsible for selecting the proper context,
        parsing the "change context" characters and handing the input
        to the context.

        """
        active = self.active
        return active.handle_input(user_input)

    def _put_at_least_one(self):
        if not self._contexts:
            context_cls = CONTEXTS["character.game"]
            character, _ = self.model
            new_context = context_cls(None, character)
            self._contexts.insert(0, new_context)
            self._contexts.insert(0, ...)
            object.__setattr__(self, "_default_context", new_context)
