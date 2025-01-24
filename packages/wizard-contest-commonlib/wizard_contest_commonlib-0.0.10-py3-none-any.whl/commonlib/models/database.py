from __future__ import annotations

from enum import Enum

from pydantic import BaseModel, ConfigDict


class DatabaseModel(BaseModel):
    model_config = ConfigDict(
        from_attributes=True,
        extra='ignore',
    )


class SpellType(str, Enum):
    ACTIVE = 'ACTIVE'
    PASSIVE = 'PASSIVE'


class SpellBase(DatabaseModel):

    type_: SpellType
    name: str
    description: str
    manacost: int


class Spell(SpellBase):
    id: int


class WizardBase(DatabaseModel):
    name: str
    speed: int
    power: int


class Wizard(WizardBase):
    id: int
    spells: list[Spell]

    @property
    def rank(self) -> int:
        return self._manapool * self.speed * self.power

    @property
    def _manapool(self) -> int:
        return sum(spell.manacost for spell in self.spells)

    @property
    def description(self) -> str:
        return (
            f'Wizard\'s name is {self.name}\n'
            f'They have following spells:\n\n'
        ) + '\n\n'.join(
            f'Spell name: {spell.name}\n'
            f'Type: {str(spell.type_).lower()}\n'
            f'Description: {spell.description}\n'
            for spell in self.spells
        )


    def get_spell(self, id_: int) -> Spell:
        for spell in self.spells:
            if spell.id == id_:
                return spell
        assert False, f'No spell with such id: {id_}'


class User(DatabaseModel):
    id: int
    wizards: list[Wizard]


class SpellCreate(SpellBase):
    wizard_id: int


class WizardCreate(WizardBase):
    user_id: int


class UserCreate(DatabaseModel):
    id: int
