from contextlib import suppress

from discord import Message
from discord.ext import commands

class CustomContext(commands.Context):
    async def send(self, content=None, *, tts=False, embed=None, file=None, files=None, delete_after=None, nonce=None, allowed_mentions=None, reference=None, mention_author=None):
        try:
            response: Message = self.bot.old_responses[self.message.id]
            with suppress(Exception):
                await response.clear_reactions()
            return await response.edit(content=content, tts=tts, embed=embed, file=file, files=files, delete_after=delete_after, nonce=nonce, allowed_mentions=allowed_mentions, reference=reference, mention_author=mention_author)
        except KeyError:
            response = await super().send(content=content, tts=tts, embed=embed, file=file, files=files, delete_after=delete_after, nonce=nonce, allowed_mentions=allowed_mentions, reference=reference, mention_author=mention_author)
            self.bot.old_responses[self.message.id] = response
            return response
            
    async def reply(self, content=None, *, tts=False, embed=None, file=None, files=None, delete_after=None, nonce=None, allowed_mentions=None, mention_author=None):
        try:
            response: Message = self.bot.old_responses[self.message.id]
            with suppress(Exception):
                await response.clear_reactions()
            return await response.edit(content=content, tts=tts, embed=embed, file=file, files=files, delete_after=delete_after, nonce=nonce, allowed_mentions=allowed_mentions, mention_author=mention_author)
        except KeyError:
            response = await super().reply(content=content, tts=tts, embed=embed, file=file, files=files, delete_after=delete_after, nonce=nonce, allowed_mentions=allowed_mentions, mention_author=mention_author)
            self.bot.old_responses[self.message.id] = response
            return response