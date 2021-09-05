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
from typing import List, Optional, Tuple, TYPE_CHECKING

from collections import UserList
import logging

from discord import abc
from discord.ext import commands, tasks

if TYPE_CHECKING:
    from aperture import ApertureBot


log = logging.getLogger('aperture.core.cache')


class CommandUsage(UserList):
    """``Note``: This list contains only the statistics of last 30 seconds since we run a task
    which put the statistics into the Database after every 30 seconds and clears the cache
    for memory optimisation and persistency.
    """

    def __init__(self, bot: ApertureBot) -> None:
        super().__init__()
        self.bot = bot

    async def add(
        self,
        command: commands.Command,
        command_type: int,
        user: abc.Snowflake,
        guild: Optional[abc.Snowflake]
    ):
        self.data.append(
            {
                'name': command.name,
                'type': command_type,
                'user_id': user.id,
                'guild_id': guild.id if guild is not None else None
            }
        )

    @tasks.loop(seconds=30)
    async def dump_in_database(self):
        if self.data:
            # Make a copy of the dict and instantly clear the original to prevent 
            # inconsistency of stats because of time taken by database
            stats = self.data
            self.data.clear()

            values: List[Tuple[str, int, int, Optional[int]]] = []
            for usage in stats:
                values.append((usage['name'], usage['type'], usage['user_id'], usage['guild_id']))

            await self.bot.database.executemany(
                'INSERT INTO command_stats (name, type, user_id, guild_id) VALUES ($1, $2, $3, $4);', values
            )
            log.debug('Dumped command stats into database and cleared it\'s cache')
