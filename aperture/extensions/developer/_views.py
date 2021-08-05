from typing import Optional

from discord import Interaction
from discord.ui import Item, View

from ._buttons import ConfirmButton, CancelButton
from aperture.core import ApertureContext, view_error_handler


class ConfirmationView(View):
    def __init__(self, ctx: ApertureContext, *, timeout: Optional[float]=30.0):
        super().__init__(timeout=timeout)

        self.ctx = ctx
        self.value: Optional[bool] = None

        self.add_item(ConfirmButton())
        self.add_item(CancelButton())

    async def interaction_check(self, interaction: Interaction) -> bool:
        return interaction.user.id == self.ctx.author.id

    async def on_error(self, error: Exception, item: Item, interaction: Interaction) -> None:
        await view_error_handler(self.ctx.bot, error, item, interaction)
