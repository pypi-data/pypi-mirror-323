from __future__ import annotations

from pydantic import BaseModel

from .database import Spell, Wizard


class ContestAction(BaseModel):
    action: str
    metadata: ActionMetadata
    result: ContestResult | None


class ActionMetadata(BaseModel):
    caster_wizard: Wizard
    spell: Spell


class ContestResult(BaseModel):
    tie: bool = False
    winner: Wizard | None = None
