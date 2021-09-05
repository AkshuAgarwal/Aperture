from typing import Callable, List, Optional, Tuple, TypedDict, Union

from discord.ext.commands import CooldownMapping, MaxConcurrency
from .context import ApertureContext

class CacheCommandUsagePayload(TypedDict):
    name: str
    type: int
    user_id: int
    guild_id: Optional[int]

class CommandKwargsPayload(TypedDict, total=False):
    aliases: Union[List[str], Tuple[str]]
    brief: str
    checks: List[Callable[[ApertureContext], bool]]
    cooldown: CooldownMapping
    description: str
    enabled: bool
    help: str
    hidden: bool
    ignore_extra: bool
    max_concurrency: MaxConcurrency
    name: str
    require_var_positional: bool
    rest_is_raw: bool
    usage: str
