from typing import Optional

from discord import VoiceChannel
from discord.ext import commands

from ._views import VCActivity


class Activity(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.description = "Commands to create and use Discord's Beta Party VC Games."


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
    async def vc_activity(self, ctx, voice_channel: Optional[VoiceChannel] = None):
        if not voice_channel and not ctx.author.voice:
            return await ctx.freply('You either need to join or input a Voice Channel manually to create an invite.')
        if not voice_channel:
            _channel = ctx.author.voice.channel
        else:
            _channel = voice_channel
        _view = VCActivity(ctx, channel=_channel)
        _resp = await ctx.freply(content='Select an option from the Dropdown to create the activity', view=_view)
        _view.message = _resp
