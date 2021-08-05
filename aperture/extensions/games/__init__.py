from .games import Games
from aperture import ApertureBot

def setup(bot: ApertureBot) -> None:
    bot.add_cog(Games(bot))