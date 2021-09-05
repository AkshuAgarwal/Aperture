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
from typing import Any, Iterable, List, Optional, Sequence

import os
import sys
import asyncio
import asyncpg
import logging
import traceback


log = logging.getLogger('aperture.core.database')


class ApertureDatabase:
    def __init__(self) -> None:
        self.pool: Optional[asyncpg.Pool] = None

    def create_pool(self, loop: Optional[asyncio.AbstractEventLoop] = None) -> asyncpg.Pool:
        if not loop:
            loop = asyncio.get_event_loop()

        DSN = os.getenv('POSTGRES_URL')
        kwargs = {
            'command_timeout': 60,
            'min_size': 20,
            'max_size': 20
        }
        try:
            pool: asyncpg.Pool = loop.run_until_complete(asyncpg.create_pool(DSN, **kwargs))
            log.debug('Created database pool')
            self.pool = pool
            return pool

        except Exception as e:
            traceback.print_exception(type(e), e, e.__traceback__, file=sys.stderr)
            raise RuntimeError('Failed to create database pool. Exiting...')

    async def close_pool(self):
        if self.pool is not None:
            await self.pool.close()
            log.debug('Closed database pool')

    async def execute(self, query: str, *args: Any) -> str:
        return await self.pool.execute(query, *args)

    async def executemany(self, query: str, args: Iterable[Sequence], timeout: Optional[float] = None):
        return await self.pool.executemany(query, args, timeout=timeout)

    async def fetch(self, query: str, *args: Any, timeout: Optional[float] = None) -> List[asyncpg.Record]:
        return await self.pool.fetch(query, *args, timeout=timeout)

    async def fetchrow(self, query: str, *args: Any, timeout: Optional[float] = None) -> Optional[asyncpg.Record]:
        return await self.pool.fetchrow(query, *args, timeout=timeout)
