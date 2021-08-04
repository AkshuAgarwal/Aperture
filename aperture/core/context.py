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

from contextlib import suppress as _suppress

from discord import Message
from discord.ext import commands

class CustomContext(commands.Context):
    async def fsend(
        self,
        content=None,
        *,
        tts=None,
        embed=None,
        file=None,
        files=None,
        delete_after=None,
        nonce=None,
        allowed_mentions=None,
        reference=None,
        mention_author=None,
        view=None,
        embeds=None,
        attachments=None,
        suppress=False
        ):
        try:
            response: Message = self.bot.old_responses[self.message.id]
            with _suppress(Exception):
                await response.clear_reactions()
            return await response.edit(
                content=content,
                embed=embed,
                attachments=attachments,
                suppress=suppress,
                delete_after=delete_after,
                allowed_mentions=allowed_mentions,
                view=view
            )
        except KeyError:
            response = await super().send(
                content=content,
                tts=tts,
                embed=embed,
                embeds=embeds,
                file=file,
                files=files,
                delete_after=delete_after,
                nonce=nonce,
                allowed_mentions=allowed_mentions,
                reference=reference,
                mention_author=mention_author,
                view=view
            )
            self.bot.old_responses[self.message.id] = response
            return response

    async def freply(
        self,
        content=None,
        *,
        tts=None,
        embed=None,
        file=None,
        files=None,
        delete_after=None,
        nonce=None,
        allowed_mentions=None,
        mention_author=None,
        view=None,
        embeds=None,
        attachments=None,
        suppress=False
        ):
        try:
            response: Message = self.bot.old_responses[self.message.id]
            with _suppress(Exception):
                await response.clear_reactions()
            return await response.edit(
                content=content,
                embed=embed,
                attachments=attachments,
                suppress=suppress,
                delete_after=delete_after,
                allowed_mentions=allowed_mentions,
                view=view
            )
        except KeyError:
            response = await super().reply(
                content=content,
                tts=tts,
                embed=embed,
                embeds=embeds,
                file=file,
                files=files,
                delete_after=delete_after,
                nonce=nonce,
                allowed_mentions=allowed_mentions,
                mention_author=mention_author,
                view=view
            )
            self.bot.old_responses[self.message.id] = response
            return response
