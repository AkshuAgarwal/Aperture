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

import asyncio
from typing import Optional

from discord import Member, Message
from discord.ext import commands

from ._tictactoe import (
    TicTacToeView,
    RequestToPlayView,
    ConfirmationView,
    Players as TicTacToePlayers
)

from aperture.core import emoji


class Games(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.description = "Bot Games to play. Also includes Multiplayer Games!"


    @commands.command(
        name='tictactoe',
        aliases=['ttt'],
        brief="Let's have a Match of TicTacToe!",
        description='The command is used to start a Match of TicTacToe between 2 players',
        help="""""", # TODO: Add it later
        usage='' # TODO: Add it later too
    )
    @commands.guild_only()
    @commands.cooldown(1, 15, commands.BucketType.user)
    async def _tictactoe(self, ctx, opponent: Optional[Member]=None) -> Message:
        _players: TicTacToePlayers = {'player_x': ctx.author}

        if not opponent:
            request_view = RequestToPlayView(ctx, player_list=_players)
            _resp: Message = await ctx.freply(
                'A match of Tic-Tac-Toe is going to be Started! Click on the `Join` button to Enter', view=request_view
            )
            request_view.response = _resp
            await request_view.wait()

            if not _players.get('player_o'):
                return

            await _resp.edit(
                content=f'{_players["player_o"].mention} Joined! Starting the Match in 5 Seconds...', view=None
            )
            await asyncio.sleep(5)
        
        else:
            if opponent.id == ctx.author.id:
                return await ctx.freply(f"{emoji.redCross} You can't play with yourself...")
            confirm_view = ConfirmationView(confirm_from=opponent)
            _resp: Message = await ctx.freply(
                f'{opponent.mention}, Would you like to join a Match of Tic-Tac-Toe against {ctx.author.name}?',
                view=confirm_view
            )
            confirm_view.response = _resp
            await confirm_view.wait()

            if confirm_view.state is None:
                return
            elif confirm_view.state is False:
                return await _resp.edit(content=f'{opponent.mention} refused to Join... :(', view=None)
            else:
                _players['player_o'] = opponent
                await _resp.edit(content=f'{opponent.mention} Joined! Starting the Match in 5 Seconds...', view=None)
                await asyncio.sleep(5)

        _view = TicTacToeView(players=_players, response=_resp)
        return await _resp.edit(content=f"It's now {ctx.author.mention}'s Turn!", view=_view)
