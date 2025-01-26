import httpx

from ..models import (
    ActionGenerationResponse,
    Message,
    Pair,
    SpellBase,
    SpellType,
    Wizard,
)


class LLMClient:
    def __init__(self, base_url: str):
        self.client = httpx.AsyncClient(base_url=base_url)

    async def close(self):
        await self.client.aclose()

    async def calculate_manacost(self, spell_type: SpellType, description: str) -> int:
        response = await self.client.post(
            "/spell/calculate_manacost",
            json={"type_": spell_type, "description": description},
        )
        response.raise_for_status()
        return response.json()

    async def start_contest(self, wizards: Pair[Wizard]) -> list[Message]:
        response = await self.client.post(
            "/contest/start_contest",
            json=wizards.model_dump()
        )
        response.raise_for_status()
        return response.json()

    async def generate_action(
            self, messages: list[Message], wizard: Wizard, spell: SpellBase
    ) -> ActionGenerationResponse:
        response = await self.client.post(
            "/contest/generate_action",
            json={
                "messages": messages,
                "wizard": wizard.model_dump(),
                "spell": spell.model_dump(),
            },
        )
        response.raise_for_status()
        return ActionGenerationResponse(**response.json())

    async def determine_turn(self, actions_history: list[str], wizards: Pair[Wizard]) -> int:
        response = await self.client.post(
            "/contest/determine_turn",
            json={"actions_history": actions_history, "wizards": wizards.model_dump()},
        )
        response.raise_for_status()
        return response.json()

    async def pick_winner(self, actions_history: list[str]) -> str | None:
        response = await self.client.post(
            "/contest/pick_winner",
            json=actions_history,
        )
        response.raise_for_status()
        result = response.json()
        return result if result else None
