import datetime
from typing import Union

from discord import Colour, Embed
from discord.embeds import _EmptyEmbed, EmptyEmbed
from discord.ext.commands import Context


class CustomEmbed(Embed):
    def __init__(
        self,
        *,
        colour: Union[int, Colour, _EmptyEmbed] = EmptyEmbed,
        color: Union[int, Colour, _EmptyEmbed] = EmptyEmbed,
        title = EmptyEmbed,
        type = 'rich',
        url = EmptyEmbed,
        description = EmptyEmbed,
        timestamp: datetime.datetime = None,
    ):
        super().__init__(
            colour=colour, color=color, title=title, type=type, url=url, description=description, timestamp=timestamp
        )

    @classmethod
    def default(
        cls,
        context: Context,
        *,
        colour: Union[int, Colour, _EmptyEmbed] = EmptyEmbed,
        color: Union[int, Colour, _EmptyEmbed] = EmptyEmbed,
        title = EmptyEmbed,
        type = 'rich',
        url = EmptyEmbed,
        description = EmptyEmbed,
        timestamp: datetime.datetime = None,
    ) -> Embed:
        if color is EmptyEmbed and colour is EmptyEmbed:
            _color = 0x0CE6F5
        elif not color is EmptyEmbed and not colour is EmptyEmbed:
            _color = color
        else:
            _color = color if color is not EmptyEmbed else colour

        _embed = cls(
            color=_color,
            title=title,
            type=type,
            url=url,
            description=description,
            timestamp=datetime.datetime.now()
        )
        _embed.set_author(name=context.author, icon_url=context.author.avatar.url)
        _embed.set_footer(text=f'Thanks for using {context.me.name}', icon_url=context.me.avatar.url)
        return _embed
