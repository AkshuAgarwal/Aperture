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

from typing import Optional

from discord import User
from discord.ext import commands

from aperture.core import CustomEmbed


class Utilities(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.description = """Utilities commands are some basic/general usage commands."""

    @commands.command(
        name='avatar',
        aliases=['av'],
        brief='Wow, your Avatar looks awesome!',
        description='The command is used to get the Avatar of a user.',
        help="""The command returns the Avatar of the user with it's Download Links!

user: The User whose Avatar is to be found. Defaults to command invoker.""",
        usage='[user: User/Member, default=Command Invoker]'
    )
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def _avatar(self, ctx, user: Optional[User]=None):
        _member = user or ctx.author
        _asset = _member.avatar
        _desc = f"> **Download Avatar:**\n> [png]({_asset.with_format('png').url}) | "\
                f"[webp]({_asset.with_format('webp').url}) | [jpg]({_asset.with_format('jpg').url}) | "\
                    f"[jpeg]({_asset.with_format('jpeg').url})"

        if _asset.key.isdigit():
            _desc = f"> **Download Avatar:**\n> [png]({_asset.with_format('png').url})"
        elif _asset.is_animated():
            _desc += f" | [gif]({_asset.with_format('gif').url})"

        embed = CustomEmbed.default(ctx, title=f"{_member}'s Avatar", description=_desc)
        embed.set_image(url=_asset.url)

        await ctx.freply(embed=embed)
