from typing import Annotated, Literal, Optional

from pydantic import Field

from src.discordbot.models import supabase_models


class Event(supabase_models.SupabaseModel):
    name: Annotated[str, Field(
        ...,
        description="The name of the event"
    )]
    description: Annotated[str, Field(
        ...,
        description="A description of the event"
    )]
    entity_type: Annotated[Literal["stage_instance", "voice", "external"], Field(
        ...,
        description="The type of entity the event is for"
    )]
    entity_id: Annotated[Optional[int], Field(
        ...,
        description="The id of the entity the event is for (like a channel id), if applicable"
    )]
    start_time: Annotated[int, Field(
        ...,
        description="The unix timestamp of when the event starts"
    )]
    end_time: Annotated[Optional[int], Field(
        ...,
        description="The unix timestamp of when the event ends"
    )]
    status: Annotated[Literal["scheduled", "active", "completed", "cancelled"], Field(
        ...,
        description="The status of the event"
    )]
    user_count: Annotated[int, Field(
        ...,
        description="The number of users that have signed up for the event"
    )]
    location: Annotated[str, Field(
        ...,
        description="The location of the event"
    )]
