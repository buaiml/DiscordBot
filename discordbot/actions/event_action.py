from discordbot.actions.timed_action import TimedAction
from discordbot.main import DiscordClient
from discordbot.models.event_models import Event
from discordbot.settings import SETTINGS


class EventAction(TimedAction):
    """
    Although we try to listen for guild events, we can't listen for all of them.
    This action will loop
    """

    def __init__(self, main: DiscordClient):
        super().__init__(main, interval=60 * 60)  # 1 hour

    async def action(self):
        print("Updating events")
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

        for event in scheduled_events:
            if event.id not in [e.id for e in supabase_events]:
                print(f"Found new event '{event.name}' to add")

            event_data = Event.from_scheduled_event(event)
            await self.main.supabase_managers[Event].upsert(event_data)
