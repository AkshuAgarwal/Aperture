from typing import ClassVar, List, Optional, TypedDict, NamedTuple

from discord import ButtonStyle, Interaction, Member, Message
from discord.ui import button, Button, View

from aperture.core import emoji


class TicTacToeButton(Button):
    def __init__(self, x: int, y: int):
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

        # If current turn (button clicked) is of X
        if view.cur_player[0] == view.X:
            self.style = ButtonStyle.danger
            self.emoji = emoji.tttx
            self.disabled = True
            view.board[self.y][self.x] = view.X
            view.cur_player = view.O, view._players['player_o']
            _desc = f"It's {view._players['player_o'].mention}'s Turn!"

        # If current turn (button clicked) is of Y
        elif view.cur_player[0] == view.O:
            self.style = ButtonStyle.success
            self.emoji = emoji.ttto
            self.disabled = True
            view.board[self.y][self.x] = view.O
            view.cur_player = view.X, view._players['player_x']
            _desc = f"It's {view._players['player_x'].mention}'s Turn!" # X's

        # Check for Result (if there is any)
        _result = view.check_result()
        if _result is not None: # This means match is over!
            if _result == view.X: # We got X as Winner!
                _desc = f"{view._players['player_x'].mention} Won!"
            elif _result == view.O: # We got Y as Winner!
                _desc = f"{view._players['player_o'].mention} Won!"
            else: # Match Tie!
                _desc = "It's a Tie!"

            for child in view.children:
                child.disabled = True

            view.stop()

        await interaction.response.edit_message(content=_desc, view=view)


# Using typed stuff just for easy understanding and make the life easier :)
class Players(TypedDict):
    player_x: Member
    player_o: Member

class Player(NamedTuple):
    player_val: int
    player: Member


class TicTacToeView(View):
    X: ClassVar[int] = 1
    O: ClassVar[int] = -1
    Tie: ClassVar[int] = 2

    def __init__(self, *, timeout: Optional[float] = 30.0, players: Players, response: Message) -> None:
        super().__init__(timeout=timeout)
        self._response = response
        self._players = players
        self.cur_player: Player = self.X, self._players['player_x']

        self.board = [ # create the board
            [0, 0, 0],
            [0, 0, 0],
            [0, 0, 0],
        ]

        for x in range(3):
            for y in range(3):
                self.add_item(TicTacToeButton(x, y)) # Add the Buttons to view

    def check_result(self) -> Optional[int]:
        # Check for horizontal rows
        for row in self.board:
            _value = sum(row)

            if _value == 3:
                return self.X
            elif _value == -3:
                return self.O

        # Check for vertical Columns
        for col in range(3):
            _value = self.board[0][col] + self.board[1][col] + self.board[2][col]

            if _value == 3:
                return self.X
            elif _value == -3:
                return self.O

        # Check for diagonals
        ## Checking for 1st diagonal
        _value = 0
        for item in range(3):
            _value += self.board[item][2-item]

        if _value == 3:
            return self.X
        elif _value == -3:
            return self.O

        ## Checking for 2nd diagonal
        _value = 0
        for item in range(3):
            _value += self.board[item][item]

        if _value == 3:
            return self.X
        elif _value == -3:
            return self.O

        # No case matched, now let's check if it was a tie
        if all(i != 0 for row in self.board for i in row): # Check whether any value is still 0. If yes, the match is not yet Tie
            return self.Tie

        return None # let the match continue if none of the cases matched

    async def interaction_check(self, interaction: Interaction) -> bool:
        return interaction.user.id == self.cur_player[1].id

    async def on_timeout(self) -> None:
        self._players: List[Member] = [value for _, value in self._players.items() if value != self.cur_player[1]]
        for child in self.children:
            child.disabled = True
        await self._response.edit(content=f':alarm_clock: {self.cur_player[1].mention} timed out responding... Therefore, {self._players[0].mention} Won! :tada:', view=self)


class RequestToPlayView(View):
    def __init__(self, ctx, *, timeout: Optional[float] = 30.0, player_list: list) -> None:
        super().__init__(timeout=timeout)
        self.ctx = ctx
        self._player_list = player_list
        self.response: Optional[Message] = None

    @button(label='Join', style=ButtonStyle.success, emoji=emoji.door)
    async def _join_button(self, button: Button, interaction: Interaction) -> None:
        self._player_list['player_o'] = interaction.user
        await interaction.response.send_message(content=f'{emoji.greenTick} Joined the Match!', ephemeral=True)
        self.stop()

    async def interaction_check(self, interaction: Interaction) -> bool:
        return interaction.user.id != self.ctx.author.id

    async def on_timeout(self) -> None:
        self.children[0].disabled = True
        await self.response.edit(content='Timed out waiting for players to Join...', view=self)

class ConfirmationView(View):
    def __init__(self, *, timeout: Optional[float] = 30.0, confirm_from: Member) -> None:
        super().__init__(timeout=timeout)
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
