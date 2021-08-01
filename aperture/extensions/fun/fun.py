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

from discord import Message
from discord.ext import commands

from aperture.core import CustomEmbed


class Fun(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.description = """Some basic mini-games/fun commands to play with"""


    @commands.Cog.listener()
    async def on_message_delete(self, message: Message):
        if message.content is None:
            return
        self.bot.snipes[message.channel.id] = message

    
    @commands.command(
        name='snipe',
        brief='I saw something got deleted from here!',
        description='The command is used to snipe a deleted message from a channel',
        help="""The command returns the content of the latest deleted message.
It is possible that it can return None in case the message is not found in the bot's cache.
The command only returns messages with some content and will not save if the content is None (i.e., the message has no content and instead have a attachment and/or embeds""",
    )
    @commands.guild_only()
    @commands.cooldown(1, 10, commands.BucketType.channel)
    async def snipe(self, ctx) -> Message:
        try:
            _message: Message = self.bot.snipes[ctx.channel.id]
            if not _message.content:
                return await ctx.freply('No Sniped Messages found in this channel')
        except KeyError:
            return await ctx.freply('No Sniped Messages found in this channel')

        embed = CustomEmbed.default(
            ctx, title='Sniped Message', description=_message.content + '\n- ' + _message.author.mention
        )
        return await ctx.freply(embed=embed)
