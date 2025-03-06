import discord
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

    if content.startswith("-channel "):
        channel = content[len("-channel "):]
        update_pairs(f"{channel}.csv")
        await message.channel.send(f"Set channel to {channel}")

    elif content.startswith("-slm "):
        if channel is None:
            await message.channel.send("Please specify a channel with -channel <channel id>")
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
            await message.channel.send("starting download!")
            save_messages_to_csv(parts[1], parts[2], f"{parts[1]}.csv")
            await message.channel.send(f"Download complete for channel {parts[1]} ({parts[2]} messages)")
        else:
            await message.channel.send("Format: -download <channel id> <number>")
    elif content == '-list':
        output = ""
        files = os.listdir(".")
        files = [os.path.splitext(file)[0] for file in files if file.endswith('.csv')]
        for file in files:
            if output:
                output += f", {file}"
            else:
                output += file
        await message.channel.send(output)

    elif content.startswith("-merge "):
        parts = content.split()
        if len(parts) < 3:
            await message.channel.send("Usage: -merge <file1> <file2>")
        else:
            file1 = parts[1] + ".csv"
            file2 = parts[2] + ".csv"
            try:
                with open(file1, 'r') as f1, open(file2, 'a') as f2:
                    f2.write(f1.read())
                await message.channel.send(f"Merged {file1} into {file2}")
            except FileNotFoundError:
                await message.channel.send("One or both files not found.")

    elif content == "-help":
        await message.channel.send("Hi! I'm SLM bot. I generate messages based off of server channel data.\nCommands:\n-channel <channel id>: set channel from ids that are already downloaded\n-download <channel id> <num messages>: download messages from channel. note tilley must be in this channel.\n-slm <word>: generate a response based on trigger word")
client.run(token)
