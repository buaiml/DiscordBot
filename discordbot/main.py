import asyncio
import time

import discord
from discord import app_commands

from discordbot.commands import notification_command
from discordbot.models.event_models import Event
from discordbot.models.user_models import User
from discordbot.settings import SETTINGS
from discordbot.store.supabase_manager import SupabaseManager
from discordbot.util.registers import SupabaseRegister


class DiscordClient(discord.Client):
    def __init__(self, intents: discord.Intents):
        super().__init__(intents=intents, member_cache_flags=discord.MemberCacheFlags.all())
        self.tree = app_commands.CommandTree(self)

        # Managers handle uploading/downloading supabase data
        self.supabase_managers = SupabaseRegister()
        self.supabase_managers[Event] = SupabaseManager("events", Event)
        self.supabase_managers[User] = SupabaseManager("users", User)

        # User commands
        notification_command.register(self.tree, self.supabase_managers[User])

    async def on_ready(self):
        # Avoid circular imports
        from discordbot.actions.event_action import EventAction

        timers = [
            EventAction(self)
        ]
        for timer in timers:
            asyncio.create_task(timer.start())

    async def setup_hook(self):
        print("Syncing commands")
        try:
            synced = await self.tree.sync()
            print(f"Synced {len(synced)} command(s)")
            for command in synced:
                print(f"  - {command.name}")
        except Exception as e:
            print(f"An error occurred while syncing commands: {e}")

    async def on_member_join(self, member: discord.Member):
        # Waiting 10 seconds, so we don't ping right away.
        await asyncio.sleep(10)

        content = (f"Welcome {member.mention} to **AI Society**! We're happy to have you here.\n\n"
                   f"We have a little notification system to help keep you up to date with events. "
                   f"If you run the command `/notifications`, you can choose to be notified about events "
                   f"24 hours, and 1 hour before they start (We recommend turning on both).")

        next_event = None
        events = await self.supabase_managers[Event].list()
        for event in events:
            if event.start_time > time.time() and event.status == "scheduled":
                next_event = event
                break

        if next_event:
            content += (f"\n\nIt looks like we have an [event coming up]({next_event.discord_link}). "
                        f"Make sure to check it out! Use <#1228852708677783572> if you would like to "
                        f"ask any questions or get help.")
        else:
            content += "\n\nWe don't have any events coming up right now, but stay tuned!"

        await member.send(content=content)

    async def on_scheduled_event_create(self, scheduled_event: discord.ScheduledEvent):
        print(f"Sending event '{scheduled_event.name}' to supabase")
        await self.update_and_upsert_event(scheduled_event)

    async def on_scheduled_event_update(self, before: discord.ScheduledEvent, after: discord.ScheduledEvent):
        print(f"Updating event '{before.name}' in supabase")
        await self.update_and_upsert_event(after)

    async def on_scheduled_event_remove(self, scheduled_event: discord.ScheduledEvent):
        print(f"Removing event '{scheduled_event.name}' from supabase")
        await self.supabase_managers[Event].remove(str(scheduled_event.id))

    async def update_and_upsert_event(self, event: discord.ScheduledEvent):
        previous_event = await self.supabase_managers[Event].query(str(event.id))
        if previous_event:
            previous_event.update(event)
            await self.supabase_managers[Event].upsert(previous_event)
        else:
            converted_event = Event.from_scheduled_event(event)
            await self.supabase_managers[Event].upsert(converted_event)


def main():
    intents = discord.Intents.default()
    intents.members = True  # Reads member list
    intents.message_content = True  # Reads message content
    intents.guild_scheduled_events = True  # See scheduled events

    client = DiscordClient(intents=intents)

    print("Running bot")
    client.run(SETTINGS.discord_token)
    print("All done")


if __name__ == "__main__":
    main()
