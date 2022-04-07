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

"""MudIO service, set to handle input/output on the game level"""

import asyncio
from collections import defaultdict
from importlib import import_module
from pathlib import Path
from typing import Optional

from context.base import Context, CONTEXTS
from context.log import logger
from data.session import Session, OUTPUT_QUEUE
from service.base import BaseService


class Service(BaseService):

    """MudIO service, to handle input/output of users.

    Users, in this context, are players (either just connected,
    interacting through a session, or already playing, interacting through
    a character object).  Input is handled here, as well as output
    from the game to users.

    """

    name = "mudIO"

    async def init(self):
        """Asynchronously initialize the service.

        This method should be overridden in subclasses.  It is called by
        `start`` before sub-services are created.  It plays the role of
        an asynchronous constructor for the service, and service attributes
        often are created there for consistency.

        """
        self.output_lock = asyncio.Lock()
        self.contexts = {}

    async def setup(self):
        """Set the MudIO up."""
        self.load_contexts()

    async def cleanup(self):
        """Clean the service up before shutting down."""

    def load_contexts(self):
        """Load the contexts dynamically.

        This method is called when the game starts.

        """
        parent = Path()
        paths = (parent / "context",)

        exclude = (
            parent / "context" / "base.py",
            parent / "context" / "log.py",
        )
        forbidden = (Context,)

        # Search the context files.
        logger.debug("Preparing to load all contexts...")
        loaded = 0
        for path in paths:
            for file_path in path.rglob("*.py"):
                if file_path in exclude or any(
                    to_ex in file_path.parents for to_ex in exclude
                ):
                    continue

                # Search for the module to begin
                if file_path.name.startswith("_"):
                    continue

                # Assume this is a module containing ONE context.
                relative = file_path.relative_to(path)
                pypath = ".".join(file_path.parts)[:-3]
                py_unique = ".".join(relative.parts)[:-3]

                # Try to import it.
                try:
                    module = import_module(pypath)
                except Exception:
                    logger.exception(
                        f"  An error occurred when importing {pypath}:"
                    )
                    continue

                # Explore the module to try to import ONE context.
                NewContext = None
                for name, value in module.__dict__.items():
                    if name.startswith("_"):
                        continue

                    if (
                        isinstance(value, type)
                        and value not in forbidden
                        and issubclass(value, Context)
                    ):
                        if value.__module__ != pypath:
                            continue

                        if NewContext is not None:
                            NewContext = ...
                            break
                        else:
                            NewContext = value

                if NewContext is None:
                    logger.warning(f"No context could be found in {pypath}.")
                    continue
                elif NewContext is ...:
                    logger.warning(
                        "More than one contexts are present "
                        f"in module {pypath}, not loading any."
                    )
                    continue
                else:
                    loaded += 1
                    logger.debug(
                        f"  Load the context in {pypath} (name={py_unique!r})"
                    )
                    self.contexts[py_unique] = NewContext
                    NewContext.pyname = py_unique

        s = "s" if loaded > 1 else ""
        was = "were" if loaded > 1 else "was"
        logger.debug(f"{loaded} context{s} {was} loaded successfully.")
        CONTEXTS.clear()
        CONTEXTS.update(self.contexts)

    def handle_input(self, session: Session, command: str):
        """Handle input from a session.

        Args:
            session (Session): the session sending input.
            command (str): the sent command as a string.

        """
        data = self.parent.data
        context = session.context
        context.handle_input(command)

    async def send_output(self, input_id: Optional[int] = None):
        """Send output synchronously."""
        host = self.parent.host
        data = self.parent.data
        to_send = defaultdict(list)

        async with self.output_lock:
            while not OUTPUT_QUEUE.empty():
                ssid, msg = OUTPUT_QUEUE.get_nowait()
                to_send[ssid].append(msg)

            # At this point, messages have been sorted by session.
            for ssid, messages in to_send.items():
                session = data.get_session(ssid)
                msg = b"\n".join(messages)

                # Display the context prompt.
                prompt = session.context.get_prompt()
                if isinstance(prompt, str):
                    prompt = prompt.encode("utf-8")

                if prompt:
                    msg = msg + b"\n\n" + prompt

                # Send the output to the session.
                await host.send_cmd(
                    host.writer,
                    "output",
                    dict(
                        session_id=session.uuid,
                        output=msg,
                        input_id=input_id,
                    ),
                )
