import httpx

from ..models import ContestAction, Wizard


class ContestClient:
    def __init__(self, base_url: str):
        self.client = httpx.AsyncClient(base_url=base_url)

    async def close(self):
        await self.client.aclose()

    async def create_director(self) -> int:
        response = await self.client.post("/create_director")
        response.raise_for_status()
        return response.json()

    async def set_wizard(self, director_id: int, user_id: int, wizard: Wizard) -> None:
        response = await self.client.post(
            "/set_wizard",
            params={"director_id": director_id, "user_id": user_id},
            json=wizard.model_dump(),
        )
        response.raise_for_status()

    async def get_user_to_make_turn(self, director_id: int) -> int:
        response = await self.client.post(
            "/get_user_to_make_turn", params={"director_id": director_id}
        )
        response.raise_for_status()
        return response.json()

    async def get_available_spells(self, director_id: int, user_id: int) -> list[int]:
        response = await self.client.post(
            "/get_available_spells",
            params={"director_id": director_id, "user_id": user_id},
        )
        response.raise_for_status()
        return response.json()

    async def cast_spell(
            self, director_id: int, user_id: int, spell_id: int
    ) -> None:
        response = await self.client.post(
            "/cast_spell",
            params={
                "director_id": director_id,
                "user_id": user_id,
                "spell_id": spell_id,
            },
        )
        response.raise_for_status()

    async def get_action(self, director_id: int) -> ContestAction:
        response = await self.client.post(
            "/get_action", params={"director_id": director_id}
        )
        response.raise_for_status()
        return ContestAction(**response.json())