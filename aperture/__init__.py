import aiohttp
import asyncio
import asyncpg
import itertools
import logging
import logging.config
import os
import sys
import yaml
from contextlib import suppress
from datetime import datetime
from dotenv import load_dotenv
from typing import Union, Optional

from discord import (
    Message,
    Intents,
    DMChannel,
)
from discord.ext import commands
from discord.ext.commands import Bot as BotBase

from .core import CustomContext, error_handler


log = logging.getLogger(__name__)

if not os.path.exists('./tmp'):
    os.makedirs('./tmp')
    log.debug('Created directory "tmp" in the project root directory')

with open('./logging.yaml', 'r', encoding='UTF-8') as stream:
    config = yaml.load(stream, Loader=yaml.FullLoader)
logging.config.dictConfig(config)

load_dotenv('./.env')

if sys.version_info[:2] in [(3, 8), (3, 9)] and sys.platform.startswith('win'):
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    log.debug('Asyncio Event Loop Policy set to Windows Selector Event Loop Policy')


class Bot(BotBase):
    def __init__(self):
        super().__init__(
            case_insensitive=True,
            command_prefix=self.get_prefix,
            description='Aperture is a Multi-Purpose and super Customisable Discord Bot with a lot of Features!',
            intents=Intents.all(),
            strip_after_prefix=True,
        )

        self.ready: bool = False
        self.aiohttp_session: Optional[aiohttp.ClientSession] = None
        self.db_conn: Optional[asyncpg.Connection] = None
        
        self.launch_time = datetime.utcnow()
        self._message_edit_timeout: int = 120
        self.old_responses: dict = {}
        self.prefixes: dict = {}

        self.loop.create_task(self.startup())
        self.loop.run_until_complete(self.create_pool(self.loop))

    async def create_pool(self, loop) -> asyncpg.Connection:
        pool: asyncpg.Pool = await asyncpg.create_pool(
            host=os.getenv('DB_HOST'),
            port=int(os.getenv('DB_PORT')),
            user=os.getenv('DB_USER'),
            password=os.getenv('DB_PASSWORD'),
            database=os.getenv('DB_NAME'),
            loop=loop,
            min_size=1,
            max_size=100,
        )
        self.db_conn = await pool.acquire()
        log.info('Created Successful Connection with Database')
        return self.db_conn

    async def get_prefix(self, message: Message) -> Union[list, str]:
        default_prefix = 'ap!'
        if isinstance(message.channel, DMChannel):
            return list(map(''.join, itertools.product(*zip(str(default_prefix).upper(), str(default_prefix).lower()))))
        try:
            data = self.prefixes[message.guild.id]
            prefix = data[0]
            if data[1] is False:
                return prefix
            return list(map(''.join, itertools.product(*zip(str(prefix).upper(), str(prefix).lower()))))
        except KeyError:
            raw_data = await self.db_conn.fetch('SELECT * FROM guild_data;')
            for row in raw_data:
                self.prefixes[row['guild_id']] = [row['prefix'], row['prefix_case_insensitive']]
            try:
                data = self.prefixes[message.guild.id]
                prefix = data[0]
                if data[1] is False:
                    return prefix
                return list(map(''.join, itertools.product(*zip(str(prefix).upper(), str(prefix).lower()))))
            except KeyError:
                async with self.db_conn.transaction() as trans:
                    await self.db_conn.execute('INSERT INTO guild_data (guild_id, prefix, prefix_case_insensitive) VALUES ($3, $1, $2) ON CONFLICT (guild_id) DO UPDATE guild_data SET prefix=$1, prefix_case_insensitive=$2 WHERE guild_id=$3;')
                    return list(map(''.join, itertools.product(*zip(str(default_prefix).upper(), str(default_prefix).lower()))))
        log.debug(f'get_prefix unable to get prefix from any existing data and function\nMessage ID: {message.id}, Invoker ID: {message.author.id}, Guild ID: {message.guild.id}')

    def setup(self):
        self.load_cogs()

    def load_cogs(self) -> None:
        for cog in os.listdir('./aperture/cogs'):
            self.load_extension(f'aperture.cogs.{cog}')
            print(f'+[COG] -- {cog}')
            log.debug(f'Added Cog - {cog}')

        self.load_extension('jishaku')
        log.debug('Added External Cog - Jishaku')

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
        await self.aiohttp_session.close()
        await super().close()

    async def on_connect(self) -> None:
        print(f'Connected to Bot. Latency: {self.latency*1000:,.0f} ms')
        log.debug(f'Connected to Bot. Latency: {self.latency*1000:,.0f} ms')

    async def on_disconnect(self) -> None:
        print('Bot Disconnnected')
        log.debug('Disconnected from Bot')

    async def on_ready(self) -> None:
        print('Bot is Ready')
        log.debug('Bot is Ready')

    async def startup(self) -> None:
        await self.wait_until_ready()
        log.debug('Executing Startup function')
        self.aiohttp_session = aiohttp.ClientSession()

    async def on_command_error(self, ctx, exc) -> None:
        if ctx.command.has_error_handler():
            return
        log.debug(f'Command {ctx.command.name} responded with error {exc}\nMessage ID: {ctx.message.id}, Invoker ID: {ctx.author.id}, Guild ID: {ctx.guild.id}')
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