from discord import PartialEmoji, ButtonStyle
from discord.ui import Button

from aperture.core import emoji


class ConfirmButton(Button):
    def __init__(self) -> None:
        super().__init__(
            label='Confirm',
            style=ButtonStyle.success,
            emoji=PartialEmoji.from_str(emoji.greenTick)
        )
        
    async def callback(self, _) -> None:
        self.view.value = True
        for child in self.view.children:
            child.disabled = True
        self.view.stop()

class CancelButton(Button):
    def __init__(self) -> None:
        super().__init__(
            label='Cancel',
            style=ButtonStyle.danger,
            emoji=PartialEmoji.from_str(emoji.redCross)
        )
        
    async def callback(self, _) -> None:
        self.view.value = False
        for child in self.view.children:
            child.disabled = True
        self.view.stop()
