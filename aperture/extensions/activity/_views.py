from contextlib import suppress
from typing import Optional

from discord import (
    ButtonStyle,
    HTTPException,
    Interaction,
    Invite,
    InviteTarget,
    Message,
    NotFound,
    SelectOption,
    VoiceChannel
)
from discord.ui import Button, Item, View, select, button
from discord.ext.commands import Context

from aperture.core.error import view_error_handler


vc_application_ids: dict = {
    'betrayal': 773336526917861400,
    'chess': 832012586023256104,
    'fishing': 814288819477020702,
    'poker': 755827207812677713,
    'youtube': 755600276941176913,
}

class VCActivity(View):
    def __init__(self, ctx: Context, *, channel: VoiceChannel, timeout: Optional[float] = 30.0):
        super().__init__(timeout=timeout)
        self.ctx = ctx
        self.channel = channel
        self.message: Optional[Message] = None

    @select(
        options=[
            SelectOption(label='Betrayal.io', value='betrayal'),
            SelectOption(label='CG 2 DEV', value='chess'),
            SelectOption(label='Fishington.io', value='fishing'),
            SelectOption(label='Poker Night', value='poker'),
            SelectOption(label='YouTube Together', value='youtube'),
        ],
        min_values=1,
        max_values=1
    )
    async def callback(self, *_): ...

    @button(label='Create Activity', style=ButtonStyle.primary)
    async def create_link(self, _, interaction: Interaction):
        reason = 'Activity Link created using `activity` command.'
        with suppress(AttributeError):
            reason = f'Activity link created using `activity` command, requested by {self.message.author} - {self.message.author.id}'
        _invite: Invite = await self.channel.create_invite(
            reason=reason,
            max_age=0,
            max_uses=0,
            target_type=InviteTarget.embedded_application,
            target_application_id=vc_application_ids[self.children[0].values[0]]
        )
        link_btn = Button(label='Join the Activity!', style=ButtonStyle.link, url=_invite.url)
        self.clear_items()
        self.add_item(link_btn)
        await interaction.response.edit_message(content='Click here to join the Activity!', view=self)
        self.stop()

    async def interaction_check(self, interaction: Interaction) -> bool:
        return interaction.user.id == self.ctx.author.id

    async def on_timeout(self) -> None:
        for child in self.children:
            child.disabled = True
        with suppress(HTTPException, NotFound, AttributeError):
            await self.message.edit(content='Timed out waiting for response...', view=self)

    async def on_error(self, error: Exception, item: Item, interaction: Interaction) -> None:
        await view_error_handler(error, item, interaction)
