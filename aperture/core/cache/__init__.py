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
from typing import TYPE_CHECKING

import logging

from .prefix import Prefix
from .blacklist import Blacklist
from .premium import Premium
from .command_usage import CommandUsage

if TYPE_CHECKING:
    from aperture import ApertureBot


log = logging.getLogger('aperture.core.cache')


class ApertureCache:
    def __init__(self, bot: ApertureBot) -> None:
        self.bot = bot

        self.prefix = Prefix(bot)
        self.blacklist = Blacklist(bot)
        self.premium = Premium(bot)
        self.command_usage = CommandUsage(bot)

    async def fill_cache(self) -> None:
        await self.prefix.fill()
        await self.blacklist.fill()
        await self.premium.fill()
        log.info('Filled bot cache from the database')

    async def start_cache_tasks(self) -> None:
        """Starts all the task"""
        # We don't start our tasks here since we also need to close them on shutdown,
        # and to keep consistency, we'll start it in main bot subclass
        self.command_usage.dump_task.start()
        log.debug('Cache routine tasks started')

    async def stop_cache_tasks(self) -> None:
        # Stopping allows tasks to complete their current running iteration, so it may take time for the tasks to stop.
        self.command_usage.dump_task.stop()
        log.debug('Cache routine tasks stopepd')
