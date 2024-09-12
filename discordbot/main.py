import asyncio

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
        #member.send(content=content, embed=embed)
        pass

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
