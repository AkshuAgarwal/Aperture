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

import aiohttp
import asyncio
import asyncpg
import itertools
import os
import sys
import yaml
import logging, logging.config
from contextlib import suppress
from datetime import datetime
from dotenv import load_dotenv
from typing import List, Union, Optional

from discord import (
    Message,
    Intents,
    DMChannel,
)
from discord.ext import commands

from aperture.core import CustomContext, error_handler
from aperture.core.error import SettingsError


log = logging.getLogger(__name__)

if not os.path.exists('./tmp'):
    os.makedirs('./tmp')
    print('Created directory "tmp" in the project root directory')

with open('./logging.yaml', 'r', encoding='UTF-8') as stream:
    log_config = yaml.load(stream, Loader=yaml.FullLoader)
    logging.config.dictConfig(log_config)

with open('./settings.yaml', 'r', encoding='utf-8') as file:
    settings = yaml.load(file, Loader=yaml.FullLoader)
    log.debug('Load settings file')

load_dotenv('./.env')

if sys.version_info[:2] in [(3, 8), (3, 9)] and sys.platform.startswith('win'):
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    log.debug('Asyncio Event Loop Policy set to Windows Selector Event Loop Policy')


class Bot(commands.Bot):
    def __init__(self):
        super().__init__(
            case_insensitive=True,
            command_prefix=self.get_prefix,
            description='Aperture is a Multi-Purpose and super '\
                'Customisable Discord Bot with a lot of Features!',
            intents=Intents.all(),
            strip_after_prefix=True,
        )

        self.ready: bool = False
        self.aiohttp_session: Optional[aiohttp.ClientSession] = None
        self.pool: Optional[asyncpg.Pool] = None
        
        self.launch_time = datetime.utcnow()
        self._message_edit_timeout: int = 120
        self.old_responses: dict = {}
        self.prefixes: dict = {}


        self.loop.create_task(self.startup())
        self.loop.run_until_complete(self.create_pool(self.loop))

        try:
            if settings['bot']['owner-only'] is True:
                self.add_check(self.owner_only)
        except KeyError:
            log.critical('Settings file is not configured properly')
            raise SettingsError


    async def create_pool(self, loop) -> asyncpg.Connection:
        self.pool: asyncpg.Pool = await asyncpg.create_pool(
            host=os.getenv('DB_HOST'),
            port=int(os.getenv('DB_PORT')),
            user=os.getenv('DB_USER'),
            password=os.getenv('DB_PASSWORD'),
            database=os.getenv('DB_NAME'),
            loop=loop,
            min_size=1,
            max_size=100,
        )
        log.info('Created Database Pool')
        return self.pool

    def _get_case_insensitive_prefixes(self, prefix: str) -> List[str]:
        return list(
            map(
                ''.join, itertools.product(
                    *zip(
                        str(prefix).upper(),
                        str(prefix).lower()
                    )
                )
            )
        )
    
    async def get_prefix(self, message: Message) -> Union[list, str]:
        try:
            default_prefix = settings['bot']['default-prefix'] or 'ap!'
        except KeyError:
            log.critical('Settings file is not configured properly')
            raise SettingsError

        if isinstance(message.channel, DMChannel):
            return self._get_case_insensitive_prefixes(default_prefix)
        try:
            data = self.prefixes[message.guild.id]
            prefix = data[0]
            if data[1] is False:
                return prefix
            return self._get_case_insensitive_prefixes(prefix)
        except KeyError:
            async with self.pool.acquire() as conn:
                raw_data = await conn.fetch('SELECT * FROM guild_data;')
                for row in raw_data:
                    self.prefixes[row['guild_id']] = [row['prefix'], row['prefix_case_insensitive']]
            try:
                data = self.prefixes[message.guild.id]
                prefix = data[0]
                if data[1] is False:
                    return prefix
                return self._get_case_insensitive_prefixes(prefix)
            except KeyError:
                async with self.pool.acquire() as conn:
                    async with conn.transaction() as trans:
                        log.warn('get_prefix unable to get prefix from any existing data and function\n'\
                            f'Message ID: {message.id}, Author ID: {message.author.id}, Guild ID: {message.guild.id}')
                        await conn.execute('INSERT INTO guild_data (guild_id, prefix, prefix_case_insensitive) VALUES ($3, $1, $2) '\
                            'ON CONFLICT (guild_id) DO UPDATE SET prefix=EXCLUDED.prefix, prefix_case_insensitive=EXCLUDED.'\
                                'prefix_case_insensitive;')
                        return self._get_case_insensitive_prefixes(default_prefix)

    def setup(self):
        self.load_cogs()

    def load_cogs(self) -> None:
        try:
            if settings['startup']['load-cogs-on-startup'] is True:
                for cog in os.listdir('./aperture/cogs'):
                    self.load_extension(f'aperture.cogs.{cog}')
                    print(f'+[COG] -- {cog}')
                    log.debug(f'Add Cog `{cog}`')
            else:
                log.debug('Load cogs on startup is Disabled in Settings. Ignoring Cog Load Task')
                print('Load cogs on startup is Disabled in Settings. Ignoring Cog Load Task')
        except KeyError:
            log.critical('Settings file is not configured properly')
            raise SettingsError
            
        try:
            if settings['startup']['load-jishaku'] is True:
                self.load_extension('jishaku')
                log.debug('Add `Jishaku`')
            else:
                log.debug('Load Jishaku on startup is Disabled in Settings. Ignoring loading Jishaku')
                print('Load Jishaku on startup is Disabled in Settings. Ignoring loading Jishaku')
        except KeyError:
            log.critical('Settings file is not configured properly')
            raise SettingsError

    def run(self, version) -> None:
        self._version = version

        print('Setting Up...')
        self.setup()

        _token = os.getenv('TOKEN')
        print('Running the Bot...')
        log.info('Logging in using static Token...')
        super().run(_token, reconnect=True)

    async def close(self) -> None:
        print('Shutting Down...')
        log.info('Received signal to close the Bot. Shutting Down...')
        await super().close()
        log.debug('Closed the Bot connection successfully')

        try:
            await self.aiohttp_session.close()
            log.debug('Closed aiohttp session')

            await self.pool.close()
            log.debug('Closed Database connection')
        except AttributeError:
            pass

    async def on_connect(self) -> None:
        print(f'Connected to Bot. Latency: {self.latency*1000:,.0f} ms')
        log.debug(f'Connected to Bot. Latency: {self.latency*1000:,.0f} ms')

    async def on_disconnect(self) -> None:
        print('Bot Disconnnected')
        log.debug('Disconnected from Bot')

    async def on_ready(self) -> None:
        print('Bot is Ready')
        log.debug('Bot is Ready')

    async def get_owner_info(self):
        _app_info = await self.application_info()
        if _app_info.team:
            self.owner_ids = [member.id for member in _app_info.team.members]
        else:
            self.owner_id = _app_info.owner.id

    async def startup(self) -> None:
        await self.wait_until_ready()
        await self.get_owner_info()
        log.debug('Executing Startup function')
        log.debug('Creating aiohttp session')
        self.aiohttp_session = aiohttp.ClientSession()

    async def on_command_error(self, ctx, exc) -> None:
        if ctx.command.has_error_handler():
            return
        log.debug(f'Command {ctx.command.name} responded with error {exc}\nMessage ID: {ctx.message.id}, '\
            f'Author ID: {ctx.author.id}, Guild ID: {ctx.guild.id}')
        await error_handler(ctx, exc)

    async def process_commands(self, message: Message) -> None:
        ctx = await self.get_context(message, cls=CustomContext)
        if ctx.command is None:
            return
        await self.invoke(ctx)
        
    async def on_message(self, message: Message) -> None:
        if message.author.bot:
            return
        await self.process_commands(message)

    async def on_message_edit(self, before: Message, after: Message) -> None:
        if after.author.bot or before.content == after.content:
            return
        if (after.edited_at - before.created_at).seconds > self._message_edit_timeout:
            return
        await self.process_commands(after)

    async def on_message_delete(self, message: Message) -> None:
        if message.author.bot:
            return
        with suppress(Exception):
            bot_response: Message = self.old_responses[message.id]
            await bot_response.delete()

    async def on_command_completion(self, ctx):
        with suppress(KeyError):
            await asyncio.sleep(self._message_edit_timeout)
            self.old_responses.pop(ctx.message.id)

    async def owner_only(self, ctx):
        return ctx.author.id in [self.owner_id] + list(self.owner_ids)

# TODO: Use eval check from settings
# Improve error handler
# Implement debug mode