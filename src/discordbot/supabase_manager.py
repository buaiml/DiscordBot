from typing import TypeVar, Generic, Optional, Type

from supabase._async.client import AsyncClient, create_client

from src.discordbot.models import supabase_models


T = TypeVar("T", bound=supabase_models.SupabaseModel)


class SupabaseManager(Generic[T]):
    """
    A manager for 1 supabase table
    """

    def __init__(self, api_url: str, api_key: str, table_name: str, model: Type[T]):
        self.api_url = api_url
        self.api_key = api_key
        self.table_name = table_name
        self.model = model

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
