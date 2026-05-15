import discord
from discord.ext import commands
import datetime
import re
import os

# --- Configuration ---
TOKEN = os.getenv("DISCORD_TOKEN")

# Owner and Admin IDs (Whitelist)
# These people can say anything without being timed out
WHITELISTED_IDS = [1406599824089808967, 1184504350224154624]

# Add EVERY word you want to ban here. 
# It will catch these even if they are inside a sentence.
BANNED_WORDS = [
    "mf", "motherfucker", "nigga", "nigger", "fuck", "fucker", 
    "bosti", "sala", "harami", "khanki", "magi", "bal", "chu"
]

# Regex to catch server invites
LINK_REGEX = r"discord(?:\.com/invite|/invite|/join|/direct)|\.gg/"

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix="/", intents=intents)

@bot.event
async def on_ready():
    # Professional Status
    activity = discord.Activity(type=discord.ActivityType.watching, name="for Gali | /help")
    await bot.change_presence(status=discord.Status.online, activity=activity)
    print(f'Logged in as {bot.user.name}')

# --- Whitelist Commands ---

@bot.command()
async def add(ctx, user: discord.Member):
    """Whitelist a user: /add @user"""
    if ctx.author.id in WHITELISTED_IDS:
        if user.id not in WHITELISTED_IDS:
            WHITELISTED_IDS.append(user.id)
            await ctx.send(f"✅ {user.display_name} is now whitelisted. They can speak freely.")
        else:
            await ctx.send("User is already whitelisted.")
    else:
        await ctx.send("❌ You do not have permission to whitelist users.")

@bot.command()
async def remove(ctx, user: discord.Member):
    """Remove user from whitelist: /remove @user"""
    if ctx.author.id in WHITELISTED_IDS:
        if user.id in WHITELISTED_IDS:
            if user.id == 1406599824089808967:
                return await ctx.send("You cannot remove the Owner!")
            
            WHITELISTED_IDS.remove(user.id)
            await ctx.send(f"⚠️ {user.display_name} removed from whitelist. They are now under monitoring.")
        else:
            await ctx.send("User is not in the whitelist.")
    else:
        await ctx.send("❌ Access Denied.")

# --- Monitoring Logic ---

@bot.event
async def on_message(message):
    # Skip if it's the bot itself
    if message.author.bot:
        return

    # Skip if the user is whitelisted (Owner/Admin/Added users)
    if message.author.id in WHITELISTED_IDS:
        await bot.process_commands(message)
        return

    content_lower = message.content.lower()

    # Check for Links
    contains_link = re.search(LINK_REGEX, content_lower)
    
    # Check for ANY Gali from the list
    # This works for "bosti", "Tui bosti", or "BOSTI"
    contains_banned_word = any(word in content_lower for word in BANNED_WORDS)

    if contains_link or contains_banned_word:
        try:
            # 5 Minute Punishment
            duration = datetime.timedelta(minutes=5)
            await message.author.timeout(duration, reason="Prohibited language or links.")
            
            # Delete the evidence
            await message.delete()
            
            # Public Warning
            await message.channel.send(
                f"🚫 {message.author.mention}, you have been timed out for 5 minutes. No Gali allowed here!", 
                delete_after=10
            )
        except Exception as e:
            print(f"Error handling violation: {e}")

    # Allow the bot to process /add and /remove commands
    await bot.process_commands(message)

bot.run(TOKEN)
