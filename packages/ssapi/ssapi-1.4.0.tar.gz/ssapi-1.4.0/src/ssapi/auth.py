import typing as T
from dataclasses import dataclass

from ssapi.relational import Table


@dataclass
class UserSession(Table):
    """A user session"""

    id: T.Optional[int]
    secret: T.Optional[str]
    datetime: T.Optional[str]

    class Meta:
        table_name = "user_sessions"
