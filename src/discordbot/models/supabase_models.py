import time
import uuid
from abc import ABC, abstractmethod
from typing import Annotated

from pydantic import BaseModel, Field

from src.discordbot.models.discord_models import DiscordUser


def get_current_timestamp():
    """
    Get the current unix (seconds since epoch) timestamp
    :return: The current unix timestamp
    """
    return int(time.time())


class SupabaseModel(ABC, BaseModel):
    """
    A base model for all models we store in Supabase. All the data we upload has this same structure
    """

    admin: Annotated[DiscordUser, Field(
        ...,
        description="The user that created this item of data"
    )]
    id: Annotated[str, Field(
        default_factory=lambda: uuid.uuid4(),
        description="The unique identifier for this item of data"
    )]
    created_at: Annotated[int, Field(
        default_factory=get_current_timestamp,
        description="The unix timestamp of when this item of data was created, used internally for sorting"
    )]
