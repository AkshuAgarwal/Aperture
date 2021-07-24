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
