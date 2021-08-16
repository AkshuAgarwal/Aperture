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

from typing import List, Optional, Union, overload
from contextlib import suppress

from discord import (
    ButtonStyle,
    Embed,
    Interaction,
    Message,
    HTTPException,
    InvalidArgument,
    NotFound,
)
from discord.ui import Item, View, button

from aperture.core import ApertureContext, ApertureEmoji, view_error_handler
from aperture.core.error import ConflictingArguments, MissingAllArguments


__all__ = ('Paginator', )

suppressed_errors = (HTTPException, NotFound, )

Page = Union[str, Embed]


class Paginator:
    @overload
    def __init__(
        self,
        embeds: List[Embed] = ...,
        *,
        timeout: Optional[float] = ...
    ) -> None:
        ...

    @overload
    def __init__(
        self,
        content: str = ...,
        *,
        prefix: Optional[str] = ...,
        suffix: Optional[str] = ...,
        max_length: Optional[int] = ...,
        timeout: Optional[float] = ...
    ) -> None:
        ...

    def __init__(
        self,
        embeds: Optional[List[Embed]] = None,
        content: Optional[str] = None,
        *,
        prefix: Optional[str] = '```',
        suffix: Optional[str] = '```',
        max_length: Optional[int] = 2000,
        timeout: Optional[float] = 60.0
    ) -> None:
        self.timeout = timeout

        if not embeds and not content:
            raise MissingAllArguments(['embeds', 'content'])
        if embeds is not None and content is not None:
            raise InvalidArgument('cannot pass both embeds and content parameter to Paginator')

        if embeds:
            self._pages = embeds
        else:
            _page_length = max_length - (len(prefix) + len(suffix))
            self._pages = [prefix + content[i:i+_page_length] + suffix for i in range(0, len(content), _page_length)]

    async def start(self, ctx: ApertureContext, **kwargs) -> Message:
        view = PaginatorView(ctx, pages=self._pages, timeout=self.timeout)
        response = await view.start(**kwargs)
        return response

    @property
    def pages(self) -> List[Page]:
        return self._pages

    def add_page(self, page: Page, index: Optional[int]=None) -> List[Page]:
        if not isinstance(page, self._pages[0]):
            raise TypeError(
                f'Cannot add page of type {page.__class__!r} into the list of {self._pages[0].__class__!r}'
            )
        if not index:
            self._pages.append(page)
        else:
            self._pages.insert(index, page)
        return self._pages

    @overload
    def remove_page(self, page: Optional[Page] = ...) -> List[Page]:
        ...

    @overload
    def remove_page(self, index: Optional[int] = ...) -> List[Page]:
        ...

    def remove_page(self, page: Optional[Page]=None, index: Optional[int]=None) -> List[Page]:
        if not any(page, index):
            raise MissingAllArguments(['page', 'index'])
        if all(page, index):
            raise ConflictingArguments(['page', 'index'])

        if page:
            self._pages.pop(self._pages.index(page))
        elif index:
            self._pages.pop(index)
        return self._pages


class PaginatorView(View):
    def __init__(self, ctx: ApertureContext, *, pages: List[Page], timeout: Optional[float]=60.0) -> None:
        super().__init__(timeout=timeout)
        self.ctx = ctx
        self._pages = pages
        self._current_index: int = 0
        self._interaction_message: Optional[Message] = None

    @button(style=ButtonStyle.blurple, emoji=ApertureEmoji.pag_toStart)
    async def _start(self, _, interaction: Interaction) -> None:
        for child in self.children:
            child.disabled = False
        self._current_index = 0
        for child in self.children:
            if child.emoji.name in self._what_to_disable():
                child.disabled = True
        self.update_page_no()
        try:
            if isinstance(self._pages[0], str):
                await interaction.message.edit(content=self._pages[0], view=self)
            elif isinstance(self._pages[0], Embed):
                await interaction.message.edit(embed=self._pages[0], view=self)
        except suppressed_errors:
            self.stop()

    @button(style=ButtonStyle.blurple, emoji=ApertureEmoji.pag_backward)
    async def _backward(self, _, interaction: Interaction) -> None:
        for child in self.children:
            child.disabled = False
        self._current_index -= 1
        for child in self.children:
            if child.emoji.name in self._what_to_disable():
                child.disabled = True
        self.update_page_no()
        try:
            if isinstance(self._pages[0], str):
                await interaction.message.edit(content=self._pages[self._current_index], view=self)
            elif isinstance(self._pages[0], Embed):
                await interaction.message.edit(embed=self._pages[self._current_index], view=self)
        except suppressed_errors:
            self.stop()

    @button(style=ButtonStyle.blurple, emoji=ApertureEmoji.pag_stop)
    async def _stop(self, _, interaction: Interaction) -> None:
        for child in self.children:
            child.disabled = True
        with suppress(suppressed_errors):
            await interaction.message.edit(view=self)
        self.stop()

    @button(style=ButtonStyle.blurple, emoji=ApertureEmoji.pag_forward)
    async def _forward(self, _, interaction: Interaction) -> None:
        for child in self.children:
            child.disabled = False
        self._current_index += 1
        for child in self.children:
            if child.emoji.name in self._what_to_disable():
                child.disabled = True
        self.update_page_no()
        try:
            if isinstance(self._pages[0], str):
                await interaction.message.edit(content=self._pages[self._current_index], view=self)
            elif isinstance(self._pages[0], Embed):
                await interaction.message.edit(embed=self._pages[self._current_index], view=self)
        except suppressed_errors:
            self.stop()

    @button(style=ButtonStyle.blurple, emoji=ApertureEmoji.pag_toEnd)
    async def _end(self, _, interaction: Interaction) -> None:
        for child in self.children:
            child.disabled = False
        self._current_index = len(self._pages)-1
        for child in self.children:
            if child.emoji.name in self._what_to_disable():
                child.disabled = True
        self.update_page_no()
        try:
            if isinstance(self._pages[0], str):
                await interaction.message.edit(content=self._pages[self._current_index], view=self)
            elif isinstance(self._pages[0], Embed):
                await interaction.message.edit(embed=self._pages[self._current_index], view=self)
        except suppressed_errors:
            self.stop()

    @button(style=ButtonStyle.blurple, emoji=ApertureEmoji.pag_jump_to)
    async def _jump_to(self, _, interaction: Interaction) -> None:
        await interaction.response.send_message("Which page would you like to Jump to?", ephemeral=True)
        _request: Message = await self.ctx.bot.wait_for(
            'message', timeout=30.0,
            check=lambda msg: msg.author.id == interaction.user.id and msg.channel.id == interaction.channel.id and \
                msg.content.isdigit()
        )
        with suppress(HTTPException, NotFound):
            await _request.delete()
        try:
            self._pages[int(_request.content)-1]
        except IndexError:
            return await interaction.followup.send(
                f'Page No. `{_request.content}` does not exist... :confused:', ephemeral=True
            )
        for child in self.children:
            child.disabled = False
        self._current_index = int(_request.content)-1
        for child in self.children:
            if child.emoji.name in self._what_to_disable():
                child.disabled = True
        self.update_page_no()
        try:
            if isinstance(self._pages[0], str):
                await interaction.message.edit(content=self._pages[self._current_index], view=self)
            elif isinstance(self._pages[0], Embed):
                await interaction.message.edit(embed=self._pages[self._current_index], view=self)
        except suppressed_errors:
            self.stop()

    @button(style=ButtonStyle.secondary, emoji=ApertureEmoji.pag_page_no, disabled=True)
    async def _page_no(self, *_) -> None:
        ...

    @button(style=ButtonStyle.danger, label='Delete', emoji=ApertureEmoji.pag_delete)
    async def _delete(self, _, interaction: Interaction) -> None:
        with suppress(suppressed_errors):
            await interaction.message.delete()
            self.stop()

    async def interaction_check(self, interaction: Interaction) -> bool:
        return interaction.user.id == self.ctx.author.id

    async def on_timeout(self) -> None:
        for child in self.children:
            child.disabled = True
        await self._interaction_message.edit(view=self)

    async def on_error(self, error: Exception, item: Item, interaction: Interaction) -> None:
        await view_error_handler(self.ctx, error, item, interaction)

    async def start(self, **kwargs) -> Message:
        for child in self.children:
            if child.emoji.name in self._what_to_disable():
                child.disabled = True

        self.update_page_no()

        kwargs.pop('view', None)
        if isinstance(self._pages[0], str):
            kwargs.pop('content', None)
            _resp = await self.ctx.freply(content=self._pages[0], view=self, **kwargs)
        elif isinstance(self._pages[0], Embed):
            kwargs.pop('embed', None)
            kwargs.pop('embeds', None)
            _resp = await self.ctx.freply(embed=self._pages[0], view=self, **kwargs)

        self._interaction_message = _resp
        return _resp

    def update_page_no(self) -> None:
        for child in self.children:
            if child.emoji.name == ApertureEmoji.pag_page_no:
                child.label = f'Page No. {self._current_index+1}/{len(self._pages)}'

    def _what_to_disable(self) -> List[str]:
        if len(self._pages) == 1:
            disabled = [ApertureEmoji.pag_toStart, ApertureEmoji.pag_backward, ApertureEmoji.pag_forward, ApertureEmoji.pag_toEnd, ApertureEmoji.pag_jump_to]
        elif len(self._pages) == 2:
            disabled = [ApertureEmoji.pag_toStart, ApertureEmoji.pag_toEnd, ApertureEmoji.pag_jump_to]
            if self._current_index == 0:
                disabled.append(ApertureEmoji.pag_backward)
            elif self._current_index == 1:
                disabled.append(ApertureEmoji.pag_forward)
        else:
            if self._current_index == 0:
                disabled = [ApertureEmoji.pag_toStart, ApertureEmoji.pag_backward]
            elif self._current_index == 1:
                disabled = [ApertureEmoji.pag_toStart]
            elif self._current_index == len(self._pages)-1:
                disabled = [ApertureEmoji.pag_toEnd, ApertureEmoji.pag_forward]
            elif self._current_index == len(self._pages)-2:
                disabled = [ApertureEmoji.pag_toEnd]
            else:
                disabled = []

        disabled.append(ApertureEmoji.pag_page_no)

        return disabled
