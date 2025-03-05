import discord
from model import *

# Instance Variables
token_path = "~/bot_tokens/SLM.token"

# Discord Bot Setup
intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)

# Load token securely
try:
    with open(os.path.expanduser(token_path), "r") as f:
        token = f.readline().strip()
except Exception as e:
    logging.error(f"Error loading bot token: {e}")
    exit(1)

@client.event
async def on_ready():
    logging.info(f"Logged in as {client.user}")
    load_model()
    update_pairs()

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    content = message.content.strip()

    if content.startswith("-slm "):
        input_content = content[len("-slm "):]
        result = generate_sentence(input_content)
        await message.channel.send(f"{result}" if result else "No prediction available.")
    else:
        pass #update_model(content)

client.run(token)
