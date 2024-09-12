from typing import Annotated, Literal, Optional

from discord import ScheduledEvent
from pydantic import Field

from discordbot.models import supabase_models


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
    discord_link: Annotated[str, Field(
        ...,
        description="A link to the discord event"
    )]
    already_notified_24_hours: Annotated[bool, Field(
        False,
        description="Whether the users have already been notified 24 hours before the event"
    )]
    already_notified_1_hours: Annotated[bool, Field(
        False,
        description="Whether the users have already been notified 1 hour before the event"
    )]

    def update(self, event: ScheduledEvent):
        self.name = event.name
        self.description = event.description
        self.entity_type = event.entity_type.name
        self.entity_id = event.entity_id
        self.start_time = int(event.start_time.timestamp())
        self.end_time = int(event.end_time.timestamp()) if event.end_time else None
        self.status = event.status.name
        self.user_count = event.user_count
        self.location = event.location
        self.discord_link = f"https://discord.com/events/{event.guild_id}/{event.id}"

    @staticmethod
    def from_scheduled_event(event: ScheduledEvent) -> "Event":
        return Event(
            id=str(event.id),
            name=event.name,
            description=event.description,
            entity_type=event.entity_type.name,
            entity_id=event.entity_id,
            start_time=int(event.start_time.timestamp()),
            end_time=int(event.end_time.timestamp()) if event.end_time else None,
            status=event.status.name,
            user_count=event.user_count,
            location=event.location,
            discord_link=f"https://discord.com/events/{event.guild_id}/{event.id}",
        )
