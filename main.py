import discord
from discord.ext import commands
import datetime
import re
import os

# --- Configuration ---
TOKEN = os.getenv("DISCORD_TOKEN")

# Add the IDs you want the bot to ignore
WHITELISTED_IDS = [1406599824089808967, 1184504350224154624]

# Expanded list of Gali / Slurs
BANNED_WORDS = [
    "mf", "motherfucker", "motherfuckerrr", "nigga", "nigger", 
    "fuck you", "fucker", "ma re", "gali"
]

# Regex for server links (discord.gg, discord.com/invite, etc.)
LINK_REGEX = r"discord(?:\.com/invite|/invite|/join|/direct)|\.gg/"

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name}')

@bot.event
async def on_message(message):
    # 1. Ignore if message is from the bot itself
    if message.author.bot:
        return

    # 2. Ignore if the user is the Owner or Admin (Whitelisted)
    if message.author.id in WHITELISTED_IDS:
        return

    # Convert message to lowercase to catch "MF" or "Mf"
    content_lower = message.content.lower()

    # 3. Check for Links or Banned Words
    contains_link = re.search(LINK_REGEX, content_lower)
    contains_banned_word = any(word in content_lower for word in BANNED_WORDS)

    if contains_link or contains_banned_word:
        try:
            # 5 Minute Timeout
            duration = datetime.timedelta(minutes=5)
            await message.author.timeout(duration, reason="Sent server link or Gali.")
            
            # Delete the offending message
            await message.delete()
            
            # Alert the channel
            await message.channel.send(
                f"🚫 {message.author.mention} has been timed out for 5 minutes for using prohibited language/links.", 
                delete_after=10
            )
        except discord.Forbidden:
            print(f"Failed to timeout {message.author.name}. Check role hierarchy.")
        except Exception as e:
            print(f"Error: {e}")

    await bot.process_commands(message)

bot.run(TOKEN)
