from typing import TypeVar, Generic, Optional, Type, List

from supabase._async.client import AsyncClient, create_client

from discordbot.models import supabase_models
from discordbot.settings import SETTINGS

T = TypeVar("T", bound=supabase_models.SupabaseModel)


class SupabaseManager(Generic[T]):
    """
    A manager for 1 supabase table
    """

    def __init__(
            self,
            table_name: str,
            model: Type[T],
            api_url: str = SETTINGS.supabase_api_url,
            api_key: str = SETTINGS.supabase_api_key
    ):
        self.table_name = table_name
        self.model = model
        self.api_url = api_url
        self.api_key = api_key

    async def client(self) -> AsyncClient:
        """
        Returns an async client for the Supabase API
        :return: The async client
        """
        return await create_client(
            self.api_url,
            self.api_key,
        )

    async def upsert(self, obj: T) -> T:
        """
        Upserts (overrides the existing data) the object in the database
        :param obj: The object to upsert
        :return: The object that was upserted (changes may have been made by supabase)
        """
        supabase = await self.client()
        upload_data = [obj.model_dump(mode="json")]
        result = await supabase.table(self.table_name).upsert(upload_data).execute()
        return self.model(**result.data[0])

    async def query(self, object_id: str) -> Optional[T]:
        """
        Queries the database for the object with the given ID
        :param object_id: The ID of the object to query
        :return: The object with the given ID, or None if it doesn't exist
        """
        supabase = await self.client()
        result = await supabase.table(self.table_name).select("*").eq("id", object_id).execute()
        if not result.data:
            print(f"Object with id {object_id} not found")
            return None

        return self.model(**result.data[0])

    async def remove(self, object_id: str):
        """
        Removes the object with the given ID from the database
        :param object_id: The ID of the object to remove
        """
        supabase = await self.client()
        await supabase.table(self.table_name).delete().eq("id", object_id).execute()

    async def list(self) -> List[T]:
        """
        Lists all objects in the table
        :return: A list of all objects in the table
        """
        supabase = await self.client()
        result = await supabase.table(self.table_name).select("*").execute()
        return [self.model(**data) for data in result.data]
