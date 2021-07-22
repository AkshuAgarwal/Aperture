from discord import Message
from discord.ext import commands

from aperture.core import CustomEmbed

class Fun(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.description = """Fun commands are some basic mini-games users can play."""


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
    @commands.bot_has_permissions(send_messages=True, read_message_history=True)
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