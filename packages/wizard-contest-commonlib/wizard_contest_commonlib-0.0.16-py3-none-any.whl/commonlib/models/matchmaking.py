from __future__ import annotations

from pydantic import BaseModel


class LobbyStatus(BaseModel):
    created: bool
    director_id: int | None = None
