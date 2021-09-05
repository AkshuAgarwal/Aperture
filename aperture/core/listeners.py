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

from .enums import CommandType

if TYPE_CHECKING:
    import discord
    from aperture import ApertureBot
    from aperture.core import ApertureContext


log = logging.getLogger('aperture.core.listeners')


async def on_message(bot: ApertureBot, message: discord.Message) -> None:
    if not message.author.bot:
        await bot.process_commands(message)

async def on_guild_join(bot: ApertureBot, guild: discord.Guild) -> None:
    log.debug('Joined a guild. ID: %s', guild.id)
    await bot.cache.insert_prefix(bot._default_prefix, guild)

async def on_guild_remove(bot: ApertureBot, guild: discord.Guild) -> None:
    log.debug('Left a guild. ID: %s', guild.id)
    await bot.cache.remove_prefix(guild)

async def on_command(ctx: ApertureContext):
    bot: ApertureBot = ctx.bot
    await bot.cache.command_usage.add(
        ctx.command, # type: ignore
        CommandType.MESSAGE_CONTENT, # For now, since bot only have message commands, this is the only type
        ctx.author,
        ctx.guild if ctx.guild is not None else None
    )
    log.debug(
        'A command has been invoked. Name: %s, type: %s, user_id: %s, guild_id: %s',
        ctx.command.name, # type: ignore
        CommandType.MESSAGE_CONTENT, # Same reason (message type only for now)
        ctx.author.id,
        ctx.guild.id if ctx.guild is not None else None
    )
