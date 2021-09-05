from __future__ import annotations

from typing import Tuple, TYPE_CHECKING
from discord.ext import commands

from .snekbox import Snekbox

if TYPE_CHECKING:
    from aperture import ApertureBot

class Useful(commands.Cog):
    """Some Useful commands like python eval and more!"""

    def __init__(self, bot: ApertureBot) -> None:
        self.bot = bot

        self.__cog_commands__: Tuple[commands.Command] = (
            Snekbox(bot)._command,
        )

def setup(bot: ApertureBot) -> None:
    bot.add_cog(Useful(bot))
