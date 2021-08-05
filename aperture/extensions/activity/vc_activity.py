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

from discord import Message, VoiceChannel
from discord.ext import commands

from ._views import VCActivity
from aperture import ApertureBot
from aperture.core import ApertureContext


class Activity(commands.Cog):
    def __init__(self, bot: ApertureBot):
        self.bot = bot
        self.description: str = "Commands to create and use Discord's Beta Party VC Games."


    @commands.command(
        name='activity',
        aliases=['vcactivity', 'vcgames'],
        brief='What about a match of Poker?',
        description="The command is used to create invite links to use Discord's Beta Party VC Games!",
        help="""The command returns an invite link to the selected channel which can be used to access the selected VC Game.
        
voice_channel: The Voice Channel for which the link is to be created. Defaults to the Member's already joined Voice Channel (if any).""",
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
