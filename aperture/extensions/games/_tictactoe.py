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

from typing import ClassVar, List, Optional, TypedDict, NamedTuple

from discord import ButtonStyle, Interaction, Member, Message
from discord.ui import button, Button, Item, View

from aperture.core import ApertureContext, emoji, view_error_handler


class Players(TypedDict):
    player_x: Member
    player_o: Member

class Player(NamedTuple):
    player_val: int
    player: Member


class TicTacToeButton(Button):
    def __init__(self, x: int, y: int) -> None:
        super().__init__(
            style=ButtonStyle.blurple,
            label='\u200b',
            emoji=emoji.invisible,
            row=y
        )
        self.x = x
        self.y = y

    async def callback(self, interaction: Interaction) -> None:
        view: TicTacToeView = self.view

        if view.cur_player[0] == view.X:
            self.style = ButtonStyle.danger
            self.emoji = emoji.tttx
            self.disabled = True
            view.board[self.y][self.x] = view.X
            view.cur_player = view.O, view._players['player_o']
            _description: str = f"It's {view._players['player_o'].mention}'s Turn!"

        elif view.cur_player[0] == view.O:
            self.style = ButtonStyle.success
            self.emoji = emoji.ttto
            self.disabled = True
            view.board[self.y][self.x] = view.O
            view.cur_player = view.X, view._players['player_x']
            _description: str = f"It's {view._players['player_x'].mention}'s Turn!"

        _result = view.check_result()
        if _result is not None:
            if _result == view.X:
                _description: str = f"{view._players['player_x'].mention} Won!"
            elif _result == view.O:
                _description: str = f"{view._players['player_o'].mention} Won!"
            else:
                _description: str = "It's a Tie!"

            for child in view.children:
                child.disabled = True

            view.stop()

        await interaction.response.edit_message(content=_description, view=view)

class TicTacToeView(View):
    X: ClassVar[int] = 1
    O: ClassVar[int] = -1
    Tie: ClassVar[int] = 2

    def __init__(
        self,
        ctx: ApertureContext,
        *,
        timeout: Optional[float] = 30.0,
        players: Players,
        response: Message
    ) -> None:
        super().__init__(timeout=timeout)
        self.ctx = ctx
        self._response = response
        self._players = players
        self.cur_player: Player = self.X, self._players['player_x']

        self.board: List[List[int]] = [
            [0, 0, 0],
            [0, 0, 0],
            [0, 0, 0],
        ]

        for x in range(3):
            for y in range(3):
                self.add_item(TicTacToeButton(x, y))

    def check_result(self) -> Optional[int]:
        for row in self.board:
            _value = sum(row)

            if _value == 3:
                return self.X
            elif _value == -3:
                return self.O

        for col in range(3):
            _value = self.board[0][col] + self.board[1][col] + self.board[2][col]

            if _value == 3:
                return self.X
            elif _value == -3:
                return self.O

        _value = 0
        for item in range(3):
            _value += self.board[item][2-item]

        if _value == 3:
            return self.X
        elif _value == -3:
            return self.O

        _value = 0
        for item in range(3):
            _value += self.board[item][item]

        if _value == 3:
            return self.X
        elif _value == -3:
            return self.O

        if all(i != 0 for row in self.board for i in row):
            return self.Tie

        return None

    async def interaction_check(self, interaction: Interaction) -> bool:
        return interaction.user.id == self.cur_player[1].id

    async def on_timeout(self) -> None:
        self._players: List[Member] = [value for _, value in self._players.items() if value != self.cur_player[1]]
        for child in self.children:
            child.disabled = True
        await self._response.edit(
            content=f':alarm_clock: {self.cur_player[1].mention} timed out responding...\nTherefore, '\
                f'{self._players[0].mention} Won! :tada:',
            view=self)

    async def on_error(self, error: Exception, item: Item, interaction: Interaction) -> None:
        await view_error_handler(self.ctx, error, item, interaction)

class RequestToPlayView(View):
    def __init__(self, ctx: ApertureContext, *, timeout: Optional[float] = 30.0, player_list: Players) -> None:
        super().__init__(timeout=timeout)
        self.ctx = ctx
        self._player_list = player_list
        self.response: Optional[Message] = None

    @button(label='Join', style=ButtonStyle.success, emoji=emoji.door)
    async def _join_button(self, _, interaction: Interaction) -> None:
        self._player_list['player_o'] = interaction.user
        await interaction.response.send_message(content=f'{emoji.greenTick} Joined the Match!', ephemeral=True)
        self.stop()

    async def interaction_check(self, interaction: Interaction) -> bool:
        return interaction.user.id != self.ctx.author.id

    async def on_timeout(self) -> None:
        self.children[0].disabled = True
        await self.response.edit(content='Timed out waiting for players to Join...', view=self)

    async def on_error(self, error: Exception, item: Item, interaction: Interaction) -> None:
        await view_error_handler(self.ctx, error, item, interaction)

class ConfirmationView(View):
    def __init__(self, ctx: ApertureContext, *, timeout: Optional[float] = 30.0, confirm_from: Member) -> None:
        super().__init__(timeout=timeout)
        self.ctx = ctx
        self.opponent = confirm_from
        self.state: Optional[bool] = None
        self.response: Optional[Message] = None

    @button(label='Yes', style=ButtonStyle.success, emoji=emoji.yes)
    async def _button_yes(self, _, interaction: Interaction) -> None:
        self.state = True
        await interaction.response.send_message(f'{emoji.greenTick} Joined the Match!', ephemeral=True)
        self.stop()

    @button(label='No', style=ButtonStyle.danger, emoji=emoji.no)
    async def _button_no(self, *_) -> None:
        self.state = False
        self.stop()

    async def interaction_check(self, interaction: Interaction) -> bool:
        return interaction.user.id == self.opponent.id

    async def on_timeout(self) -> None:
        for child in self.children:
            child.disabled = True
        await self.response.edit(content=f"{self.opponent.name} didn't responded...", view=self)

    async def on_error(self, error: Exception, item: Item, interaction: Interaction) -> None:
        await view_error_handler(self.ctx, error, item, interaction)
