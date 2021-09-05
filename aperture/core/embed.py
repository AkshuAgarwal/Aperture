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

from __future__ import annotations
from typing import Any, Optional, Union, TYPE_CHECKING

import datetime

from discord import Embed, Colour
from discord.embeds import EmptyEmbed

from ..core import constants

if TYPE_CHECKING:
    from discord.embeds import _EmptyEmbed, MaybeEmpty
    from discord.types.embed import EmbedType

    from .context import ApertureContext


class ApertureEmbed(Embed):
    def __init__(
        self,
        *,
        colour: Union[int, Colour, _EmptyEmbed] = EmptyEmbed,
        color: Union[int, Colour, _EmptyEmbed] = EmptyEmbed,
        title: MaybeEmpty[Any] = EmptyEmbed,
        type: EmbedType = 'rich',
        url: MaybeEmpty[Any] = EmptyEmbed,
        description: MaybeEmpty[Any] = EmptyEmbed,
        timestamp: Optional[datetime.datetime] = None
    ):
        super().__init__(
            colour=colour, color=color, title=title, type=type, url=url, description=description, timestamp=timestamp
        )

    @classmethod
    def default(
        cls,
        context: ApertureContext,
        *,
        colour: Union[int, Colour, _EmptyEmbed] = EmptyEmbed,
        color: Union[int, Colour, _EmptyEmbed] = EmptyEmbed,
        title: MaybeEmpty[Any] = EmptyEmbed,
        type: EmbedType = 'rich',
        url: MaybeEmpty[Any] = EmptyEmbed,
        description: MaybeEmpty[Any] = EmptyEmbed,
        timestamp: Optional[datetime.datetime] = None
    ):
        if color is EmptyEmbed and colour is EmptyEmbed:
            _color = constants.EMBED_DEFAULT_COLOR
        elif color is not EmptyEmbed and colour is not EmptyEmbed:
            _color = colour
        else:
            _color = color if color is not EmptyEmbed else colour

        _timestamp: datetime.datetime = timestamp or datetime.datetime.now()

        embed = cls(
            color = _color,
            title = title,
            type = type,
            url = url,
            description = description,
            timestamp = _timestamp
        ).set_author(
            name=context.author, icon_url=context.author.display_avatar
        ).set_footer(
            text=f'Thanks for using {context.me.name}', icon_url=context.me.display_avatar
        )

        return embed
