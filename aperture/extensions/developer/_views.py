from discord import Interaction
from discord.ui import View

from ._buttons import ConfirmButton, CancelButton


class ConfirmationView(View):
    def __init__(self, ctx, *, timeout: float):
        super().__init__(timeout=timeout)

        self.ctx = ctx
        self.value = None

        self.add_item(ConfirmButton())
        self.add_item(CancelButton())

    async def interaction_check(self, interaction: Interaction) -> bool:
        return interaction.user.id == self.ctx.author.id