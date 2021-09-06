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
from typing import TYPE_CHECKING, Set, Tuple

import os
import re
import io
import aiohttp
import logging
import contextlib
import traceback
import textwrap
import signal

import discord
from discord.ext import commands
from aperture.core.cooldown import ApertureCooldown

from aperture.core import ApertureContext, ApertureEmoji
from aperture.core.types import CommandKwargsPayload

if TYPE_CHECKING:
    from aperture import ApertureBot


log = logging.getLogger(__name__)

# Thanks https://github.com/python-discord/bot for the regex :)
FORMATTED_CODE_REGEX = re.compile(
    r"(?P<delim>(?P<block>```)|``?)"        # code delimiter: 1-3 backticks; (?P=block) only matches if it's a block
    r"(?(block)(?:(?P<lang>[a-z]+)\n)?)"    # if we're in a block, match optional language (only letters plus newline)
    r"(?:[ \t]*\n)*"                        # any blank (empty or tabs/spaces only) lines before the code
    r"(?P<code>.*?)"                        # extract all code inside the markup
    r"\s*"                                  # any more whitespace before the end of the code markup
    r"(?P=delim)",                          # match the exact same delimiter from the start again
    re.DOTALL | re.IGNORECASE               # "." also matches newlines, case insensitive
)

RAW_CODE_REGEX = re.compile(
    r"^(?:[ \t]*\n)*"                       # any blank (empty or tabs/spaces only) lines before the code
    r"(?P<code>.*?)"                        # extract all the rest as code
    r"\s*$",                                # any trailing whitespace until the end of the string
    re.DOTALL                               # "." also matches newlines
)

ESCAPE_REGEX = re.compile("[`\u202E\u200B]{3,}")


class Snekbox:
    def __init__(self, bot: ApertureBot) -> None:
        self.bot = bot
        self._cooldown_creator = ApertureCooldown(
            bot,
            **{
                'normal_cooldown': commands.Cooldown(3, 30),
                'premium_cooldown': commands.Cooldown(3, 15)
            }
        )
        kwargs = self._prepare_command()
        self._command = commands.Command(self.callback, **kwargs)

        self.snekbox_url: str = os.getenv('SNEKBOX_URL')
        self.running_jobs: Set[int] = set()


    def _prepare_command(self) -> CommandKwargsPayload:
        kwargs: CommandKwargsPayload = {
            'name': 'snekbox',
            'aliases': ['eval', 'exec'],
            'brief': 'Evaluate a Python code',
            'description': 'The code takes in a Python code evaluates it and returns the Output with a Python return code.',
            'help': """You can only run one evaluation job at a time.
                    Very long outputs will either be paginated or if the OS kills the process, you'll be returned with an Error return code instead.

                    `code`: The code to evaluate. This can be a raw string, a simple code block, or a python language highlighted code block.
                    """,
            'usage': '<code: str>',
            'cooldown': commands.DynamicCooldownMapping(self._cooldown_creator.default_cooldown, type=commands.BucketType.user),
            'max_concurrency': commands.MaxConcurrency(10, per=commands.BucketType.guild, wait=False),
        }
        return kwargs


    @staticmethod
    def parse_codeblock(code: str) -> str:
        if match := list(FORMATTED_CODE_REGEX.finditer(code)):
            blocks = [block for block in match if block.group('block')]

            if len(blocks) > 1:
                code = '\n'.join(block.group('code') for block in blocks)
            else:
                match = match[0] if len(blocks) == 0 else blocks[0]
                code, *_ = match.group('code', 'block', 'lang', 'delim')

        else:
            code = RAW_CODE_REGEX.fullmatch(code).group('code')

        code = textwrap.dedent(code)
        return code

    # Thanks https://github.com/python-discord/bot for this too :)
    @staticmethod
    def get_return_message(result: dict) -> Tuple[str, str]:
        stdout, returncode = result['stdout'], result['returncode']
        response = f'Your Evaluation job has completed and responded with Return Code `{returncode}`'
        error = ''

        if returncode is None:
            response = 'Your eval job has failed'
            error = stdout.strip()
        elif returncode == 128 + 9: # 128 + SIGKILL
            response = 'Your eval job timed out or ran out of memory'
        elif returncode ==  255:
            response = 'Your eval job has failed'
            error = 'A fatal NsJail error occured'
        else:
            try:
                name = signal.Signals(returncode - 128).name
                response = f'{response} ({name})'
            except ValueError:
                pass

        if not stdout.strip(): # No output
            response = f'{ApertureEmoji.warning} ' + response
        elif returncode == 0: # No error
            response = f'{ApertureEmoji.tick} ' + response
        else: # Some Exception
            response = f'{ApertureEmoji.cross} ' + response
        
        return response, error


    async def callback(self, _: commands.Cog, ctx: ApertureContext, *, code: str) -> None:
        if ctx.author.id in self.running_jobs:
            return await ctx.reply(
                'You already have an eval job running... Please wait it to finish before starting another'
            )

        log_msg = 'Snekbox server responded with HTTP Status code %s for '\
            'Message ID: %s, Author ID: %s, Channel ID: %s, Guild ID: %s'

        self.running_jobs.add(ctx.author.id)

        formatted_code = self.parse_codeblock(code)

        async with ctx.typing():
            payload = {'input': formatted_code}
            try:
                response = await ctx.bot.http_session.post(self.snekbox_url, json=payload)
                log.debug('Code sent for evaluation to snekbox. Code: %s', formatted_code)
            except aiohttp.ClientConnectorError as e:
                with contextlib.suppress(KeyError):
                    self.running_jobs.remove(ctx.author.id)
                await ctx.reply('Oops! Failed to connect to the server. Please try again after some time')
                exc = ''.join(traceback.format_exception(type(e), e, e.__traceback__))
                await ctx.bot.webhook_client.send_critical_report(
                    ctx,
                    f'Failed to connect to the Snekbox Server!\nException: ```{exc}```'
                )
                log.error('Failed to connect to Snekbox')
                return

            result = await response.json()

            stdout, http_status = result['stdout'], response.status

            with contextlib.suppress(KeyError):
                self.running_jobs.remove(ctx.author.id)

            if http_status != 200:
                if str(http_status)[0] in ['1', '2']:
                    log_method = log.debug
                elif str(http_status)[0] in ['3', '4', '5']:
                    log_method = log.warn
                log_method(log_msg, http_status, ctx.message.id, ctx.author.id,
                        ctx.channel.id, ctx.guild.id if ctx.guild is not None else None)

                return await ctx.reply(
                    f'Oops! The eval job failed with HTTP Status code `{http_status}`. '
                    'Please try again after some time'
                )

            response, error = self.get_return_message(result)
            content = error if error else stdout
            output = response +  '\n\n' + '```\n' + '[No Output]' + '```' if not content else '\n\n' + '```py\n' + content + '```'

            if len(output.split('\n')) > 15 or len(output) > 1900: # Idk, Just in case, keep the max limit a bit less than 2000
                buffer = io.StringIO(content)
                buffer.seek(0)
                file = discord.File(buffer, filename='output.txt')
                return await ctx.send(response, file=file)

            return await ctx.reply(output)

# TODO: fix cooldown for owner
