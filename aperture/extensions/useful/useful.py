import os
from typing import List
import aiohttp

from discord.ext import commands

from aperture import ApertureBot
from aperture.core import ApertureContext
from aperture.utils import Paginator

class Useful(commands.Cog):
    def __init__(self, bot: ApertureBot) -> None:
        self.bot = bot
        self.description = 'Some Useful commands'

        self.snekbox_url = os.getenv('SNEKBOX_URL')
        self._snekbox_jobs: List[int] = []

    @commands.command(
        name='run',
        aliases=['eval', 'code', 'exec'],
        brief='Run this code...',
        description='The command evaluates a Python Code and returns the output',
        help="""The command takes in a valid Python code and evaluates it and returns the Output with the HTTP return code.

`code`: The code to execute. This can be raw string or a code block with language highlighter as `py`, `python` or None""",
        usage='<code: str>'
    )
    @commands.cooldown(3, 15, commands.BucketType.user)
    @commands.max_concurrency(15, commands.BucketType.guild)
    async def public_eval(self, ctx: ApertureContext, *, code: str) -> None:
        if ctx.author.id in self._snekbox_jobs:
            return await ctx.reply('You already have a job running... Please wait the running job to finish.')

        def clean_format(code: str):
            code = code.replace('```', '')
            to_remove = ('py\n', 'python\n', '\n')
            for prefix in to_remove:
                if code.startswith(prefix):
                    code = code.replace(prefix, '', 1)
            return code
        
        code = clean_format(code)
        self._snekbox_jobs.append(ctx.author.id)

        async with ctx.typing():
            payload = {'input': code}
            try:
                response = await self.bot.aiohttp_session.post(self.snekbox_url, json=payload)
            except aiohttp.ClientConnectionError:
                await ctx.freply("Can't connect to the server... Please try again after a few minutes.")
                self._snekbox_jobs.remove(ctx.author.id)
                return

            out = await response.json()
            stdout = out['stdout']
            return_code = out['returncode']
            if not stdout:
                stdout = 'None'

            output = f'```py\n{stdout}```\nReturn Code: `{return_code}`'
            
            if len(output) > 2000:
                temp = [stdout[i:i+1970] for i in range(0, len(stdout), 1970)]
                final = ['```py\n' + i + '```' + f'\nReturn Code: `{return_code}`' for i in temp]
                await Paginator(content=final, prefix=None, suffix=None).start(ctx)
            else:
                await ctx.freply(output)

            self._snekbox_jobs.remove(ctx.author.id)
