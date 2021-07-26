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

import asyncio
import os
import logging
from typing import List

from discord import Message
from discord.ext import commands

from aperture.core import emoji
from ._views import ConfirmationView

log = logging.getLogger(__name__)


class Developer(commands.Cog):
    _unload_restricted: List[str] = ['developer']
    
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.description = 'Bot Owner (Developer) only Commands!'


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
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def _load(self, ctx, *, extensions_name: str = None) -> Message:
        view = ConfirmationView(ctx, timeout=30.0)
        _response = await ctx.freply('Are you sure to perform the task?', view=view)
        await view.wait()

        if view.value is None:
            raise asyncio.exceptions.TimeoutError
        elif view.value is False:
            return await _response.edit(content='Cancelled Task!', view=view)
        else:
            pass

        if not extensions_name or extensions_name=="--all":
            for ext in os.listdir('./aperture/cogs'):
                try:
                    self.bot.load_extension(f'aperture.cogs.{ext}')
                    log.debug(f'loaded {ext} on command.')
                except commands.ExtensionAlreadyLoaded:
                    pass
            return await _response.edit(content=f'{emoji.greenTick} Loaded all unloaded Extensions', view=view)
        else:
            _extensions = extensions_name.split()
            _loaded_extensions = []
            _failed_extensions = {}
            for ext in _extensions:
                try:
                    self.bot.load_extension(f'aperture.cogs.{ext}')
                    log.debug(f'loaded {ext} on command.')
                    _loaded_extensions.append(ext)
                except commands.ExtensionError as exc:
                    exc = getattr(exc, 'original', exc)
                    log.warn(f'extension {ext} failed to load:  {exc.__class__.__name__}: {exc}')
                    _failed_extensions[ext] = exc.__class__.__name__ + ': ' + str(exc)
            
            _success_fmt = str(
                f'{emoji.greenTick} Loaded Extensions: ' + ', '.join(f'`{i}`' for i in _loaded_extensions) + '\n'
            ) if _loaded_extensions else ''
            _failed_fmt = str(
                f'{emoji.redCross} Failed Extensions:\n> ' + '\n> '.join(
                    f'`{k}`: `{v}`' for k, v in _failed_extensions.items()
                )
            ) if _failed_extensions else ''
            return await _response.edit(content=_success_fmt + _failed_fmt, view=view)


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
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def _unload(self, ctx, *, extensions_name: str = None) -> Message:
        view = ConfirmationView(ctx, timeout=30.0)
        _response = await ctx.freply('Are you sure to perform the task?', view=view)
        await view.wait()

        if view.value is None:
            raise asyncio.exceptions.TimeoutError
        elif view.value is False:
            return await _response.edit(content='Cancelled Task!', view=view)
        else:
            pass

        if not extensions_name or extensions_name=="--all":
            for ext in os.listdir('./aperture/cogs'):
                if ext not in Developer._unload_restricted:
                    try:
                        self.bot.unload_extension(f'aperture.cogs.{ext}')
                        log.debug(f'unloaded {ext} on command.')
                    except commands.ExtensionNotLoaded:
                        pass
            return await _response.edit(content=f'{emoji.greenTick} Unloaded all loaded Extensions', view=view)
        else:
            _extensions = extensions_name.split()
            _unloaded_extensions = []
            _failed_extensions = {}
            for ext in _extensions:
                try:
                    self.bot.unload_extension(f'aperture.cogs.{ext}')
                    log.debug(f'unloaded {ext} on command.')
                    _unloaded_extensions.append(ext)
                except commands.ExtensionError as exc:
                    exc = getattr(exc, 'original', exc)
                    log.warn(f'extension {ext} failed to unload:  {exc.__class__.__name__}: {exc}')
                    _failed_extensions[ext] = exc.__class__.__name__ + ': ' + str(exc)
                
            _success_fmt = str(
                f'{emoji.greenTick} Unloaded Extensions: ' + ', '.join(f'`{i}`' for i in _unloaded_extensions) + '\n'
            ) if _unloaded_extensions else ''
            _failed_fmt = str(
                f'{emoji.redCross} Failed Extensions:\n> ' + '\n> '.join(
                    f'`{k}`: `{v}`' for k, v in _failed_extensions.items()
                )
            ) if _failed_extensions else ''
            return await _response.edit(content=_success_fmt + _failed_fmt, view=view)


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
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def _reload(self, ctx, *, extensions_name: str = None) -> Message:
        view = ConfirmationView(ctx, timeout=30.0)
        _response = await ctx.freply('Are you sure to perform the task?', view=view)
        await view.wait()

        if view.value is None:
            raise asyncio.exceptions.TimeoutError
        elif view.value is False:
            return await _response.edit(content='Cancelled Task!', view=view)
        else:
            pass

        if not extensions_name or extensions_name=="--all":
            for ext in os.listdir('./aperture/cogs'):
                try:
                    self.bot.reload_extension(f'aperture.cogs.{ext}')
                    log.debug(f'reloaded {ext} on command.')
                except commands.ExtensionNotLoaded:
                    pass
            return await _response.edit(content=f'{emoji.greenTick} Reloaded all loaded Extensions', view=view)
        else:
            _extensions = extensions_name.split()
            _reloaded_extensions = []
            _failed_extensions = {}
            for ext in _extensions:
                try:
                    self.bot.reload_extension(f'aperture.cogs.{ext}')
                    log.debug(f'reloaded {ext} on command.')
                    _reloaded_extensions.append(ext)
                except commands.ExtensionError as exc:
                    exc = getattr(exc, 'original', exc)
                    log.warn(f'extension {ext} failed to reload:  {exc.__class__.__name__}: {exc}')
                    _failed_extensions[ext] = exc.__class__.__name__ + ': ' + str(exc)
                
            _success_fmt = str(
                f'{emoji.greenTick} Reloaded Extensions: ' + ', '.join(f'`{i}`' for i in _reloaded_extensions) + '\n'
            ) if _reloaded_extensions else ''
            _failed_fmt = str(
                f'{emoji.redCross} Failed Extensions:\n> ' + '\n> '.join(
                    f'`{k}`: `{v}`' for k, v in _failed_extensions.items()
                )
            ) if _failed_extensions else ''
            return await _response.edit(content=_success_fmt + _failed_fmt, view=view)
