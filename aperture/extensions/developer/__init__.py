from .developer import Developer

def setup(bot):
    bot.add_cog(Developer(bot))