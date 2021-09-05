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
from typing import TYPE_CHECKING, List

import asyncpg
from collections import UserList
import contextlib
import logging

from discord import abc
from aperture.core import error

if TYPE_CHECKING:
    from aperture import ApertureBot


log = logging.getLogger('aperture.core.cache')


class GuildPremium(UserList):
    def __init__(self, bot: ApertureBot) -> None:
        super().__init__()
        self.bot = bot

    async def insert(self, guild: abc.Snowflake) -> None:
        query = 'INSERT INTO guilds_core (guild_id, blacklisted, premium) VALUES ($1, false, true) '\
            'ON CONFLICT (guild_id) DO UPDATE SET premium=true;'
        await self.bot.database.execute(query, guild.id)

        self.data.append(guild.id)

        log.debug('Added guild with ID: %s to premium list', guild.id)

    async def remove(self, guild: abc.Snowflake) -> None:
        query ='UPDATE guilds_core SET premium=false WHERE guild_id=$1;'
        await self.bot.database.execute(query, guild.id)
        
        with contextlib.suppress(ValueError):
            self.data.remove(guild.id)

        log.debug('Removed guild with ID: %s from premium list', guild.id)


class UserPremium(UserList):
    def __init__(self, bot: ApertureBot) -> None:
        super().__init__()
        self.bot = bot

    async def insert(self, user: abc.Snowflake) -> None:
        if user.id in self.data:
            raise error.PremiumBlacklisted(user.id)

        query = 'INSERT INTO users_core (user_id, blacklisted, premium) VALUES ($1, false, true) '\
            'ON CONFLICT (user_id) DO UPDATE SET premium=true;'
        await self.bot.database.execute(query, user.id)

        self.data.append(user.id)

        log.debug('Added user with ID: %s to premium list', user.id)

    async def remove(self, user: abc.Snowflake) -> None:
        query = 'UPDATE users_core SET premium=false WHERE user_id=$1;'
        await self.bot.database.execute(query, user.id)
        
        with contextlib.suppress(ValueError):
            self.data.remove(user.id)

        log.debug('Removed user with ID: %s from premium list', user.id)


class Premium:
    def __init__(self, bot: ApertureBot) -> None:
        self.bot = bot
        self.guilds: List[int] = GuildPremium(bot)
        self.users: List[int] = UserPremium(bot)

    @property
    def all(self) -> List[int]:
        return self.guilds + self.users

    async def fill(self) -> None:
        data: List[asyncpg.Record] = await self.bot.database.fetch('SELECT guild_id FROM guilds_core WHERE premium=true;')
        for row in data:
            self.guilds.append(row['guild_id'])
        data: List[asyncpg.Record] = await self.bot.database.fetch('SELECT user_id FROM users_core WHERE premium=true;')
        for row in data:
            self.users.append(row['user_id'])
        log.debug('Filled premium cache')
