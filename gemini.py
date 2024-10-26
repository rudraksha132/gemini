import discord
from discord.ext import commands
import google.generativeai as genai
import logging
import time
from PIL import Image
import os

# Setup logging
logging.basicConfig(level=logging.INFO)

# Initialize the bot
cmd_prefix = "G!"
intents = discord.Intents.all()
bot = commands.Bot(command_prefix=cmd_prefix, intents=intents)

# Configure your API keys
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
TOKEN = os.getenv("TOKEN")

genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-1.5-pro')

activated_guilds = {}
guild_prefix = {}

async def getprefix(bot, message):
    guild_id = message.guild.id if message.guild else None
    if guild_id in guild_prefix:
        return guild_prefix[guild_id]
    else:
        return cmd_prefix

bot.command_prefix = getprefix

# Event listener for when the bot is ready
@bot.event
async def on_ready():
    logging.info(f'{bot.user} has connected to Discord!')
    await bot.change_presence(activity=discord.Game(name="something cool!"))
    await bot.tree.sync()

# Slash command to test the bot's latency
@bot.tree.command(name="ping", description="Check the bot's latency")
async def ping(interaction: discord.Interaction):
    start_time = time.time()
    await interaction.response.defer()
    end_time = time.time()
    latency = (end_time - start_time) * 1000
    await interaction.followup.send(f"Pong! My latency is {latency:.2f}ms")

@bot.tree.command(name="activate", description="Activate a channel for the bot")
@commands.has_permissions(manage_guild=True)
async def activate(interaction: discord.Interaction):
    guild_id = interaction.guild_id
    channel_id = interaction.channel_id
    if guild_id not in activated_guilds:
        activated_guilds[guild_id] = [channel_id]  # Create a new list with the channel ID
    elif channel_id not in activated_guilds[guild_id]:
        activated_guilds[guild_id].append(channel_id)  # Add the channel ID to the existing list
    await interaction.response.send_message(f"Channel <#{interaction.channel.id}> activated!")

@bot.tree.command(name="deactivate", description="Deactivate a channel for the bot")
@commands.has_permissions(manage_guild=True)
async def deactivate(interaction: discord.Interaction):
    guild_id = interaction.guild_id
    channel_id = interaction.channel_id
    if guild_id in activated_guilds and channel_id in activated_guilds[guild_id]:
        activated_guilds[guild_id].remove(channel_id)  # Remove the channel ID from the list
        if not activated_guilds[guild_id]:  # If the list is empty, remove the guild ID from the dictionary
            del activated_guilds[guild_id]
        await interaction.response.send_message(f"Channel <#{interaction.channel.id}> deactivated!")
    else:
        await interaction.response.send_message(f"Channel <#{interaction.channel.id}> is not activated!")


@bot.tree.command(name = "listactivated", description = "List all activated channels")
async def listactivated(interaction: discord.Interaction):
    guild_id = interaction.guild_id
    if guild_id in activated_guilds:
        channels = activated_guilds[guild_id]
        if channels:
            channel_list = [f"<#{channel_id}>" for channel_id in channels]
            await interaction.response.send_message(f"Activated channels in this server: {', '.join(channel_list)}")
        else:
            await interaction.response.send_message("There are no activated channels in this server.")
    else:
        await interaction.response.send_message("This server has no activated channels.")


@bot.tree.command(name="setpresence")
async def setpresence(interaction: discord.Interaction, *, activity_type: str, activity_name: str):
    if interaction.user.id == 1144963059954237500:
        if activity_type.lower() == "play":
            await bot.change_presence(activity=discord.Game(name=activity_name))
            await interaction.response.send_message(f"Bot's activity set to **playing {activity_name}**", ephemeral=True)
        elif activity_type.lower() == "stream":
            await bot.change_presence(activity=discord.Streaming(name=activity_name, url="https://twitch.tv/your_twitch_channel"))
            await interaction.response.send_message(f"Bot's activity set to **streaming {activity_name}**", ephemeral=True)
        elif activity_type.lower() == "listen":
            await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.listening, name=activity_name))
            await interaction.response.send_message(f"Bot's activity set to **listening to {activity_name}**", ephemeral=True)
        elif activity_type.lower() == "watch":
            await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name=activity_name))
            await interaction.response.send_message(f"Bot's activity set to **watching {activity_name}**", ephemeral=True)
        else:
            await interaction.response.send_message("Invalid activity type. Choose from: playing, streaming, listening, watching.", ephemeral=True)
    else:
        await interaction.response.send_message("You do not have permission to use this command.", ephemeral=False)
        

@bot.command()
async def setpresence(ctx, *args):
    if ctx.author.id == 1144963059954237500:  # Replace with your user ID
        if not args:
            embed = discord.Embed(
                title="Set Presence Command Help",
                description="Use this command to change the bot's activity status.",
                color=discord.Color(value=0x87CEFA)  # Set color to #87CEFA
            )
            embed.add_field(name="Usage:", value=f"`{cmd_prefix}setpresence [activity_type] [activity_name]`", inline=False)
            embed.add_field(name="Example:", value=f"`{cmd_prefix}setpresence play \"My favorite game\"`", inline=False)
            embed.add_field(name="Valid Activity Types:", value="* play\n* stream\n* listen\n* watch", inline=False)
            embed.set_thumbnail(url="https://d1muf25xaso8hp.cloudfront.net/https%3A%2F%2Fmeta-q.cdn.bubble.io%2Ff1707847080246x798414315632580500%2FGoogle-Gemini-AI-Icon.png?w=64&h=64&auto=compress&dpr=1.75&fit=max")
            embed.set_author(name=f"{ctx.author.name}", icon_url=ctx.author.avatar.url)
            await ctx.send(embed=embed)
            
        activity_type = args[0].lower()
        activity_name = " ".join(args[1:])

        if activity_type in ["play", "stream", "listen", "watch"]:
            if activity_type == "play":
                await bot.change_presence(activity=discord.Game(name=activity_name))
                embed = discord.Embed(
                    title="Activity Updated",
                    description=f"Bot's activity set to **Playing {activity_name}**",
                color=discord.Color(value=0x87CEFA)  # Set color to #87CEFA
            )
                embed.set_thumbnail(url="https://d1muf25xaso8hp.cloudfront.net/https%3A%2F%2Fmeta-q.cdn.bubble.io%2Ff1707847080246x798414315632580500%2FGoogle-Gemini-AI-Icon.png?w=64&h=64&auto=compress&dpr=1.75&fit=max")
                embed.set_author(name=f"{ctx.author.name}", icon_url=ctx.author.avatar.url)
                await ctx.send(embed=embed)
            elif activity_type == "stream":
                await bot.change_presence(activity=discord.Streaming(name=activity_name, url=f"https://twitch.tv/{activity_name}"))
                embed = discord.Embed(
                    title="Activity Updated",
                    description=f"Bot's activity set to **Streaming {activity_name}**",
                    color=discord.Color(value=0x87CEFA)  # Set color to #87CEFA
            )
                embed.set_thumbnail(url="https://d1muf25xaso8hp.cloudfront.net/https%3A%2F%2Fmeta-q.cdn.bubble.io%2Ff1707847080246x798414315632580500%2FGoogle-Gemini-AI-Icon.png?w=64&h=64&auto=compress&dpr=1.75&fit=max")
                embed.set_author(name=f"{ctx.author.name}", icon_url=ctx.author.avatar.url)
                await ctx.send(embed=embed)
            elif activity_type == "listen":  # Added functionality for listen
                await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.listening, name=activity_name))
                embed = discord.Embed(
                    title="Activity Updated",
                    description=f"Bot's activity set to **Listening to {activity_name}**",
                    color=discord.Color(value=0x87CEFA)  # Set color to #87CEFA
            )
                embed.set_thumbnail(url="https://d1muf25xaso8hp.cloudfront.net/https%3A%2F%2Fmeta-q.cdn.bubble.io%2Ff1707847080246x798414315632580500%2FGoogle-Gemini-AI-Icon.png?w=64&h=64&auto=compress&dpr=1.75&fit=max")
                embed.set_author(name=f"{ctx.author.name}", icon_url=ctx.author.avatar.url)
                await ctx.send(embed=embed)
            elif activity_type == "watch":  # Added functionality for watch
                await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name=activity_name))
                embed = discord.Embed(
                    title="Activity Updated",
                    description=f"Bot's activity set to **Watching {activity_name}**",
                    color=discord.Color(value=0x87CEFA)  # Set color to #87CEFA
            )
                embed.set_thumbnail(url="https://d1muf25xaso8hp.cloudfront.net/https%3A%2F%2Fmeta-q.cdn.bubble.io%2Ff1707847080246x798414315632580500%2FGoogle-Gemini-AI-Icon.png?w=64&h=64&auto=compress&dpr=1.75&fit=max")
                embed.set_author(name=f"{ctx.author.name}", icon_url=ctx.author.avatar.url)
                await ctx.send(embed=embed)
        else:
            embed = discord.Embed(
                title="Invalid Activity Type",
                description="Choose from: play, stream, listen, watch.",
                color=discord.Color(value=0x87CEFA)  # Set color to #87CEFA
            )
            embed.set_thumbnail(url="https://d1muf25xaso8hp.cloudfront.net/https%3A%2F%2Fmeta-q.cdn.bubble.io%2Ff1707847080246x798414315632580500%2FGoogle-Gemini-AI-Icon.png?w=64&h=64&auto=compress&dpr=1.75&fit=max")
            embed.set_author(name=f"{ctx.author.name}", icon_url=ctx.author.avatar.url)
            await ctx.send(embed=embed)
    else:
        embed = discord.Embed(
            title="Permission Denied",
            description="Only the bot owner can use this command.",
            color=discord.Color(value=0x87CEFA)
        )
        embed.set_thumbnail(url="https://d1muf25xaso8hp.cloudfront.net/https%3A%2F%2Fmeta-q.cdn.bubble.io%2Ff1707847080246x798414315632580500%2FGoogle-Gemini-AI-Icon.png?w=64&h=64&auto=compress&dpr=1.75&fit=max")
        embed.set_author(name=f"{ctx.author.name}", icon_url=ctx.author.avatar.url)
        await ctx.send(embed=embed)



@bot.tree.command(name="setprefix", description="Change the bot's prefix for this server")
@commands.has_permissions(manage_guild=True)
async def setprefix(interaction: discord.Interaction, new_prefix: str):
    guild_id = interaction.guild.id
    guild_prefix[guild_id] = new_prefix
    await interaction.response.send_message(f"Prefix `{new_prefix}` added for this server.")

@setprefix.error
async def set_prefix_error(interaction: discord.Interaction, error):
    if isinstance(error, commands.MissingPermissions):
        await interaction.response.send_message("You do not have permission to change the prefix.")
    else:
        raise error

@bot.command(name="prefix", description="List all active prefixes")
async def list_prefixes(ctx, *args):
    try:
        if not args:
            guild_id = ctx.guild.id
            if guild_id in guild_prefix:
                prefix = guild_prefix[guild_id]
                await ctx.send(f"`{prefix}` is the current server prefix.")
            else:
                await ctx.send(f"`{cmd_prefix}` is the current server prefix.")
        elif args:
            new_prefix = args[0]
            guild_id = ctx.guild.id
            guild_prefix[guild_id] = new_prefix
            await ctx.send(f"The prefix is changed to `{new_prefix}` for this server.")
    except Exception as e:
        await ctx.send(f"An error occurred: {e}")


# Event listener for messages
@bot.event
async def on_message(message):
    await bot.process_commands(message)
    if message.author == bot.user or message.author.bot:
        return

    guild_id = message.guild.id if message.guild else None
    channel_id = message.channel.id if message.guild else None

    if message.guild is None:
        # Direct message, respond to the message
        if message.clean_content:
            try:
                async with message.channel.typing():
                    result = model.generate_content(message.clean_content)
                    text = result.text
                    if len(text) > 2000:
                        chunks = [text[i:i + 2000] for i in range(0, len(text), 2000)]
                        for chunk in chunks:
                            await message.channel.send(chunk)
                    else:
                        await message.channel.send(text)
            except Exception as e:
                logging.error(f"Error generating content: {e}")
                await message.channel.send(f'Something went wrong! Try again later. {e}')
            if message.attachments:
                await handle_attachment(message.attachments[0], message)
        else:
            await message.channel.send('You sent an empty message!')
            if message.attachments:
                await handle_attachment(message.attachments[0], message)
    elif guild_id in activated_guilds and channel_id in activated_guilds[guild_id]:
        # Channel is activated, respond to the message
        if message:
            try:
                async with message.channel.typing():
                    logging.info(f"Got a message from {message.author} in {message.channel.name} in {message.guild.name}: '{message.clean_content}'")
                    result = model.generate_content(message.content)
                    text = result.text
                    if len(text) > 2000:
                        chunks = [text[i:i + 2000] for i in range(0, len(text), 2000)]
                        for chunk in chunks:
                            await message.channel.send(chunk, allowed_mentions=discord.AllowedMentions.none())
                    else:
                        await message.reply(text, allowed_mentions=discord.AllowedMentions.none())
            except Exception as e:
                logging.error(f"Error generating content: {e}")
                await message.channel.send(f"Something went wrong! Try again later. ({e})")
            if message.attachments:
                await handle_attachment(message.attachments[0], message)
            await bot.process_commands(message)  # Process commands only if the bot responds
        else:
            await message.channel.send(f"You sent an empty message! '{message}'")
            if message.attachments:
                await handle_attachment(message.attachments[0], message)
    elif message.mentions and bot.user in message.mentions:
        # Message mentions the bot, respond to the message
        if message.clean_content:
            try:
                async with message.channel.typing():
                    result = model.generate_content(message.clean_content)
                    text = result.text
                    if len(text) > 2000:
                        chunks = [text[i:i + 2000] for i in range(0, len(text), 2000)]
                        for chunk in chunks:
                            await message.reply(chunk, allowed_mentions=discord.AllowedMentions.none())
                    else:
                        await message.reply(text, allowed_mentions=discord.AllowedMentions.none())
            except Exception as e:
                logging.error(f"Error generating content: {e}")
                await message.channel.send(f'Something went wrong! Try again later. {e}')
            if message.attachments:
                await handle_attachment(message.attachments[0], message)
        else:
            await message.channel.send('You sent an empty message!')
            if message.attachments:
                await handle_attachment(message.attachments[0], message)
    else:
        # Channel is not activated, ignore the message
        pass

# Slash command to generate a response
@bot.tree.command(name="generate", description="Generate a response")
async def generate(interaction: discord.Interaction, *, prompt: str):
    try:
        async with interaction.channel.typing():
            result = model.generate_content(message)
            text = result.text
            if len(text) > 2000:
                chunks = [text[i:i + 2000] for i in range(0, len(text), 2000)]
                for chunk in chunks:
                    embed = discord.Embed(
                    title=f"{message.content}",
                    description=f"{text}",
                color=discord.Color(value=0x87CEFA)  # Set color to #87CEFA
            )
                embed.set_thumbnail(url="https://d1muf25xaso8hp.cloudfront.net/https%3A%2F%2Fmeta-q.cdn.bubble.io%2Ff1707847080246x798414315632580500%2FGoogle-Gemini-AI-Icon.png?w=64&h=64&auto=compress&dpr=1.75&fit=max")
                embed.set_author(name=f"{interaction.author.name}", icon_url=interaction.author.avatar.url)
                await interaction.followup.send(embed=embed)
            else:
                await interaction.followup.send(embed=embed)
    except Exception as e:
        await interaction.response.send_message(f"Error generating content: {e}")
    if interaction.data.options:
        for option in interaction.data.options:
            if option.name == 'attachment':
                attachment = option.value
                await handle_attachment(attachment, interaction)
                break

async def handle_attachment(attachment, message):
    try:
        async with message.channel.typing():
            if attachment.filename.endswith(('.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tif', '.tiff')):
                # Image attachment
                file_path = f"{attachment.filename}"
                await attachment.save(file_path)
                image = Image.open(file_path)
                result = model.generate_content(image)
                text = result.text
                if len(text) > 2000:
                    chunks = [text[i:i + 2000] for i in range(0, len(text), 2000)]
                    for chunk in chunks:
                        await message.channel.send(chunk)
                else:
                    await message.channel.send(text)
            elif attachment.filename.endswith(('.mp4', '.mov', '.avi', '.wmv', '.flv')):
                # Video attachment
                await attachment.save(attachment.filename)
                await message.channel.send("Video received!")
            elif attachment.filename.endswith(('.mp3', '.wav', '.ogg', '.m4a')):
                # Audio attachment
                await attachment.save(attachment.filename)
                await message.channel.send("Audio received!")
            elif attachment.filename.endswith(('.txt', '.doc', '.docx', '.pdf')):
                # Text attachment
                await attachment.save(attachment.filename)
                with open(attachment.filename, 'r') as file:
                    content = file.read()
                    result = model.generate_content(content)
                    text = result.text
                    if len(text) > 2000:
                        chunks = [text[i:i + 2000] for i in range(0, len(text), 2000)]
                        for chunk in chunks:
                            await message.channel.send(chunk)
                    else:
                        await message.channel.send(text)
            else:
                await message.channel.send("Unsupported file type!")
    except Exception as e:
  
