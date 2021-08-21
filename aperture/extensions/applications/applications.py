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

from typing import Any, Optional

from discord import Embed, Message, VoiceChannel
from discord.ext import commands

from aperture import ApertureBot
from aperture.core import ApertureContext
from ._vcactivity import VCActivity
from ._calculator import CalculatorView


class Applications(commands.Cog):
    def __init__(self, bot: ApertureBot) -> None:
        self.bot = bot
        self.description: str = 'Interactive Applications of the Bot'
    
    @commands.command(
        name='activity',
        aliases=['vcactivity', 'vcgames'],
        brief='What about a match of Poker?',
        description="The command is used to create invite links to use Discord's Beta Party VC Games!",
        help="""The command returns an invite link to the selected channel which can be used to access the selected VC Game.
        
`voice_channel`: The Voice Channel for which the link is to be created. Defaults to the Member's already joined Voice Channel (if any).""",
        usage="[voice_channel: VoiceChannel, default=Member's currently joined VC.]"
    )
    @commands.bot_has_guild_permissions(create_instant_invite=True)
    @commands.guild_only()
    @commands.cooldown(1, 15, commands.BucketType.user)
    async def vc_activity(self, ctx: ApertureContext, voice_channel: Optional[VoiceChannel] = None) -> Optional[Any]:
        if not voice_channel and not ctx.author.voice:
            return await ctx.freply('You either need to join or input a Voice Channel manually to create an invite.')
        if not voice_channel:
            _channel: VoiceChannel = ctx.author.voice.channel
        else:
            _channel: VoiceChannel = voice_channel
        _view = VCActivity(ctx, channel=_channel)
        _resp: Message = await ctx.freply(content='Select an option from the Dropdown to create the activity', view=_view)
        _view.message = _resp

    @commands.command(
        name='calculator',
        aliases=['calc'],
        brief='➕➖✖️➗',
        description='The command starts an Interactive Buttons based Calculator',
        help="""The command starts a Buttons based Interactive Simple Calculator you can use to calculate basic Mathematical Operations."""
    )
    @commands.guild_only()
    @commands.max_concurrency(5, commands.BucketType.guild)
    @commands.cooldown(1, 20, commands.BucketType.user)
    async def _calculator(self, ctx: ApertureContext):
        space = '\u2002'
        total_len = 40
        _no = 0
        embed = Embed(description=f'```{space*(total_len-len(str(_no)))}{_no}```', color=0x2F3136)
        view=CalculatorView(ctx)
        view.response = await ctx.freply(embed=embed, view=view)
