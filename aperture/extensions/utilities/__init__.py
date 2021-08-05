from .utilities import Utilities
from aperture import ApertureBot

def setup(bot: ApertureBot) -> None:
    bot.add_cog(Utilities(bot))
