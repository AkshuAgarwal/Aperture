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
from typing import Any, Callable, List, Optional, Union, TYPE_CHECKING

import os
import asyncio
import aiohttp
import itertools
import contextlib
import logging

import discord
from discord.ext import commands

from aperture.core import listeners, constants, ApertureContext
from aperture.management import ApertureManagementWebhookClient


log = logging.getLogger(__name__)


class ApertureBot(commands.Bot):
    if TYPE_CHECKING:
        import asyncpg
        from ..launcher import VersionInfo
        from .core import ApertureDatabase, ApertureCache

        version_info: VersionInfo
        database: ApertureDatabase
        pool: asyncpg.Pool
        cache: ApertureCache
        webhook_client: ApertureManagementWebhookClient

    def __init__(self) -> None:
        activity = discord.Activity(type = discord.ActivityType.listening, name='@Aperture help')
        allowed_mentions = discord.AllowedMentions(
            everyone = False,
            users = True,
            roles = False,
            replied_user = True,
        )
        description = 'Aperture is a Multipurpose, Customisable Discord Bot with tons of Features!'
        intents = discord.Intents(
            bans = False,
            emojis_and_stickers = False,
            guilds = True,
            integrations = False,
            invites = False,
            members = True,
            presences = False,
            messages = True,
            reactions = False,
            typing = False,
            voice_states = False,
            webhooks = False,
        )
        member_cache_flags = discord.MemberCacheFlags(joined=True, voice=False)

        super().__init__(
            activity = activity,
            allowed_mentions = allowed_mentions,
            case_insensitive = True,
            command_prefix = self.get_prefix,
            description = description,
            intents = intents,
            max_messages = None,
            member_cache_flags = member_cache_flags,
            owner_ids=constants.OWNER_IDS,
            strip_after_prefix = True,
        )
        log.debug('Initialised the Bot class')

        self._BotBase__cogs = commands.core._CaseInsensitiveDict()

        self.ready: bool = False
        self._default_prefix: str = constants.DEFAULT_PREFIX
        self.http_session: Optional[aiohttp.ClientSession] = None

        # Tasks to execute after bot gets ready
        self.loop.create_task(self.initialise_after_run())


    @staticmethod
    def _get_case_insensitive_prefixes(prefix: str) -> List[str]:
        return list(map(''.join, itertools.product(*zip(prefix.lower(), prefix.upper()))))

    async def get_prefix(self, message: discord.Message) -> Union[List[str], str]:
        if not message.guild:
            return commands.when_mentioned_or(
                *self._get_case_insensitive_prefixes(self._default_prefix)
            )(self, message)

        prefix = await self.cache.prefix.get_or_fetch(message.guild)

        if prefix: # Prefix is either found in cache or in database
            return commands.when_mentioned_or(*self._get_case_insensitive_prefixes(prefix))(self, message)

        # Prefix is not in cache or database. Possible reasons: 
            # Bot joined the guild when offline
            # Error in putting prefix in database when joined the guild
        # Put the default prefix in database, update prefix cache, and return default prefix
        await self.cache.prefix.insert(self._default_prefix, message.guild)
        log.debug('Prefix for Guild ID: %s not found in database', message.guild.id)
        return commands.when_mentioned_or(*self._get_case_insensitive_prefixes(self._default_prefix))(self, message)


    def initialise_before_run(self) -> None:
        log.debug('Initialising `before run` setup')
        self.load_extensions()

    def load_extensions(self):
        for ext in os.listdir('./aperture/extensions'):
            self.load_extension(f'aperture.extensions.{ext}')
            log.info('Load Extension: aperture.extensions.%s', ext)

        # Load jishaku
        self.load_extension('jishaku')
        log.info('Load Extension: jishaku')


    async def initialise_after_run(self) -> None:
        log.debug('Initialising `after run` setup')
        await self.wait_until_ready()

        self.http_session = aiohttp.ClientSession()
        log.debug('Created aiohttp session and attached to bot')

        self.webhook_client = ApertureManagementWebhookClient(self.http_session)
        log.debug('Initialized Management Webhook Client')

        # (Try to) Migrate the Database at startup
        with open('./aperture.sql', 'r', encoding='utf-8') as sql_file:
            data = sql_file.readlines()
            query = ''.join(line for line in data)
            await self.database.execute(query)
            log.debug('Database Migration completed')

        await self.cache.fill_cache()
        log.debug('Fetched and prepared bot\'s cache')

        await self.cache.start_cache_tasks()
        log.debug('Started cache tasks')

        # Set ready = True after last initialisation step (this method) of the bot.
        self.ready = True
        print('Setup completed! Bot is ready to be operated')
        log.info('Setup completed! Bot is ready to be operated')


    def run(self, token: str, *_: Any, **kwargs: Any) -> None:
        self.version = kwargs.pop('version', None)

        print('Starting Up...')
        log.debug('Executing `initialise_before_run` setup')
        self.initialise_before_run()

        print('Running the bot...')
        log.info('Logging in and running the bot...')
        super().run(token, reconnect=True)

    async def close(self) -> None:
        print('Shutting down...')

        log.info('Received signal to terminate the connection. Shutting Down...')
        await super().close()
        log.info('Closed the bot connection successfully')

        with contextlib.suppress(AttributeError):
            # This may take time since we allow tasks to complete their current running iteration.
            await self.cache.stop_cache_tasks()
            log.debug('Stopped cache tasks')

            await self.http_session.close()
            log.debug('Closed aiohttp session')

            await self.database.close_pool()
            log.debug('Closed database connection')


    # Listeners (Modified in aperture.core.listeners)
    async def on_message(self, message: discord.Message) -> None:
        await listeners.on_message(self, message)

    async def on_guild_join(self, guild: discord.Guild) -> None:
        await listeners.on_guild_join(self, guild)

    async def on_guild_remove(self, guild: discord.Guild) -> None:
        await listeners.on_guild_remove(self, guild)

    async def on_command(self, ctx: ApertureContext) -> None:
        await listeners.on_command(ctx)

    # Listeners (Unmodified)
    async def on_connect(self) -> None:
        print(f'Connected. Latency: {round(self.latency*1000)} ms')
        log.info('Connected. Latency: %s ms', round(self.latency*1000))

    async def on_resumed(self) -> None:
        print(f'Resumed the connection. Latency: {round(self.latency*1000)} ms')
        log.info('Resumed the connection. Latency: %s ms', round(self.latency*1000))

    async def on_disconnect(self) -> None:
        print('Disconnected. Trying to reconnect...')
        log.info('Disconnected. Trying to reconnect...')

    async def on_ready(self):
        print('Bot\'s internal cache is ready.')
        log.info('Bot\'s internal cache is ready.')

    # Modified methods
    async def wait_for(self, event: str, *, check: Optional[Callable[..., bool]], timeout: Optional[float]) -> Any:
        if event.lower() == 'reaction':
            done, pending = await asyncio.wait([
                self.wait_for('reaction_add', check=check, timeout=timeout),
                self.wait_for('reaction_remove', check=check, timeout=timeout)
            ], return_when=asyncio.FIRST_COMPLETED)

            for task in pending:
                task.cancel()
            return done.pop().result()

        return await super().wait_for(event, check=check, timeout=timeout)

    async def process_commands(self, message: discord.Message) -> None:
        ctx = await self.get_context(message, cls=ApertureContext)

        if ctx.command is None:
            return

        if not self.ready:
            await message.reply('Booting Up... Please wait for a few seconds', mention_author=False)
            return

        # Check for permissions of bot in the guild
        if isinstance(ctx.me, discord.Member):
            p: discord.Permissions = ctx.me.guild_permissions
            if not all([
                p.add_reactions,
                p.embed_links,
                p.read_message_history,
                p.send_messages,
                p.use_external_emojis,
                p.view_channel,
            ]):
                with contextlib.suppress(discord.Forbidden, discord.HTTPException):
                    await ctx.reply(
                        "I'm Missing minimum permissions I require to be operated in a Guild.\n"
                        "> Permissions I require: `Add reactions, Embed Links, Read message history, Send messages, "
                        "Use external emojis, View channel`. Please make sure I atleast have these permissions!"
                    )
                    log.debug('Missing minimum permissions for guild id: %s', ctx.guild.id)
                    return

        # Check if the guild or user is blacklisted
        if ctx.guild is not None and ctx.guild.id in self.cache.blacklist.guilds:
            return
        if ctx.author.id in self.cache.blacklist.users:
            return

        await self.invoke(ctx)
