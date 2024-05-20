import os
import asyncio
import discord
import random
import yt_dlp as youtube_dl
from config import PREFIX
from discord.ext import commands
from discord import FFmpegPCMAudio

intents = discord.Intents.default()
intents.voice_states = True
bot = commands.Bot(command_prefix=PREFIX, intents=discord.Intents.all())
bot.remove_command("help")

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
    'source_address': '0.0.0.0', # bind to ipv4 since ipv6 addresses cause issues sometimes
    'outtmpl': 'song.mp3' # Temporary file template
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
        if stream:
            # If streaming, directly return the URL
            return {'title': data['title'], 'url': data['url']}
        else:
            # If downloading, prepare the filename
            filename = ytdl.prepare_filename(data)
            return filename

class Music(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def play(self, ctx, *, url):
        song_there = os.path.isfile('song.mp3')
        server = ctx.message.guild
        voice_channel = server.voice_client
        try:
            if song_there:
                os.remove(os.path.join(os.getcwd(),"song.mp3"))
            
            async with ctx.typing():
                info = await YTDLSource.from_url(url, loop=self.bot.loop, stream=True)
                filename = await YTDLSource.from_url(url, loop=self.bot.loop)
                voice_channel.play(discord.FFmpegPCMAudio(executable = "/bin/ffmpeg", source=filename))
            await ctx.send('**Now playing:** {}'.format(info['title']))
        except youtube_dl.utils.DownloadError as e:
            await ctx.send(f"Failed to play the song: {e}")

    @commands.command()
    async def stream(self, ctx, *, url):
        server = ctx.message.guild
        voice_channel = server.voice_client
        try:
            async with ctx.typing():
            # Fetch the stream URL instead of downloading
                info = await YTDLSource.from_url(url, loop=self.bot.loop, stream=True)
                source = discord.FFmpegPCMAudio(info['url'], **ffmpeg_options)
                voice_channel.play(source)
                await ctx.send('**Now playing:** {}'.format(info['title']))
        except youtube_dl.utils.DownloadError as e:
            await ctx.send(f"Failed to play the song: {e}")

    @commands.command()
    async def bar(self, ctx, args):
        server = ctx.message.guild
        voice_channel = server.voice_client
        source = os.path.join("bar", args)
        voice_channel.play(FFmpegPCMAudio(source=source))

    @commands.command()
    async def barandom(self, ctx):
        # Ensure the bot is connected to a voice channel
        if ctx.voice_client is None:
            if ctx.author.voice:
                await ctx.author.voice.channel.connect()
                print("Bot connected to the voice channel.")
            else:
                await ctx.send("You are not connected to a voice channel.")
                print("User is not connected to a voice channel.")
                return

        # Define the directory path
        directory = os.path.join("bar")
        print(f"Directory path: {directory}")

        # Check if the directory exists
        if not os.path.isdir(directory):
            await ctx.send(f"The directory {directory} does not exist.")
            print(f"The directory {directory} does not exist.")
            return

        # Get a list of MP3 files in the directory
        files = [f for f in os.listdir(directory) if os.path.isfile(os.path.join(directory, f)) and f.endswith('.mp3')]
        print(f"MP3 files in directory: {files}")

        # Check if the directory is empty
        if not files:
            await ctx.send(f"No MP3 files found in the directory {directory}.")
            print(f"No MP3 files found in the directory {directory}.")
            return

        # Choose a random file
        source = random.choice(files)
        source_path = os.path.join(directory, source)
        print(f"Selected file: {source_path}")

        # Play the file
        ctx.voice_client.play(FFmpegPCMAudio(source=source_path))
        await ctx.send(f"Now playing: {source}")
        print(f"Now playing: {source}")

        

    @commands.command(aliases=['b'])
    async def pause(self, ctx):
        voice_client = ctx.message.guild.voice_client
        if voice_client.is_playing():
            await voice_client.pause()
        else:
            await ctx.send("The bot is not playing anything at the moment.")
    
    @commands.command(aliases=['r'])
    async def resume(self, ctx):
        voice_client = ctx.message.guild.voice_client
        if voice_client.is_paused():
            await voice_client.resume()
        else:
            await ctx.send("The bot was not playing anything before this. Use play_song command")

    @commands.command(aliases=['l'])
    async def leave(self, ctx):
        await ctx.voice_client.disconnect()

    @play.before_invoke
    @stream.before_invoke
    @bar.before_invoke
    @barandom.before_invoke
    async def ensure_voice(self, ctx):
        if ctx.voice_client is None:
            if ctx.author.voice:
                await ctx.author.voice.channel.connect()
            else:
                await ctx.send("You are not connected to a voice channel.")
                raise commands.CommandError("Author not connected to a voice channel.")
        elif ctx.voice_client.is_playing():
            ctx.voice_client.stop()