import asyncio
import discord
from discord.ext import commands,tasks
import os
from dotenv import load_dotenv
import youtube_dl

DOWNLOADS_FOLDER = "downloads"  # Name of the folder to store downloaded files
last_downloaded_file = None  # Define the last_downloaded_file variable

# Ensure the downloads folder exists
if not os.path.exists(DOWNLOADS_FOLDER):
    os.makedirs(DOWNLOADS_FOLDER)

load_dotenv()
# Get the API token from the .env file.
DISCORD_TOKEN = os.getenv("MTE2NTMwMDg0NTIxOTQyNjM3NA.GxGV61.iUG9lAp9q5RaFDukF9FUxOS4PH2J4ngEgS-PIc")

intents = discord.Intents().all()
client = discord.Client(intents=intents)
bot = commands.Bot(command_prefix='!',intents=intents)


youtube_dl.utils.bug_reports_message = lambda: ''

ytdl_format_options = {
    'format': 'bestaudio/best',
    'restrictfilenames': True,
    'noplaylist': True,
    'nocheckcertificate': True,
    'ignoreerrors': False,
    'logtostderr': False,
    'quiet': True,
    'no_warnings': True,
    'default_search': 'auto',
    'source_address': '0.0.0.0',
    'extractor': 'soundcloud,youtube',  # Add 'soundcloud' and 'youtube' as extractors
}


ffmpeg_options = {
    'options': '-vn'
}

ytdl = youtube_dl.YoutubeDL(ytdl_format_options)

class YTDLSource(discord.PCMVolumeTransformer):
    def __init__(self, source, *, data, volume=0.5):
        super().__init__(source, volume)
        self.data = data
        self.title = data.get('title')
        self.url = ""

    @classmethod
    async def from_url(cls, url, *, loop=None, stream=False):
        loop = loop or asyncio.get_event_loop()
        data = await loop.run_in_executor(None, lambda: ytdl.extract_info(url, download=not stream))
        if 'entries' in data:
            # take first item from a playlist
            data = data['entries'][0]
        filename = data['title'] if stream else ytdl.prepare_filename(data)
        return filename
    
@bot.command(name='play', help='To play a song')
async def play(ctx, url):
    server = ctx.message.guild
    voice_channel = server.voice_client

    # Check if the bot is not in a voice channel
    if voice_channel is None:
        await ctx.send("I'm not connected to a voice channel. Use the !join command to have me join one.")
        return

    global last_downloaded_file  # Declare last_downloaded_file as a global variable

    async with ctx.typing():
        try:
            if "soundcloud.com" in url:
                ytdl_format_options['extractor'] = 'soundcloud'
            else:
                ytdl_format_options['extractor'] = 'youtube'
            filename = await YTDLSource.from_url(url, loop=bot.loop)
            voice_channel.play(discord.FFmpegPCMAudio(executable="C:\\Users\\bakht\\Documents\\discord-music-bot\\ffmpeg\\bin\\ffmpeg.exe", source=filename))
            last_downloaded_file = filename  # Set the last downloaded file
            await ctx.send(f'**Now playing:** {filename}')
        except youtube_dl.utils.DownloadError as e:
            await ctx.send('An error occurred while trying to play the song. Please check the URL or try again later.')

@bot.command(name='stop', help='Stops the song')
async def stop(ctx):
    global last_downloaded_file  # Declare last_downloaded_file as a global variable

    voice_client = ctx.message.guild.voice_client

    if voice_client.is_playing():
        voice_client.stop()
        await ctx.send("The song has been stopped.")

        if last_downloaded_file:
            try:
                # Move the last downloaded file into the downloads folder
                os.replace(last_downloaded_file, os.path.join("C:\\Users\\bakht\\Documents\\discord-music-bot\\downloads", os.path.basename(last_downloaded_file)))
                await ctx.send(f'The song has been moved to the downloads folder.')
                last_downloaded_file = None  # Clear the last downloaded file variable
            except Exception as e:
                await ctx.send('An error occurred while moving the file to the downloads folder.')
    else:
        await ctx.send("The bot is not playing anything at the moment.")






@bot.command(name='join', help='Tells the bot to join the voice channel')
async def join(ctx):
    if not ctx.message.author.voice:
        await ctx.send("{} is not connected to a voice channel".format(ctx.message.author.name))
        return
    else:
        channel = ctx.message.author.voice.channel
    await channel.connect()


@bot.command(name='pause', help='This command pauses the song')
async def pause(ctx):
    voice_client = ctx.message.guild.voice_client

    if voice_client is None:
        await ctx.send("The bot is not connected to a voice channel.")
    elif voice_client.is_playing():
        voice_client.pause()
    else:
        await ctx.send("Whatta I do ?")

    
@bot.command(name='resume', help='Resumes the song')
async def resume(ctx):
    voice_client = ctx.message.guild.voice_client
    if voice_client.is_paused():
        await voice_client.resume()
    else:
        await ctx.send("Calm")
    


@bot.command(name='leave', help='To make the bot leave the voice channel')
async def leave(ctx):
    voice_client = ctx.message.guild.voice_client
    if voice_client.is_connected():
        await voice_client.disconnect()
    else:
        await ctx.send("Man I aint even wanna be with u lames ")

@bot.command(name='clear', help='Clears the downloaded files folder')
async def clear(ctx):
    global last_downloaded_file
    if os.path.exists(DOWNLOADS_FOLDER):
        # Delete all files in the DOWNLOADS_FOLDER
        for filename in os.listdir(DOWNLOADS_FOLDER):
            file_path = os.path.join(DOWNLOADS_FOLDER, filename)
            try:
                os.remove(file_path)
            except Exception as e:
                pass

        # Clear the last downloaded file variable
        last_downloaded_file = None

        await ctx.send('All downloaded files have been cleared.')
    else:
        await ctx.send('No downloaded files to clear.')

#Make skip button and make que system











if __name__ == "__main__" :
    bot.run("MTE2NTMwMDg0NTIxOTQyNjM3NA.GxGV61.iUG9lAp9q5RaFDukF9FUxOS4PH2J4ngEgS-PIc")


