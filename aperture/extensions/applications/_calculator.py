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

import math
import simpleeval
from contextlib import suppress
from typing import Optional

from discord import ButtonStyle, Embed, Interaction, InteractionResponded, Message, NotFound
from discord.ui import View, button

from aperture.core import ApertureContext
from aperture.utils import Paginator

simpleeval.MAX_POWER = 10000


class CalculatorView(View):
    def __init__(self, ctx: ApertureContext, *, timeout: Optional[float] = 60.0):
        super().__init__(timeout=timeout)
        self.ctx = ctx
        self.response: Optional[Message] = None
        self._cur_no = 0
        self._cur_ph = ''

        self._cache = [self._cur_no]
        self._converter = {
            '(': '(',
            ')': ')',
            'p': '**',
            '/': '/',
            '-': '-',
            'x': '*',
            '.': '.',
            '+': '+'
        }

    async def interaction_check(self, interaction: Interaction) -> bool:
        return interaction.user == self.ctx.author

    async def update_placeholder(self, interaction: Interaction) -> None:
        space = '\u2002'
        total_len = 40
        _placeholder = f'```{space*(total_len-len(self._cur_ph))}{self._cur_ph}```'
        placeholder_embed: Embed = self.response.embeds[0]
        placeholder_embed.description = _placeholder
        if len(placeholder_embed) > 6000 or len(placeholder_embed.description) > 4096:
            content='Oops! Looks like the result is too Huge... The result is Paginated...'
            await Paginator(content=str(self._cur_ph)).start(self.ctx)
        else:
            content=None
        try:
            await interaction.response.edit_message(content=content, embed=placeholder_embed, view=self)
        except (InteractionResponded, NotFound):
            with suppress(NotFound):
                await self.response.edit(content=content, embed=placeholder_embed, view=self)

    @button(label='Back', style=ButtonStyle.danger)
    async def back(self, _, interaction: Interaction) -> None:
        if isinstance(self._cache[-1:][0], (int, float)):
            new_int = math.floor(self._cache[-1:][0]/10)
            self._cache[-1:] = [new_int]
            self._cur_no = new_int
        elif isinstance(self._cache[-1:][0], str):
            self._cache.pop()
            self._cur_no = self._cache[-1:][0]
        self._cur_ph = self._cur_ph[:-1]
        await self.update_placeholder(interaction)

    @button(label='CE')
    async def clear_entry(self, _, interaction: Interaction) -> None:
        self._cache = []
        self._cur_no = 0
        self._cur_ph = '0'
        await self.update_placeholder(interaction)

    @button(label='C')
    async def clear(self, _, interaction: Interaction) -> None:
        self._cache.pop()
        self._cur_no = 0
        self._cur_ph = '0'
        await self.update_placeholder(interaction)

    @button(label='(')
    async def parenthesis_left(self, _, interaction: Interaction) -> None:
        self._cur_no = 0
        if isinstance(self._cache[-1:][0], str):
            self._cache[-1:] = ['(']
        else:
            self._cache.append('(')
        self._cur_ph += '('
        await self.update_placeholder(interaction)

    @button(label=')')
    async def parenthesis_right(self, _, interaction: Interaction) -> None:
        self._cur_no = 0
        if isinstance(self._cache[-1:][0], str):
            self._cache[-1:] = [')']
        else:
            self._cache.append(')')
        self._cache.append('*')
        self._cur_ph += ')'
        await self.update_placeholder(interaction)

    @button(label='7', style=ButtonStyle.blurple)
    async def num_seven(self, _,  interaction: Interaction) -> None:
        self._cur_no = (self._cur_no*10) + 7 if self._cur_no >= 0 else (self._cur_no*10) - 7
        if isinstance(self._cache[-1:][0], (int, float)):
            self._cache[-1:] = [self._cur_no]
        else:
            self._cache.append(self._cur_no)
        self._cur_ph += '7'
        await self.update_placeholder(interaction)
    
    @button(label='8', style=ButtonStyle.blurple)
    async def num_eight(self, _,  interaction: Interaction) -> None:
        self._cur_no = (self._cur_no*10) + 8 if self._cur_no >= 0 else (self._cur_no*10) - 8
        if isinstance(self._cache[-1:][0], (int, float)):
            self._cache[-1:] = [self._cur_no]
        else:
            self._cache.append(self._cur_no)
        self._cur_ph += '8'
        await self.update_placeholder(interaction)

    @button(label='9', style=ButtonStyle.blurple)
    async def num_nine(self, _,  interaction: Interaction) -> None:
        self._cur_no = (self._cur_no*10) + 9 if self._cur_no >= 0 else (self._cur_no*10) - 9
        if isinstance(self._cache[-1:][0], (int, float)):
            self._cache[-1:] = [self._cur_no]
        else:
            self._cache.append(self._cur_no)
        self._cur_ph += '9'
        await self.update_placeholder(interaction)

    @button(label='xⁿ')
    async def x_power_n(self, _,  interaction: Interaction) -> None:
        self._cur_no = 0
        if isinstance(self._cache[-1:][0], str):
            self._cache[-1:] = ['p']
        else:
            self._cache.append('p')
        self._cur_ph += '^'
        await self.update_placeholder(interaction)

    @button(label='√')
    async def sqrt_x(self, _,  interaction: Interaction) -> None:
        self._cur_no = 0

        self._cache.insert(0, '(')
        if isinstance(self._cache[-1:][0], str):
            self._cache[-1:] = ['**0.5']
        else:
            self._cache.append('**0.5')
        self._cache.append(')')
        self._cache.append('*')

        self._cur_ph = '√(' + self._cur_ph + ')'
        await self.update_placeholder(interaction)

    @button(label='4', style=ButtonStyle.blurple)
    async def num_four(self, _,  interaction: Interaction) -> None:
        self._cur_no = (self._cur_no*10) + 4 if self._cur_no >= 0 else (self._cur_no*10) - 4
        if isinstance(self._cache[-1:][0], (int, float)):
            self._cache[-1:] = [self._cur_no]
        else:
            self._cache.append(self._cur_no)
        self._cur_ph += '4'
        await self.update_placeholder(interaction)

    @button(label='5', style=ButtonStyle.blurple)
    async def num_five(self, _,  interaction: Interaction) -> None:
        self._cur_no = (self._cur_no*10) + 5 if self._cur_no >= 0 else (self._cur_no*10) - 5
        if isinstance(self._cache[-1:][0], (int, float)):
            self._cache[-1:] = [self._cur_no]
        else:
            self._cache.append(self._cur_no)
        self._cur_ph += '5'
        await self.update_placeholder(interaction)

    @button(label='6', style=ButtonStyle.blurple)
    async def num_six(self, _,  interaction: Interaction) -> None:
        self._cur_no = (self._cur_no*10) + 6 if self._cur_no >= 0 else (self._cur_no*10) - 6
        if isinstance(self._cache[-1:][0], (int, float)):
            self._cache[-1:] = [self._cur_no]
        else:
            self._cache.append(self._cur_no)
        self._cur_ph += '6'
        await self.update_placeholder(interaction)

    @button(label='/')
    async def division(self, _,  interaction: Interaction) -> None:
        self._cur_no = 0
        if isinstance(self._cache[-1:][0], str):
            self._cache[-1:] = ['/']
        else:
            self._cache.append('/')
        self._cur_ph += '/'
        await self.update_placeholder(interaction)

    @button(label='n!')
    async def n_factorial(self, _,  interaction: Interaction) -> None:
        await interaction.response.edit_message(content='Calculating...', view=self)
        for index, key in enumerate(self._cache):
            if key in list(self._converter.keys()):
                self._cache[index] = self._converter[key]
    
        expression = ''.join(str(i) for i in self._cache)
        try:
            out = simpleeval.simple_eval(expression)
            out = math.factorial(int(out))
            self._cur_ph = str(out)
            await self.update_placeholder(interaction)
            self._cur_no = out
            self._cache = [out]
        except simpleeval.NumberTooHigh:
            await interaction.followup.send('Oops! The number is too large to be evaluated... Please try a shorter expression.', ephemeral=True)
        except SyntaxError:
            await interaction.followup.send('The expression is not a valid mathematical expression.', ephemeral=True)

    @button(label='1', style=ButtonStyle.blurple)
    async def num_one(self, _,  interaction: Interaction) -> None:
        self._cur_no = (self._cur_no*10) + 1 if self._cur_no >= 0 else (self._cur_no*10) - 1
        if isinstance(self._cache[-1:][0], (int, float)):
            self._cache[-1:] = [self._cur_no]
        else:
            self._cache.append(self._cur_no)
        self._cur_ph += '1'
        await self.update_placeholder(interaction)

    @button(label='2', style=ButtonStyle.blurple)
    async def num_two(self, _,  interaction: Interaction) -> None:
        self._cur_no = (self._cur_no*10) + 2 if self._cur_no >= 0 else (self._cur_no*10) - 2
        if isinstance(self._cache[-1:][0], (int, float)):
            self._cache[-1:] = [self._cur_no]
        else:
            self._cache.append(self._cur_no)
        self._cur_ph += '2'
        await self.update_placeholder(interaction)

    @button(label='3', style=ButtonStyle.blurple)
    async def num_three(self, _,  interaction: Interaction) -> None:
        self._cur_no = (self._cur_no*10) + 3 if self._cur_no >= 0 else (self._cur_no*10) - 3
        if isinstance(self._cache[-1:][0], (int, float)):
            self._cache[-1:] = [self._cur_no]
        else:
            self._cache.append(self._cur_no)
        self._cur_ph += '3'
        await self.update_placeholder(interaction)

    @button(label='-')
    async def subtract(self, _,  interaction: Interaction) -> None:
        self._cur_no = 0
        if isinstance(self._cache[-1:][0], str):
            self._cache[-1:] = ['-']
        else:
            self._cache.append('-')
        self._cur_ph += '-'
        await self.update_placeholder(interaction)

    @button(label='x')
    async def multiplication(self, _,  interaction: Interaction) -> None:
        self._cur_no = 0
        if isinstance(self._cache[-1:][0], str):
            self._cache[-1:] = ['x']
        else:
            self._cache.append('x')
        self._cur_ph += 'x'
        await self.update_placeholder(interaction)

    @button(label='∓')
    async def negate(self, _,  interaction: Interaction) -> None:
        if isinstance(self._cache[-1:][0], str):
            return
        elif isinstance(self._cache[-1:][0], (int, float)):
            self._cur_no = -self._cur_no
            self._cache[-1:] = [self._cur_no]
            if self._cur_no >= 0:
                self._cur_ph = self._cur_ph[1:]
            else:
                self._cur_ph = '-' + self._cur_ph
            await self.update_placeholder(interaction)

    @button(label='0', style=ButtonStyle.blurple)
    async def num_zero(self, _,  interaction: Interaction) -> None:
        self._cur_no = (self._cur_no*10) + 0 if self._cur_no >= 0 else (self._cur_no*10) - 0
        if isinstance(self._cache[-1:][0], (int, float)):
            self._cache[-1:] = [self._cur_no]
        else:
            self._cache.append(self._cur_no)
        self._cur_ph += '0'
        await self.update_placeholder(interaction)

    @button(label='.')
    async def decimal(self, _,  interaction: Interaction) -> None:
        self._cur_no = 0
        if isinstance(self._cache[-1:][0], str):
            self._cache[-1:] = ['.']
        else:
            self._cache.append('.')
        self._cur_ph += '.'
        await self.update_placeholder(interaction)

    @button(label='+')
    async def addition(self, _,  interaction: Interaction) -> None:
        self._cur_no = 0
        if isinstance(self._cache[-1:][0], str):
            self._cache[-1:] = ['+']
        else:
            self._cache.append('+')
        self._cur_ph += '+'
        await self.update_placeholder(interaction)

    @button(label='=', style=ButtonStyle.success)
    async def equals_to(self, _,  interaction: Interaction) -> None:
        await interaction.response.edit_message(content='Calculating...', view=self)
        for index, key in enumerate(self._cache):
            if key in list(self._converter.keys()):
                self._cache[index] = self._converter[key]
    
        expression = ''.join(str(i) for i in self._cache)
        try:
            out = simpleeval.simple_eval(expression)
            self._cur_ph = str(out)
            await self.update_placeholder(interaction)
            self._cur_no = out
            self._cache = [out]
        except simpleeval.NumberTooHigh:
            await interaction.followup.send('Oops! The number is too large to be evaluated... Please try a shorter expression.', ephemeral=True)
        except SyntaxError:
            await interaction.followup.send('The expression is not a valid mathematical expression.', ephemeral=True)