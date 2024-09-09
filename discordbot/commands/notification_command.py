from typing import Optional

from discord import app_commands, Interaction
from discord.app_commands import CommandTree, Group

from discordbot.models.user_models import User
from discordbot.store.supabase_manager import SupabaseManager


async def get_or_create_user(user_id: str, manager: SupabaseManager[User]) -> User:
    user = await manager.query(user_id)
    if user is None:
        user = User(
            id=user_id,
            is_ping_hour_before=False,
            is_ping_day_before=False,
        )
    return user


def register(tree: CommandTree, manager: SupabaseManager[User]):
    notifications = Group(
        name="notifications",
        description="Manage your notification settings",
    )

    @notifications.command(
        name="hour_before",
        description="Toggle notifications 1 hour before the event",
    )
    @app_commands.describe(
        on="Whether to enable notifications",
    )
    @app_commands.choices(
        on=[
            app_commands.Choice(name="on", value=1),
            app_commands.Choice(name="off", value=0),
        ]
    )
    async def hour_before(interaction: Interaction, on: Optional[app_commands.Choice[int]] = None):
        await interaction.response.defer(ephemeral=True)

        discord_user_id = str(interaction.user.id)
        user = await get_or_create_user(discord_user_id, manager)

        if on is None:
            user.is_ping_hour_before = not user.is_ping_hour_before
        else:
            user.is_ping_hour_before = on.value == 1
        await manager.upsert(user)

        msg = f"Hour before notifications {'enabled' if user.is_ping_day_before else 'disabled'}"
        await interaction.followup.send(content=msg)

    @notifications.command(
        name="day_before",
        description="Toggle notifications 1 day before the event",
    )
    @app_commands.describe(
        on="Whether to enable notifications",
    )
    @app_commands.choices(
        on=[
            app_commands.Choice(name="on", value=1),
            app_commands.Choice(name="off", value=0),
        ]
    )
    async def day_before(interaction: Interaction, on: Optional[app_commands.Choice[int]] = None):
        await interaction.response.defer(ephemeral=True)

        discord_user_id = str(interaction.user.id)
        user = await get_or_create_user(discord_user_id, manager)
        if on is None:
            user.is_ping_day_before = not user.is_ping_day_before
        else:
            user.is_ping_day_before = on.value == 1
        await manager.upsert(user)

        msg = f"Day before notifications {'enabled' if user.is_ping_day_before else 'disabled'}"
        await interaction.followup.send(content=msg)

    # Add the commands to the tree
    tree.add_command(notifications)
