from .vc_activity import Activity
from aperture import ApertureBot

def setup(bot: ApertureBot) -> None:
    bot.add_cog(Activity(bot))
