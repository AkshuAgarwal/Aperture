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

from typing import Any, Dict, List, Optional

from discord import Message
from discord.ext import commands

from aperture import ApertureBot
from aperture.core import ApertureEmbed, ApertureContext


class Fun(commands.Cog):
    def __init__(self, bot: ApertureBot):
        self.bot = bot
        self.description = """Some basic mini-games/fun commands to play with"""

        self.snipes: Dict[int, List[Message]] = {}


    @commands.Cog.listener()
    async def on_message_delete(self, message: Message) -> None:
        if message.content:
            if not self.snipes.get(message.channel.id, None):
                self.snipes[message.channel.id] = []
            else:
                if len(self.snipes[message.channel.id]) > 100:
                    self.snipes[message.channel.id].pop(0)
            self.snipes[message.channel.id].append(message)


    @commands.command(
        name='snipe',
        brief='I saw something got deleted from here!',
        description='The command is used to snipe a deleted message from a channel',
        help="""The command returns the content of the deleted messages in a particular channel.
The command only returns messages with some content and will not return anything if the content is None (i.e., message have a attachment and/or embeds

`index`: The index of the message to get. Min-max: 1 (Latest) - 100 (Last 100th message)""",
        usage='[index: int, default=1]'
    )
    @commands.guild_only()
    @commands.cooldown(1, 10, commands.BucketType.channel)
    async def snipe(self, ctx: ApertureContext, index: Optional[int] = 1) -> Optional[Any]:
        additional_message = ''
        whitespace = '\u2002'

        if not index in range(1, 101):
            await ctx.freply('You can only choose an Index between 1 and 100')
            return

        channel_snipes = self.snipes.get(ctx.channel.id, None)
        if not channel_snipes:
            await ctx.freply('No Sniped messages found in this channel.')
            return
        
        try:
            _message = channel_snipes[index-1]
        except IndexError:
            try:
                _message = channel_snipes[0]
                additional_message = f'No sniped message found with index `{index}`.\nShowing the latest sniped message'
            except IndexError:
                await ctx.freply('No Sniped messages found in this channel.')
                return

        embed = ApertureEmbed.default(
            ctx, title='Sniped Message', description=additional_message + '\n\n' + _message.content + f'\n{whitespace*10}- ' + _message.author.mention
        )
        return await ctx.freply(embed=embed)
