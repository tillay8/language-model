import discord
import os
import logging
from model import *
from downloader import save_messages_to_csv

token_path = "~/bot_tokens/SLM.token"
intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)

try:
    with open(os.path.expanduser(token_path), "r") as f:
        token = f.readline().strip()
except Exception as e:
    logging.error(f"Error loading bot token: {e}")
    exit(1)

channel = None

@client.event
async def on_ready():
    logging.info(f"Logged in as {client.user}")
    load_model()

@client.event
async def on_message(message):
    global channel

    if message.author == client.user:
        return

    content = message.content.strip()

    if content.startswith("-setchannel "):
        channel = content[len("-setchannel "):]
        update_pairs(f"{channel}.csv")
        await message.channel.send(f"Set channel to {channel}")

    elif content.startswith("-slm "):
        if channel is None:
            await message.channel.send("Please specify a channel with -setchannel <channel id>")
            return

        input_content = content[len("-slm "):]
        if os.path.exists(f"./{channel}.csv"):
            result = generate_sentence(input_content, f"{channel}.csv")
            await message.channel.send(f"{result}" if result else "No prediction available.")
        else:
            await message.channel.send("No data available for the specified channel.")

    elif content.startswith("-download "):
        parts = content.split()
        if len(parts) == 3:
            save_messages_to_csv(parts[1], parts[2], f"{parts[1]}.csv")
            await message.channel.send(f"Download complete for channel {parts[1]} ({parts[2]} messages)")
        else:
            await message.channel.send("Format: -download <channel id> <number>")

client.run(token)
