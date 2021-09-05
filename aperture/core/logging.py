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

import logging
from logging.handlers import RotatingFileHandler


__all__ = ('ApertureLogger', )


class RemoveNoise(logging.Filter):
    def __init__(self) -> None:
        super().__init__(name='discord.state')

    def filter(self, record) -> bool:
        if record.levelname == 'WARNING' and 'referencing an unknown' in record.msg:
            return False
        return True

class ApertureLogger:
    def __init__(self, log_discord: bool = True, enable_bot_debug: bool = False) -> None:
        self.log_discord: bool = log_discord
        self.enable_bot_debug: bool = enable_bot_debug
        self.max_bytes: int = 64 * 1024 * 1024 # 64 MiB
        self.log: logging.Logger = logging.getLogger()

    def __enter__(self) -> None:
        if self.log_discord is True:
            logging.getLogger('discord').setLevel(logging.INFO)
            logging.getLogger('discord.http').setLevel(logging.WARNING)
            logging.getLogger('discord.state').addFilter(RemoveNoise())

        if self.enable_bot_debug is True:
            logging.getLogger('aperture').setLevel(logging.DEBUG)
            logging.getLogger('aperture.core.cache').setLevel(logging.DEBUG)
            logging.getLogger('aperture.core.database').setLevel(logging.DEBUG)
            logging.getLogger('aperture.core.listeners').setLevel(logging.DEBUG)

        self.log.setLevel(logging.INFO)
        handler = RotatingFileHandler(
            filename='./tmp/aperture.log',
            encoding='utf-8',
            mode='w',
            maxBytes=self.max_bytes,
            backupCount=5
        )
        dt_fmt: str = '%Y-%m-%d %H:%M:%S'
        fmt = logging.Formatter('[{asctime}] [{levelname:<7}] {name}: {message}', dt_fmt, style='{')
        handler.setFormatter(fmt)
        self.log.addHandler(handler)

    def __exit__(self, *_) -> None:
        handlers = self.log.handlers[:]
        for handler in handlers:
            handler.close()
            self.log.removeHandler(handler)
