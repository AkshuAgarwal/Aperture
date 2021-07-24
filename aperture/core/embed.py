"""
Aperture - A Multi-Purpose Discord Bot
Copyright (C) 2021-present  AkshuAgarwal

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""

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
