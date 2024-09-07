from pathlib import Path

import discord
from discord import app_commands


class DiscordClient(discord.Client):
    def __init__(self, intents: discord.Intents):
        super().__init__(intents=intents)
        self.tree = app_commands.CommandTree(self)

    async def setup_hook(self) -> None:
        print("Syncing commands")
        try:
            synced = await self.tree.sync()
            print(f"Synced {len(synced)} command(s)")
            for command in synced:
                print(f"  - {command.name}")
        except Exception as e:
            print(f"An error occurred while syncing commands: {e}")


intents = discord.Intents.default()
intents.message_content = True

client = DiscordClient(intents=intents)


@client.tree.command(
    name="embed",
    description="Embeds the wiki and prints info",
)
@app_commands.describe(
    wiki="The wiki to embed",
)
@app_commands.choices(
    wiki=[
        app_commands.Choice(name="wm", value="weaponmechanics"),
        app_commands.Choice(name="mechanics", value="mechanics"),
    ]
)
async def embed(ctx: discord.Interaction, wiki: app_commands.Choice[str]):
    await ctx.response.defer()
    await embed_command.embed_wiki(Path.cwd() / "resources" / "weaponmechanics")
    await ctx.response.edit_message(content=f"Embedding {wiki}")


@client.tree.command(
    name="query",
    description="Queries the wiki",
)
@app_commands.describe(
    query="The query to search",
    top_k="The number of results to return",
)
async def query(ctx: discord.Interaction, query: str, top_k: int = 3):
    await ctx.response.defer()
    results = await embed_command.query_wiki(query, top_k=top_k)
    await ctx.followup.send(content="\n-----\n".join([str(result) for result in results]))


print("Running bot")
client.run(SETTINGS.discord_token)
