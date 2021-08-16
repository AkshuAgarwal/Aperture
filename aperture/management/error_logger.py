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

import sys
import time
import traceback
import aiohttp

from discord.webhook import Webhook

from aperture.core import ApertureContext, ApertureEmbed

__all__ = ('ErrorLogger', )


class ErrorLogger:
    def __init__(self, *, webhook_url: str, session: aiohttp.ClientSession) -> None:
        self._webhook_url = webhook_url
        self._session = session
        self.webhook: Webhook = Webhook.from_url(self._webhook_url, session=self._session)

        self.prefix: str = '```'
        self.suffix: str = '```'
        self.embed_desc_limit = 4096
        self.max_len = self.embed_desc_limit - (len(self.prefix) + len(self.suffix))

    def generate_exc_id(self, user_id: int) -> str:
        return hex(int(str(time.time()).replace('.', '') + str(user_id)))[2:]

    async def send(self, ctx: ApertureContext, error: Exception) -> str:
        exc_id = self.generate_exc_id(ctx.author.id)
        exc: str = f'Ignoring exception in command {ctx.command}:\n' + ''.join(traceback.format_exception(type(error), error, error.__traceback__))
        chunked: list = [self.prefix + exc[i:i+self.max_len] + self.suffix for i in range(0, len(exc), self.max_len)]
        _embeds: list = []

        _embeds.append(
            ApertureEmbed.default(
                ctx,
                title='Unexpected Exception',
                description=f"""
                    > **Unique Exception ID:** `{exc_id}`

                    > **Author:**
                    > {ctx.author} -- {ctx.author.mention} -- `{ctx.author.id}`

                    > **Message:** -- `{ctx.message.id}`
                    > ```{ctx.message.content}```

                    > **Channel:**
                    > {ctx.channel} -- {ctx.channel.mention} -- `{ctx.channel.id}`

                    > **Guild:**
                    > {ctx.guild} -- `{ctx.guild.id}`

                    > **Command:**
                    > `{ctx.command.name}` 
                    > {ctx.message.content[len(ctx.prefix):]}
                """,
                color=0xff0000
            )
        )
        for chunk in chunked:
            _embeds.append(ApertureEmbed.default(ctx, description=chunk, color=0xff0000))

        if len(_embeds) > 10:
            for i in range(0, len(_embeds), 10):
                await self.webhook.send(username='Aperture Error Logging', avatar_url=ctx.me.avatar.url, embeds=_embeds[i:i+10])
        else:
            await self.webhook.send(username='Aperture Error Logging', avatar_url=ctx.me.avatar.url, embeds=_embeds)

        traceback.print_exception(type(error), error, error.__traceback__, file=sys.stderr)

        return exc_id
