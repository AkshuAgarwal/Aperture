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
from typing import Any

# Base Exception Class
class ApertureError(Exception):
    """Base class for Bot related errors."""
    pass


class CacheError(ApertureError):
    """All the errors raised on Cache handling."""
    pass

class PremiumBlacklisted(CacheError):
    """The user/guild tried to be added in premium list are blacklisted"""

    def __init__(self, id: int, *args: Any) -> None:
        self.id: int = id
        message = f'The user/guild with ID: {id} you\'re trying to add as premium are blacklisted. '\
            'You need to remove them from blacklist first to add them to premium' 
        
        super().__init__(message, *args)
