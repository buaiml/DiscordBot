from typing import Annotated

from pydantic import Field

from discordbot.models import supabase_models


class User(supabase_models.SupabaseModel):
    is_ping_hour_before: Annotated[bool, Field(
        ...,
        description="Whether to ping the user 1 hour before the event"
    )]
    is_ping_day_before: Annotated[bool, Field(
        ...,
        description="Whether to ping the user 1 hour before the event"
    )]
