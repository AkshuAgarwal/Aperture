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
import logging
from contextlib import suppress
from typing import List

from discord.ext import commands

from aperture.core import emoji

log = logging.getLogger(__name__)

class Developer(commands.Cog):
    _unload_restricted: List[str] = ['developer']
    
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        log.debug('Developer Cog ready')
        print('Developer Cog ready')


    @commands.command(
        name='load',
        brief='Loads an Extension',
        description='The command is used to load the Extensions into the Bot.',
        help="""The Extension should be a Python File Only with valid Extension syntax and should not already be loaded.
The Extension should be in the Proper directory in the bot's code as set by the Developer.

extension_name: Name of the extension to be loaded. Extension names are delimited by Spaces. Leave it blank or use `--all` to load all unloaded extensions.""",
        usage='[extension_name:str, default=all]'
    )
    @commands.is_owner()
    @commands.bot_has_permissions(
        send_messages=True,
        embed_links=True,
        add_reactions=True)
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def _load(self, ctx, *, extensions_name: str = None) -> None:
        _emojis = [emoji.greenTick, emoji.redCross]

        await ctx.message.add_reaction(_emojis[0])
        await ctx.message.add_reaction(_emojis[1])
        reaction, _ = await self.bot.wait_for('reaction_add', timeout=30,
                    check=lambda reaction, user: str(reaction.emoji) in _emojis and \
                        user == ctx.author and reaction.message == ctx.message)
        
        if str(reaction.emoji) == _emojis[1]:
            with suppress(Exception):
                await ctx.message.clear_reactions()
            await ctx.freply(f'{emoji.greenTick} Cancelled Task')
            return

        if not extensions_name or extensions_name=="--all":
            for ext in os.listdir('./aperture/cogs'):
                try:
                    self.bot.load_extension(f'aperture.cogs.{ext}')
                    log.debug(f'loaded {ext} on command.')
                except commands.ExtensionAlreadyLoaded:
                    pass
            await ctx.freply(f'{emoji.greenTick} Loaded all unloaded Extensions')
        else:
            _extensions = extensions_name.split()
            _loaded_extensions = []
            for ext in os.listdir('./aperture/cogs'):
                if ext in _extensions:
                    self.bot.load_extension(f'aperture.cogs.{ext}')
                    log.debug(f'loaded {ext} on command.')
                    _loaded_extensions.append(ext)
                
            return await ctx.freply(f'{emoji.greenTick} Loaded Cog(s) - `{"`, `".join(i for i in _loaded_extensions)}`')

    
    @commands.command(
        name='unload',
        brief='Unloads an Extension',
        description='The command is used to unload the Extensions from the Bot.',
        help=f"""The Extension should be a Python File Only with valid Extension syntax and should already be loaded.
The Extension should be in the Proper directory in the bot's code as set by the Developer.

extension_name: Name of the extension to be unloaded. Extension names are delimited by Spaces. Leave it blank or use `--all` to unload all loaded extensions (`{'`, `'.join(i for i in _unload_restricted)}` cog can only be unloaded by manually giving it as input).""",
        usage='[extension_name:str, default=all]'
    )
    @commands.is_owner()
    @commands.bot_has_permissions(
        send_messages=True,
        embed_links=True,
        add_reactions=True)
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def _unload(self, ctx, *, extensions_name: str = None) -> None:
        _emojis = [emoji.greenTick, emoji.redCross]

        await ctx.message.add_reaction(_emojis[0])
        await ctx.message.add_reaction(_emojis[1])
        reaction, _ = await self.bot.wait_for('reaction_add', timeout=30,
                    check=lambda reaction, user: str(reaction.emoji) in _emojis and \
                        user == ctx.author and reaction.message == ctx.message)
        
        if str(reaction.emoji) == _emojis[1]:
            with suppress(Exception):
                await ctx.message.clear_reactions()
            await ctx.freply(f'{emoji.greenTick} Cancelled Task')
            return

        if not extensions_name or extensions_name=="--all":
            for ext in os.listdir('./aperture/cogs'):
                if ext not in Developer._unload_restricted:
                    try:
                        self.bot.unload_extension(f'aperture.cogs.{ext}')
                        log.debug(f'unloaded {ext} on command.')
                    except commands.ExtensionNotLoaded:
                        pass
            await ctx.freply(f'{emoji.greenTick} Unloaded all loaded Extensions')
        else:
            _extensions = extensions_name.split()
            _unloaded_extensions = []
            for ext in os.listdir('./aperture/cogs'):
                if ext in _extensions:
                    self.bot.unload_extension(f'aperture.cogs.{ext}')
                    log.debug(f'unloaded {ext} on command.')
                    _unloaded_extensions.append(ext)
                
            return await ctx.freply(f'{emoji.greenTick} Unloaded Cog(s) - `{"`, `".join(i for i in _unloaded_extensions)}`')

    
    @commands.command(
        name='reload',
        brief='Reloads an Extension',
        description='The command is used to reload the Extensions from the Bot.',
        help=f"""The Extension should be a Python File Only with valid Extension syntax and should already be loaded.
The Extension should be in the Proper directory in the bot's code as set by the Developer.

extension_name: Name of the extension to be reloaded. Extension names are delimited by Spaces. Leave it blank or use `--all` to reload all loaded extensions.""",
        usage='[extension_name:str, default=all]'
    )
    @commands.is_owner()
    @commands.bot_has_permissions(
        send_messages=True,
        embed_links=True,
        add_reactions=True)
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def _reload(self, ctx, *, extensions_name: str = None) -> None:
        _emojis = [emoji.greenTick, emoji.redCross]

        await ctx.message.add_reaction(_emojis[0])
        await ctx.message.add_reaction(_emojis[1])
        reaction, _ = await self.bot.wait_for('reaction_add', timeout=30,
                    check=lambda reaction, user: str(reaction.emoji) in _emojis and \
                        user == ctx.author and reaction.message == ctx.message)
        
        if str(reaction.emoji) == _emojis[1]:
            with suppress(Exception):
                await ctx.message.clear_reactions()
            await ctx.freply(f'{emoji.greenTick} Cancelled Task')
            return

        if not extensions_name or extensions_name=="--all":
            for ext in os.listdir('./aperture/cogs'):
                try:
                    self.bot.reload_extension(f'aperture.cogs.{ext}')
                    log.debug(f'reloaded {ext} on command.')
                except commands.ExtensionNotLoaded:
                    pass
            await ctx.freply(f'{emoji.greenTick} Reloaded all loaded Extensions')
        else:
            _extensions = extensions_name.split()
            _reloaded_extensions = []
            for ext in os.listdir('./aperture/cogs'):
                if ext in _extensions:
                    self.bot.reload_extension(f'aperture.cogs.{ext}')
                    log.debug(f'reloaded {ext} on command.')
                    _reloaded_extensions.append(ext)
                
            return await ctx.freply(f'{emoji.greenTick} Reloaded Cog(s) - `{"`, `".join(i for i in _reloaded_extensions)}`')