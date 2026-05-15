import discord
from discord import app_commands
import datetime
import re
import os

# --- Configuration ---
TOKEN = os.getenv("DISCORD_TOKEN")
WHITELISTED_IDS = [1406599824089808967, 1184504350224154624]
BANNED_WORDS = ["mf", "motherfucker", "nigga", "bosti", "sala", "harami"]
LINK_REGEX = r"discord(?:\.com/invite|/invite|/join|/direct)|\.gg/"

class MyBot(discord.Client):
    def __init__(self):
        super().__init__(intents=discord.Intents.all())
        self.tree = app_commands.CommandTree(self)

    async def setup_hook(self):
        # This registers the commands so they appear in the / menu
        await self.tree.sync()
        print("Slash commands synced!")

bot = MyBot()

# --- Slash Commands ---

@bot.tree.command(name="add", description="Whitelist a user")
async def add(interaction: discord.Interaction, user: discord.Member):
    if interaction.user.id in WHITELISTED_IDS:
        if user.id not in WHITELISTED_IDS:
            WHITELISTED_IDS.append(user.id)
            await interaction.response.send_message(f"✅ {user.display_name} added to whitelist.")
        else:
            await interaction.response.send_message("User is already whitelisted.")
    else:
        await interaction.response.send_message("❌ No permission!", ephemeral=True)

@bot.tree.command(name="remove", description="Remove user from whitelist")
async def remove(interaction: discord.Interaction, user: discord.Member):
    if interaction.user.id in WHITELISTED_IDS:
        if user.id in WHITELISTED_IDS:
            if user.id == 1406599824089808967:
                return await interaction.response.send_message("Cannot remove Owner!")
            WHITELISTED_IDS.remove(user.id)
            await interaction.response.send_message(f"⚠️ {user.display_name} removed.")
        else:
            await interaction.response.send_message("User not whitelisted.")
    else:
        await interaction.response.send_message("❌ No permission!", ephemeral=True)

# --- Auto Mod Logic ---

@bot.event
async def on_message(message):
    if message.author.bot or message.author.id in WHITELISTED_IDS:
        return

    content_lower = message.content.lower()
    if re.search(LINK_REGEX, content_lower) or any(word in content_lower for word in BANNED_WORDS):
        try:
            await message.author.timeout(datetime.timedelta(minutes=5), reason="Gali/Link")
            await message.delete()
            await message.channel.send(f"🚫 {message.author.mention} timed out for 5 mins.", delete_after=10)
        except Exception as e:
            print(f"Error: {e}")

@bot.event
async def on_ready():
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name="for Gali"))
    print(f'Logged in as {bot.user}')

bot.run(TOKEN)
