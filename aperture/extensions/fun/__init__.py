from .fun import Fun
from aperture import ApertureBot

def setup(bot: ApertureBot) -> None:
    bot.add_cog(Fun(bot))