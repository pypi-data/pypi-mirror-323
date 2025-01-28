import httpx

from ..models import (
    GenerateActionResponse,
    Message,
    Pair,
    Wizard,
)


class LLMClient:
    def __init__(self, base_url: str):
        self.client = httpx.AsyncClient(base_url=base_url)

    async def calculate_manacost(self, **kwargs) -> int:
        response = await self.client.post(
            '/spell/calculate_manacost',
            json=kwargs
        )
        response.raise_for_status()
        return response.json()

    async def start_contest(self, wizards: Pair[Wizard]) -> list[Message]:
        response = await self.client.post('/contest/start_contest', json=wizards.model_dump())
        response.raise_for_status()
        return response.json()

    async def generate_action(self, **kwargs) -> GenerateActionResponse:
        response = await self.client.post('/contest/generate_action', json=kwargs)
        response.raise_for_status()
        return GenerateActionResponse(**response.json())

    async def determine_turn(self, **kwargs) -> int:
        response = await self.client.post('/contest/determine_turn', json=kwargs)
        response.raise_for_status()
        return response.json()

    async def pick_winner(self, actions: list[Message]) -> str | None:
        response = await self.client.post('/contest/pick_winner', json=actions)
        response.raise_for_status()
        return response.json()

    async def close(self):
        await self.client.aclose()
