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

"""Module containing the definition for a generic blueprint."""

from pathlib import Path
from typing import Any, Sequence

from data.blueprints.abc import BlueprintMetaclass
from data.handler.abc import BaseHandler
from tools.logging.frequent import FrequentLogger

logger = FrequentLogger("world")
logger.setup()


class Blueprint:

    """A blueprint object, containing world definitions."""

    def __init__(
        self,
        unique_name: str,
        file_path: Path,
        content: Sequence[dict[str, Any]],
    ):
        self.unique_name = unique_name
        self.file_path = file_path
        self.content = content

    def apply(self):
        """Apply the entire blueprints, except to delays."""
        self._apply(True)

    def complete(self):
        """Apply only the delayed documents."""
        self._apply(False)

    def _apply(self, to_delay: bool) -> None:
        """Apply the entire blueprint."""
        for definition in self.content:
            definition = definition.copy()
            d_type = definition.pop("type", None)
            if d_type is None:
                logger.warning(
                    f"This blueprint definition has no type: {definition}"
                )
                continue

            if d_type not in BlueprintMetaclass.models:
                logger.warning("Unknown type: {d_type}")
                continue

            schema = BlueprintMetaclass.models[d_type]
            model = schema.model
            keys = {}
            for field in model.__fields__.values():
                if field.field_info.extra.get("bpk", False):
                    value = definition.get(field.name, ...)
                    if value is ...:
                        continue

                    keys[field.name] = value

            if not keys:
                logger.warning(
                    f"No blueprint key was identified for {definition}"
                )
                continue

            # Try to get the object from the database.
            obj = model.get(raise_not_found=False, **keys)
            path = model.class_path
            if obj is not None:
                logger.debug(f"{path} {obj} was found and will be updated.")

                for key, value in definition.items():
                    if not to_delay and key not in schema.to_delay:
                        continue

                    if to_delay and key in schema.to_delay:
                        continue

                    if key in schema.special:
                        continue

                    field = model.__fields__[key]
                    if issubclass(field.type_, BaseHandler):
                        getattr(obj, key).from_blueprint(value)
                    else:
                        setattr(obj, key, value)
            else:
                # The object will be created.
                logger.debug(f"Attempting to create {keys}")
                safe, handlers = {}, {}
                for field in model.__fields__.values():
                    value = definition.get(field.name, ...)
                    if value is ...:
                        continue

                    if issubclass(field.type_, BaseHandler):
                        handlers[field.name] = value
                    else:
                        safe[field.name] = value

                try:
                    obj = model.create(**safe)
                except Exception:
                    logger.exception(
                        f"An error occurred while creating {path}:"
                    )

                # Update the handler values.
                for key, value in handlers.items():
                    if not to_delay and key not in schema.to_delay:
                        continue

                    if to_delay and key in schema.to_delay:
                        continue

                    getattr(obj, key).from_blueprint(value)

            # Take care of the special attributes.
            for name in schema.special:
                if not to_delay and name not in schema.to_delay:
                    continue

                if to_delay and name in schema.to_delay:
                    continue

                method_name = f"update_{name}"
                method = getattr(schema, method_name, None)
                if method is None:
                    logger.error(
                        f"{name!r} is a special case for {model}, "
                        f"but there is no method {method_name!r} in {schema}"
                    )

                special = definition.pop(name, ...)
                if special is not ...:
                    method(logger, obj, special)

            # Add the blueprint to this object.
            obj.blueprints.add(self)
