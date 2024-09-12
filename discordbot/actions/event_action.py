import time
from typing import List, Literal

import discord
from discord import ScheduledEvent

from discordbot.actions.timed_action import TimedAction
from discordbot.models.event_models import Event
from discordbot.models.user_models import User
from discordbot.settings import SETTINGS
from main import DiscordClient


class EventAction(TimedAction):
    """
    Although we try to listen for guild events, we can't listen for all of them.
    This action will loop
    """

    def __init__(self, main: DiscordClient):
        super().__init__(main, interval=60 * 5)  # 5 minutes

    async def action(self):
        guild = self.main.get_guild(SETTINGS.discord_guild_id)
        if guild is None:
            print("Guild not found... Could not update the events")
            return

        # Update any events that have changed
        scheduled_events = await guild.fetch_scheduled_events()
        print(f"Found {scheduled_events} scheduled events")
        supabase_events = await self.main.supabase_managers[Event].list()
        print(f"Found {len(supabase_events)} supabase events")

        if not scheduled_events:
            print("No scheduled events found")
            return

        # Upload any missing events and updating any existing events
        for event in scheduled_events:
            supabase_event = next(
                (e for e in supabase_events if e.id == str(event.id)),
                None
            )
            if supabase_event is None:
                supabase_event = Event.from_scheduled_event(event)
            else:
                supabase_event.update(event)

            await self.main.supabase_managers[Event].upsert(supabase_event)

        # Update our old events list... Redundant(?)
        supabase_events = await self.main.supabase_managers[Event].list()
        print(f"Checking again... Now have {len(supabase_events)} supabase events")
        users = await self.main.supabase_managers[User].list()

        # If we are within 24 hours of the event, notify the users
        for event in supabase_events:
            start_time = event.start_time
            current_time = time.time()

            scheduled_event: ScheduledEvent = next(
                (e for e in scheduled_events if str(e.id) == event.id),
                None
            )

            if not scheduled_event:
                print(f"Could not find scheduled event with ID {event.id}... "
                      f"Is this event left over? Might need to clear table.")
                continue

            # If we are within 24 hours of the event, notify the users
            if not event.already_notified_24_hours and start_time - current_time <= 24 * 60 * 60:
                event.already_notified_24_hours = True
                await self.main.supabase_managers[Event].upsert(event)
                await self.notify_users(guild, users, event, "is_ping_day_before")

            # If we are within 1 hour of the event, notify the users
            if not event.already_notified_1_hours and start_time - current_time <= 60 * 60:
                event.already_notified_1_hours = True
                await self.main.supabase_managers[Event].upsert(event)
                await self.notify_users(guild, users, event, "is_ping_hour_before")

            # Make sure we start the event, for the traditional event notifications
            if start_time < current_time and event.status == "scheduled":
                await scheduled_event.start()

    async def notify_users(
            self,
            guild: discord.Guild,
            users: List[User],
            event: Event,
            time_attribute: Literal["is_ping_hour_before", "is_ping_day_before"]
    ):
        """
        Sends a message to the users if they have the given time attribute set to True
        """
        content = (f"We have an [event]({event.discord_link}) coming up! Make sure to check it out!"
                   f"\n-# You can disable these notifications by using `/notifications`")

        print(f"Sending notification to {len(users)} users for event '{event.name}'")
        for user in users:
            if not getattr(user, time_attribute):
                continue

            member = guild.get_member(int(user.id))
            if member is None:
                print(f"User with ID {user.id} not found in guild")
                continue

            await member.send(content=content)
