from .useful import Useful
from aperture import ApertureBot

def setup(bot: ApertureBot) -> None:
    bot.add_cog(Useful(bot))