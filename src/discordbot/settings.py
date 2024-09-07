from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Discord bot token
    discord_token: str
    discord_guild_id: int

    # Storing embeddings and events
    pinecone_api_key: str
    supabase_api_url: str
    supabase_api_key: str

    class Config:
        """
        Used by the BaseSettings superclass as config options
        """
        env_file = ".env"
        case_sensitive = False


SETTINGS = Settings()
