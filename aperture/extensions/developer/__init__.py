from .developer import Developer
from aperture import ApertureBot

def setup(bot: ApertureBot) -> None:
    bot.add_cog(Developer(bot))