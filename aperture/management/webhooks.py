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

from __future__ import annotations
from typing import List

import os
import sys
import time
import aiohttp
import traceback

from discord import Embed, Webhook

from aperture.core import ApertureEmbed, ApertureContext


__all__ = ('ApertureManagementWebhookClient', )


class ApertureManagementWebhookClient:
    def __init__(self, session: aiohttp.ClientSession) -> None:
        self.error_report_webhook = Webhook.from_url(os.getenv('ERROR_REPORT_WEBHOOK'), session=session)
        self.critical_report_webhook = Webhook.from_url(os.getenv('CRITICAL_REPORT_WEBHOOK'), session=session)

        embed_description_max_limit: int = 4096
        self.prefix: str = '```'
        self.suffix: str = '```'
        self.max_error_length = embed_description_max_limit - (len(self.prefix) + len(self.suffix))

    @staticmethod
    def generate_uuid(user_id: int) -> str:
        return hex(int(str(time.time()).replace('.', '') + str(user_id)))[2:]

    async def send_error_report(self, ctx: ApertureContext, error: Exception) -> str:
        """Returns the UUID generated for the Case"""

        exc_id = self.generate_uuid(ctx.author.id)
        exc = f'Ignoring Exception in command {ctx.command}:\n' + ''.join(traceback.format_exception(type(error), error, error.__traceback__))
        chunks: List[str] = [self.prefix + exc[i:i+self.max_error_length] + self.suffix for i in range(0, len(exc), self.max_error_length)]
        embeds: List[Embed] = list()
        attachments_url: str = str('\n>' + ', '.join('`' + attc.url + '`' for attc in ctx.message.attachments)) if ctx.message.attachments else 'None'

        embeds.append(
            ApertureEmbed.default(
                ctx,
                title='Unexpected Exception',
                description=f"""
                    > **Exception ID:** `{exc_id}`

                    > **Author:** {ctx.author} (`{ctx.author.id}`) - {ctx.author.mention}

                    > **Channel:** {ctx.channel} (`{ctx.channel.id}`) - {ctx.channel.mention}

                    > **Guild:** {ctx.guild} (`{ctx.guild.id}`)

                    > **Command:** `{ctx.command.name}`

                    > **Message:** (`{ctx.message.id}`) - [Jump URL]({ctx.message.jump_url})
                    > ```{ctx.message.content}```

                    > **Attachments:** {attachments_url}
                """,
                color=0xFF7F7F
            )
        )
        for chunk in chunks:
            embeds.append(ApertureEmbed.default(ctx, description=chunk, color=0xFF7F7F))

        if len(embeds) > 10:
            for i in range(0, len(embeds), 10):
                await self.error_report_webhook.send(username='Aperture Error Reports', avatar_url=ctx.me.display_avatar.url, embeds=embeds[i:i+10])

        else:
            await self.error_report_webhook.send(username='Aperture Error Reports', avatar_url=ctx.me.display_avatar.url, embeds=embeds)

        traceback.print_exception(type(error), error, error.__traceback__, file=sys.stderr)
        return exc_id

    async def send_critical_report(self, ctx: ApertureContext, message: str):
        embeds: List[Embed] = list()
        chunks: List[str] = [message[i:i+4000] for i in range(0, len(message), 4000)] # A bit less than 4096

        for chunk in chunks:
            embeds.append(ApertureEmbed.default(ctx, title='Critical Report', description=chunk, color=0xFF0000))

        if len(embeds) > 10:
            for i in range(0, len(embeds), 10):
                await self.critical_report_webhook.send(username='Aperture Critical Reports', avatar_url=ctx.me.display_avatar.url, embeds=embeds[i:i+10])

        else:
            await self.critical_report_webhook.send(username='Aperture Critical Reports', avatar_url=ctx.me.display_avatar.url, embeds=embeds)
