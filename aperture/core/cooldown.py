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
from typing import TYPE_CHECKING, Optional

from discord.ext import commands

if TYPE_CHECKING:
    from discord import Message
    from aperture import ApertureBot

class ApertureCooldown:
    def __init__(self, bot: ApertureBot, **kwargs: commands.Cooldown) -> None:
        self.bot = bot

        for cooldown in kwargs.values():
            if not isinstance(cooldown, commands.Cooldown):
                raise TypeError(f'Expected Cooldown in keyword arguments but got {cooldown.__class__.__name__!r}')
        self.kwargs = kwargs

    def default_cooldown(self, message: Message) -> Optional[commands.Cooldown]:
        """Required Cooldowns: `premium_cooldown`, `normal_cooldown`"""

        # Bypass cooldown for bot owner
        if message.author.id == self.bot.owner_id or message.author.id in self.bot.owner_ids:
            return None

        # Returns shorter cooldowns for premium users and guilds
        if message.author.id in self.bot.cache.premium.users:
            return self.kwargs.get('premium_cooldown')

        if message.guild is not None and message.guild.id in self.bot.cache.premium.all:
            return self.kwargs.get('premium_cooldown')

        return self.kwargs.get('normal_cooldown')
