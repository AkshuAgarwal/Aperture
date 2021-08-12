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

import os
import sys
import asyncio
import itertools
import logging
import logging.config
from datetime import datetime
from contextlib import suppress
from typing import Any, Callable, Dict, List, Optional, Union

import aiohttp
import asyncpg
import yaml
from dotenv import load_dotenv

from discord import (
    AllowedMentions,
    DMChannel,
    Guild,
    Intents,
    Member,
    Message,
    Permissions,
)
from discord.ext import commands

from aperture.core import ApertureContext, error_handler
from aperture.core.error import SettingsError
from aperture.management import ErrorLogger


log = logging.getLogger(__name__)
load_dotenv('./.env')

if not os.path.exists('./tmp'):
    os.makedirs('./tmp')
    print('Created directory "tmp" in the project root directory')

with open('./logging.yaml', 'r', encoding='UTF-8') as stream:
    log_config: Union[Dict[str, Any], Any] = yaml.load(stream, Loader=yaml.FullLoader)
    logging.config.dictConfig(log_config)

with open('./settings.yaml', 'r', encoding='utf-8') as file:
    settings: Union[Dict[str, Any], Any] = yaml.load(file, Loader=yaml.FullLoader)
    log.info('Loaded settings file')

if sys.version_info[:2] in [(3, 8), (3, 9)] and sys.platform.startswith('win'):
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    log.debug('Asyncio Event Loop Policy set to Windows Selector Event Loop Policy')


class ApertureBot(commands.Bot):
    def __init__(self) -> None:
        allowed_mentions = AllowedMentions(everyone=False, users=True, roles=False, replied_user=True)
        super().__init__(
            allowed_mentions=allowed_mentions,
            case_insensitive=True,
            command_prefix=self.get_prefix,
            description='Aperture is a Multi-Purpose and super '\
                'Customisable Discord Bot with a lot of Features!',
            intents=Intents.all(),
            strip_after_prefix=True,
        )

        self.ready: bool = False
        self.version: Optional[str] = None
        self.aiohttp_session: Optional[aiohttp.ClientSession] = None
        self.pool: Optional[asyncpg.Pool] = None
        self.error_log_webhook: Optional[ErrorLogger] = None

        self.launch_time: datetime = datetime.utcnow()
        self.message_edit_timeout: int = 120
        self.old_responses: dict = {}
        self.prefixes: dict = {}
        self.snipes: dict = {}

        self.loop.create_task(self.startup())
        self.loop.run_until_complete(self.create_pool(self.loop))

        try:
            if settings['bot']['owner-only'] is True:
                self.add_check(self.owner_only)
        except KeyError:
            log.critical('Settings file is not configured properly')
            raise SettingsError

    async def create_pool(self, loop: asyncio.AbstractEventLoop) -> asyncpg.Pool:
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

    @staticmethod
    def _get_case_insensitive_prefixes(prefix: str) -> List[str]:
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

    async def get_prefix(self, message: Message) -> Union[List[str], str]:
        try:
            default_prefix: str = settings['bot']['default-prefix']
        except KeyError:
            log.critical('Settings file is not configured properly')
            raise SettingsError

        if isinstance(message.channel, DMChannel):
            return commands.when_mentioned_or(
                self._get_case_insensitive_prefixes(default_prefix)
            )(self, message)
        try:
            data: List[str, bool] = self.prefixes[message.guild.id]
            prefix: str = data[0]
            if data[1] is False:
                return commands.when_mentioned_or(prefix)(self, message)
            return commands.when_mentioned_or(
                self._get_case_insensitive_prefixes(prefix)
            )(self, message)
        except KeyError:
            async with self.pool.acquire() as conn:
                raw_data: List[asyncpg.Record] = await conn.fetch(
                    'SELECT guild_id, prefix, prefix_case_insensitive FROM guild_prefixes;'
                )
                for row in raw_data:
                    self.prefixes[row['guild_id']] = [row['prefix'], row['prefix_case_insensitive']]
            try:
                data: List[str, bool] = self.prefixes[message.guild.id]
                prefix: str = data[0]
                if data[1] is False:
                    return commands.when_mentioned_or(prefix)(self, message)
                return commands.when_mentioned_or(
                    self._get_case_insensitive_prefixes(prefix)
                )(self, message)
            except KeyError:
                async with self.pool.acquire() as conn:
                    async with conn.transaction():
                        await conn.execute(
                            'INSERT INTO guild_prefixes (guild_id, prefix, prefix_case_insensitive) VALUES '
                            '($3, $1, $2) ON CONFLICT (guild_id) DO UPDATE SET prefix=EXCLUDED.prefix, '
                            'prefix_case_insensitive=EXCLUDED.prefix_case_insensitive;',
                            default_prefix, True, message.guild.id
                        )
                        log.warn(
                            'get_prefix unable to get prefix from any existing data and function\n'
                            'Message ID: %s, Author ID: %s, Channel ID: %s, Guild ID: %s',
                            message.id, message.author.id, message.channel.id, message.guild.id)
                        return commands.when_mentioned_or(
                            self._get_case_insensitive_prefixes(default_prefix)
                        )(self, message)

    def load_extensions(self) -> None:
        try:
            if settings['startup']['load-extensions'] is True:
                for ext in os.listdir('./aperture/extensions'):
                    self.load_extension(f'aperture.extensions.{ext}')
                    print(f'+[EXTENSION] -- {ext}')
                    log.debug('Add Extension - %s', ext)
            else:
                log.debug('Load extensions on startup is Disabled in Settings. Ignoring Extension load Task')
                print('Load extensions on startup is Disabled in Settings. Ignoring Extension load Task')
        except KeyError:
            log.critical('Settings file is not configured properly')
            raise SettingsError

        try:
            if settings['startup']['load-jishaku'] is True:
                self.load_extension('jishaku')
                log.debug('Add Jishaku')
            else:
                log.debug('Load Jishaku on startup is Disabled in Settings. Ignoring loading Jishaku')
                print('Load Jishaku on startup is Disabled in Settings. Ignoring loading Jishaku')
        except KeyError:
            log.critical('Settings file is not configured properly')
            raise SettingsError

    def initialise_before_run(self) -> None:
        self.load_extensions()

    def run(self, *_, **kwargs) -> None:
        self.version = kwargs.get('version', None)

        print('Setting Up...')
        self.initialise_before_run()

        _token: str = os.getenv('TOKEN')
        print('Running the Bot...')
        log.info('Logging in using static Token...')
        super().run(_token, reconnect=True)

    async def close(self) -> None:
        print('Shutting Down...')
        log.info('Received signal to close the Bot. Shutting Down...')
        await super().close()
        log.info('Closed the Bot connection successfully')

        with suppress(AttributeError):
            await self.aiohttp_session.close()
            log.debug('Closed aiohttp session')

            await self.pool.close()
            log.debug('Closed Database connection')

    async def on_ready(self) -> None:
        print('Bot is Ready')
        log.debug('Bot is Ready')

    async def setup_backend(self) -> None:
        self.error_log_webhook = ErrorLogger(webhook_url=os.getenv('ERROR_LOG_WEBHOOK'), session=self.aiohttp_session)

    async def startup(self) -> None:
        await self.wait_until_ready()
        log.debug('Executing Startup function')
        
        await self.get_owner_info()
        
        self.aiohttp_session = aiohttp.ClientSession()
        log.debug('Created aiohttp session')

        await self.setup_backend()
        log.debug('Backend setup completed')

        self.ready = True

    async def on_connect(self) -> None:
        print(f'Connected to Bot. Latency: {round(self.latency*1000)} ms')
        log.debug('Connected to Bot. Latency: %s ms', round(self.latency*1000))

    async def on_disconnect(self) -> None:
        print('Bot Disconnnected')
        log.debug('Disconnected from Bot')

    async def on_command_error(self, ctx: ApertureContext, exc: Exception) -> None:
        if ctx.command.has_error_handler():
            return
        log.debug('Command %s responded with error %s\nMessage ID: %s, Author ID: %s, Guild ID: %s',
            ctx.command.name, exc, ctx.message.id, ctx.author.id, ctx.guild.id)
        await error_handler(ctx, exc)

    async def wait_for(
        self, event: str, *, check: Optional[Callable[..., bool]]=None, timeout: Optional[float]=None
    ) -> Any:
        if event == 'reaction':
            done, pending = await asyncio.wait([
                self.wait_for('reaction_add', check=check, timeout=timeout),
                self.wait_for('reaction_remove', check=check, timeout=timeout)
            ], return_when=asyncio.FIRST_COMPLETED)

            for task in pending:
                task.cancel()
            return done.pop().result()

        return await super().wait_for(event, check=check, timeout=timeout)

    async def process_commands(self, message: Message) -> None:
        ctx = await self.get_context(message, cls=ApertureContext)
        if ctx.command is None:
            return
        if not self.ready and ctx.command is not None:
            await message.reply("I'm currently setting up. Please wait for a few seconds...")
            return
        if isinstance(ctx.me, Member):
            p: Permissions = ctx.me.guild_permissions
            if not all([
                p.add_reactions,
                p.embed_links,
                p.read_message_history,
                p.send_messages,
                p.use_external_emojis,
                p.view_channel,
            ]):
                with suppress(Exception):
                    await ctx.reply(
                        "I'm Missing minimum permissions I require to be operated in a Guild.\n"
                        "> Permissions I require: `Add reactions, Embed Links, Read message history, Send messages, "
                        "Use external emojis, View channel`\nMake sure I atleast have these permissions!"
                    )
                    return
        await self.invoke(ctx)

    async def on_message(self, message: Message) -> None:
        if not message.author.bot:
            await self.process_commands(message)

    async def on_message_edit(self, before: Message, after: Message) -> None:
        if not after.author.bot and (after.created_at - before.created_at).seconds <= self.message_edit_timeout:
            await self.process_commands(after)

    async def on_message_delete(self, message: Message) -> None:
        if not message.author.bot:
            with suppress(Exception):
                bot_response: Message = self.old_responses[message.id]
                await bot_response.delete()
                self.old_responses.pop(message.id, None)

    async def on_command_completion(self, ctx) -> None:
        await asyncio.sleep(self.message_edit_timeout)
        self.old_responses.pop(ctx.message.id, None)

    async def on_guild_join(self, guild: Guild) -> None:
        try:
            default_prefix = settings['bot']['default-prefix']
        except KeyError:
            log.critical('Settings file is not configured properly')
            raise SettingsError

        async with self.pool.acquire() as conn:
            async with conn.transaction():
                await conn.execute('INSERT INTO guild_data (guild_id, prefix, prefix_case_insensitive)'
                                    ' VALUES ($3, $1, $2) ON CONFLICT (guild_id) DO NOTHING;',
                                    default_prefix, True, guild.id)

    async def on_guild_remove(self, guild: Guild) -> None:
        async with self.pool.acquire() as conn:
            async with conn.transaction():
                await conn.execute('DELETE FROM guild_data WHERE guild_id = $1;', guild.id)

    async def get_owner_info(self) -> None:
        _app_info = await self.application_info()
        if _app_info.team:
            self.owner_ids: List[int] = [member.id for member in _app_info.team.members]
        else:
            self.owner_id: int = _app_info.owner.id

    async def owner_only(self, ctx: ApertureContext) -> bool:
        return ctx.author.id in [self.owner_id] + list(self.owner_ids)
