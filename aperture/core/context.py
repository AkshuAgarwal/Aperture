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

from contextlib import suppress as sup
from typing import Any, Dict, List, Optional, Sequence, Union, overload

from discord import (
    AllowedMentions,
    Embed,
    File,
    GuildSticker,
    Message,
    MessageReference,
    PartialMessage,
    StickerItem,
)
from discord.ui import View
from discord.ext.commands import Context


class ApertureContext(Context):
    @overload
    async def fsend(
        self,
        content: Optional[str] = ...,
        *,
        tts: bool = ...,
        embed: Embed = ...,
        file: File = ...,
        stickers: Sequence[Union[GuildSticker, StickerItem]] = ...,
        delete_after: float = ...,
        nonce: Union[str, int] = ...,
        allowed_mentions: AllowedMentions = ...,
        reference: Union[Message, MessageReference, PartialMessage] = ...,
        mention_author: bool = ...,
        view: View = ...,
    ) -> Message:
        ...

    @overload
    async def fsend(
        self,
        content: Optional[str] = ...,
        *,
        tts: bool = ...,
        embed: Embed = ...,
        files: List[File] = ...,
        stickers: Sequence[Union[GuildSticker, StickerItem]] = ...,
        delete_after: float = ...,
        nonce: Union[str, int] = ...,
        allowed_mentions: AllowedMentions = ...,
        reference: Union[Message, MessageReference, PartialMessage] = ...,
        mention_author: bool = ...,
        view: View = ...,
    ) -> Message:
        ...

    @overload
    async def fsend(
        self,
        content: Optional[str] = ...,
        *,
        tts: bool = ...,
        embeds: List[Embed] = ...,
        file: File = ...,
        stickers: Sequence[Union[GuildSticker, StickerItem]] = ...,
        delete_after: float = ...,
        nonce: Union[str, int] = ...,
        allowed_mentions: AllowedMentions = ...,
        reference: Union[Message, MessageReference, PartialMessage] = ...,
        mention_author: bool = ...,
        view: View = ...,
    ) -> Message:
        ...

    @overload
    async def fsend(
        self,
        content: Optional[str] = ...,
        *,
        tts: bool = ...,
        embeds: List[Embed] = ...,
        files: List[File] = ...,
        stickers: Sequence[Union[GuildSticker, StickerItem]] = ...,
        delete_after: float = ...,
        nonce: Union[str, int] = ...,
        allowed_mentions: AllowedMentions = ...,
        reference: Union[Message, MessageReference, PartialMessage] = ...,
        mention_author: bool = ...,
        view: View = ...,
    ) -> Message:
        ...

    async def fsend(
        self,
        content=None,
        *,
        tts=None,
        embed=None,
        embeds=[],
        attachments=[],
        file=None,
        files=None,
        stickers=None,
        delete_after=None,
        nonce=None,
        allowed_mentions=None,
        suppress=True,
        reference=None,
        mention_author=None,
        view=None,
    ) -> Message:
        """|coro|
        Sends a message to the destination with the content given.

        The content must be a type that can convert to a string through ``str(content)``.
        If the content is set to ``None`` (the default), then the ``embed`` parameter must
        be provided.

        To upload a single file, the ``file`` parameter should be used with a
        single :class:`~discord.File` object. To upload multiple files, the ``files``
        parameter should be used with a :class:`list` of :class:`~discord.File` objects.
        **Specifying both parameters will lead to an exception**.

        To upload a single embed, the ``embed`` parameter should be used with a
        single :class:`~discord.Embed` object. To upload multiple embeds, the ``embeds``
        parameter should be used with a :class:`list` of :class:`~discord.Embed` objects.
        **Specifying both parameters will lead to an exception**.

        Parameters
        ------------
        content: Optional[:class:`str`]
            The content of the message to send.
        tts: :class:`bool`
            Indicates if the message should be sent using text-to-speech.
        embed: :class:`~discord.Embed`
            The rich embed for the content.
        embeds: List[:class:`~discord.Embed`]
            A list of embeds to upload. Must be a maximum of 10.
        attachments: List[:class:`Attachment`]
            A list of attachments to keep in the message. If ``[]`` is passed
            then all attachments are removed.
        file: :class:`~discord.File`
            The file to upload.
        files: List[:class:`~discord.File`]
            A list of files to upload. Must be a maximum of 10.
        stickers: Sequence[Union[:class:`~discord.GuildSticker`, :class:`~discord.StickerItem`]]
            A list of stickers to upload. Must be a maximum of 3.
        delete_after: :class:`float`
            If provided, the number of seconds to wait in the background
            before deleting the message we just sent. If the deletion fails,
            then it is silently ignored.
        nonce: :class:`int`
            The nonce to use for sending this message. If the message was successfully sent,
            then the message will have a nonce with this value.
        allowed_mentions: :class:`~discord.AllowedMentions`
            Controls the mentions being processed in this message. If this is
            passed, then the object is merged with :attr:`~discord.Client.allowed_mentions`.
            The merging behaviour only overrides attributes that have been explicitly passed
            to the object, otherwise it uses the attributes set in :attr:`~discord.Client.allowed_mentions`.
            If no object is passed at all then the defaults given by :attr:`~discord.Client.allowed_mentions`
            are used instead.
        reference: Union[:class:`~discord.Message`, :class:`~discord.MessageReference`, :class:`~discord.PartialMessage`]
            A reference to the :class:`~discord.Message` to which you are replying, this can be created using
            :meth:`~discord.Message.to_reference` or passed directly as a :class:`~discord.Message`. You can control
            whether this mentions the author of the referenced message using the :attr:`~discord.AllowedMentions.replied_user`
            attribute of ``allowed_mentions`` or by setting ``mention_author``.
        mention_author: Optional[:class:`bool`]
            If set, overrides the :attr:`~discord.AllowedMentions.replied_user` attribute of ``allowed_mentions``.
        view: :class:`discord.ui.View`
            A Discord UI View to add to the message.

        Raises
        --------
        ~discord.HTTPException
            Sending/Editing the message failed.
        ~discord.Forbidden
            You do not have the proper permissions to send the message or
            Tried to suppress a message without permissions or
            edited a message's content or embed that isn't yours.
        ~discord.InvalidArgument
            The ``files`` list is not of the appropriate size,
            you specified both ``file`` and ``files``,
            or you specified both ``embed`` and ``embeds``,
            or the ``reference`` object is not a :class:`~discord.Message`,
            :class:`~discord.MessageReference` or :class:`~discord.PartialMessage`.

        Returns
        ---------
        :class:`~discord.Message`
            The message that was sent.
        """

        try:
            response: Message = self.bot.old_responses[self.message.id]
            with sup(Exception):
                await response.clear_reactions()
            if embed is not None:
                response = await response.edit(
                    content=content,
                    embed=embed,
                    attachments=attachments,
                    suppress=suppress,
                    delete_after=delete_after,
                    allowed_mentions=allowed_mentions,
                    view=view
                )
            else:
                response = await response.edit(
                    content=content,
                    embeds=embeds,
                    attachments=attachments,
                    suppress=suppress,
                    delete_after=delete_after,
                    allowed_mentions=allowed_mentions,
                    view=view
                )
            return response
        except KeyError:
            if embed is not None and file is not None:
                response = await super().send(
                    content=content,
                    tts=tts,
                    embed=embed,
                    file=file,
                    stickers=stickers,
                    delete_after=delete_after,
                    nonce=nonce,
                    allowed_mentions=allowed_mentions,
                    reference=reference,
                    mention_author=mention_author,
                    view=view
                )
            elif embed is None and file is not None:
                response = await super().send(
                    content=content,
                    tts=tts,
                    embeds=embeds,
                    file=file,
                    stickers=stickers,
                    delete_after=delete_after,
                    nonce=nonce,
                    allowed_mentions=allowed_mentions,
                    reference=reference,
                    mention_author=mention_author,
                    view=view
                )
            elif embed is not None and file is None:
                response = await super().send(
                    content=content,
                    tts=tts,
                    embed=embed,
                    files=files,
                    stickers=stickers,
                    delete_after=delete_after,
                    nonce=nonce,
                    allowed_mentions=allowed_mentions,
                    reference=reference,
                    mention_author=mention_author,
                    view=view
                )
            else:
                response = await super().send(
                    content=content,
                    tts=tts,
                    embeds=embeds,
                    files=files,
                    stickers=stickers,
                    delete_after=delete_after,
                    nonce=nonce,
                    allowed_mentions=allowed_mentions,
                    reference=reference,
                    mention_author=mention_author,
                    view=view
                )
            self.bot.old_responses[self.message.id] = response
            return response

    async def freply(self, content: Optional[str] = None, **kwargs: Dict[str, Any]) -> Message:
        """|coro|
        A shortcut method to :meth:`discord.abc.Messageable.fsend` to reply to the
        :class:`discord.Message`.

        Raises
        --------
        ~discord.HTTPException
            Sending the message failed.
        ~discord.Forbidden
            You do not have the proper permissions to send the message.
        ~discord.InvalidArgument
            The ``files`` list is not of the appropriate size or
            you specified both ``file`` and ``files``.

        Returns
        ---------
        :class:`discord.Message`
            The message that was sent.
        """
        if not kwargs.get('mention_author', None):
            kwargs['mention_author'] = False

        return await self.fsend(content, reference=self.message, **kwargs)

    async def reply(self, content: Optional[str] = None, **kwargs: Dict[str, Any]):
        """|coro|
        A shortcut method to :meth:`.abc.Messageable.send` to reply to the
        :class:`.Message`.
        .. versionadded:: 1.6
        Raises
        --------
        ~discord.HTTPException
            Sending the message failed.
        ~discord.Forbidden
            You do not have the proper permissions to send the message.
        ~discord.InvalidArgument
            The ``files`` list is not of the appropriate size or
            you specified both ``file`` and ``files``.
        Returns
        ---------
        :class:`.Message`
            The message that was sent.
        """

        if not kwargs.get('mention_author', None):
            kwargs['mention_author'] = False

        return await super().reply(content=content, **kwargs)
