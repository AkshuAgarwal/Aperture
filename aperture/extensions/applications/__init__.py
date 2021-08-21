from .applications import Applications
from aperture import ApertureBot

def setup(bot: ApertureBot):
    bot.add_cog(Applications(bot))
