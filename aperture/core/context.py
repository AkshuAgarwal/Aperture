"""
Aperture - A Multi-Purpose Discord Bot
Copyright (C) 2021-present  AkshuAgarwal

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""

from __future__ import annotations
from typing import Any, Optional, TYPE_CHECKING

from discord.ext import commands

if TYPE_CHECKING:
    from discord import Message
    from aperture import ApertureBot

class ApertureContext(commands.Context['ApertureBot']):
    async def reply(self, content: Optional[str] = None, **kwargs: Any) -> Message:
        if not kwargs.get('mention_author', None):
            kwargs['mention_author'] = False

        return await super().reply(content=content, **kwargs)
