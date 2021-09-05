from __future__ import annotations

import os
import sys
import logging
import asyncio
from dotenv import load_dotenv
from typing import Literal, NamedTuple

from aperture import ApertureBot
from aperture.core import ApertureLogger, ApertureDatabase, ApertureCache

load_dotenv('./.env')
log = logging.getLogger(__name__)


if sys.version_info[:2] >= (3, 8) and sys.platform.startswith('win'):
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    log.debug('Asyncio Event Loop Policy set to Windows Selector Event Loop Policy')


class VersionInfo(NamedTuple):
    major: int
    minor: int
    micro: int
    releaselevel: Literal['alpha', 'beta', 'candidate', 'final']
    serial: int

__version__: str = '1.0.1a'


def run_bot() -> None:
    with ApertureLogger(log_discord=True, enable_bot_debug=True):
        bot = ApertureBot()
        bot.version_info = VersionInfo(major=1, minor=0, micro=1, releaselevel='alpha', serial=0)

        bot.database = ApertureDatabase()
        bot.pool = bot.database.create_pool()
        bot.cache = ApertureCache(bot)

        bot.run(os.getenv('BOT_TOKEN'), version=__version__)


if __name__ == '__main__':
    run_bot()
