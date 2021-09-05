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
from typing import List, Optional, TYPE_CHECKING

import logging
import asyncpg

from discord import abc

if TYPE_CHECKING:
    from aperture import ApertureBot


log = logging.getLogger('aperture.core.cache')


class Prefix(dict):
    def __init__(self, bot: ApertureBot) -> None:
        super().__init__()
        self.bot = bot

    async def get_or_fetch(self, guild: abc.Snowflake) -> Optional[str]:
        prefix = super().get(guild.id)
        if prefix:
            return prefix

        query = 'SELECT * FROM prefixes WHERE guild_id=$1;'
        data: asyncpg.Record = await self.bot.database.fetchrow(query, guild.id)
        if data:
            self.__dict__[guild.id] = data['prefix']
            return data['prefix']

        return None

    async def insert(self, prefix: str, guild: abc.Snowflake) -> None:
        query = 'INSERT INTO prefixes (prefix, guild_id) VALUES ($1, $2);'
        await self.bot.database.execute(query, prefix, guild.id)

        self.__dict__[guild.id] = prefix

        log.debug('Prefix %s added for Guild ID: %s', prefix, guild.id)

    async def remove(self, guild: abc.Snowflake) -> None:
        query = 'DELETE FROM prefixes WHERE guild_id=$1;'
        await self.bot.database.execute(query, guild.id)

        # Safe Mode: If the prefix is not in cache (like in the case mentioned in bot.get_prefix),
        # we don't need to raise any Exception
        self.__dict__.pop(guild.id, None)

        log.debug('Prefix removed for Guild ID: %s', guild.id)

    async def fill(self) -> None:
        data: List[asyncpg.Record] = await self.bot.database.fetch('SELECT guild_id, prefix FROM prefixes;')
        for row in data:
            self.__dict__[row['guild_id']] = row['prefix']
        log.debug('Filled prefix cache')
