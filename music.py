import os
import asyncio
import discord
import random
import yt_dlp as youtube_dl
from discord.ext import commands
from discord import FFmpegPCMAudio

ytdl_format_options = {
    'format': 'bestaudio[ext=webm]/bestaudio/best',
    'postprocessors': [{
        'key': 'FFmpegExtractAudio',
        'preferredcodec': 'opus',
        'preferredquality': '192',
    }],
    'outtmpl': '%(title)s.%(ext)s',
    'restrictfilenames': True,
    'noplaylist': True,
    'quiet': False,
    'default_search': 'auto',
    'ffmpeg_location': r'C:\ffmpeg\bin',
}

ffmpeg_options = {
    'before_options': (
        '-reconnect 1 '
        '-reconnect_streamed 1 '
        '-reconnect_delay_max 5'
    ),
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
            #Take first item from a playlist
            data = data['entries'][0]
        if stream:
            #If streaming, directly return the URL
            return {'title': data['title'], 'url': data['url']}
        else:
            #If downloading, prepare the filename
            filename = ytdl.prepare_filename(data)
            return filename

class Music(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(aliases=['j'])
    async def join(self, ctx):
        channel = ctx.message.author.voice.channel
        await channel.connect()

        server = ctx.message.guild
        voice_channel = server.voice_client
        source = os.path.join("bar/livesey.mp3")
        voice_channel.play(FFmpegPCMAudio(source=source))

    @commands.command(aliases=['p'])
    async def play(self, ctx, *, url):
        server = ctx.message.guild
        voice_channel = server.voice_client
        try:
            async with ctx.typing():
            #Fetch the stream URL instead of downloading
                info = await YTDLSource.from_url(url, loop=self.bot.loop, stream=True)
                source = discord.FFmpegPCMAudio(info['url'], **ffmpeg_options)
                voice_channel.play(source)
                await ctx.send('Граю: {}'.format(info['title']))
        except youtube_dl.utils.DownloadError as e:
            await ctx.send(f"Не вдалось зіграти: {e}")

    @commands.command(aliases=['br'])
    async def bar(self, ctx, args):
        server = ctx.message.guild
        voice_channel = server.voice_client
        if not args.endswith('.mp3'):
            args += '.mp3'
        source = os.path.join("bar", args)
        voice_channel.play(FFmpegPCMAudio(source=source))

    #Command that choosing random mp3 from bar directory and playing it in voice
    @commands.command(aliases=['brr'])
    async def barandom(self, ctx):
        #Define the directory path
        directory = os.path.join("bar")
        #Get a list of mp3 files in the directory
        files = [f for f in os.listdir(directory) if os.path.isfile(os.path.join(directory, f)) and f.endswith('.mp3')]
        #Check if the directory is empty( maybe it would be empty for you, cause I don't want to post my sound bar directory:) )
        if not files:
            await ctx.send("АХАХ, СЕР, Я НЕ МАЮ ЩО ГРАТИ!!!!")
            return
        #Choose a random file
        source = random.choice(files)
        source_path = os.path.join(directory, source)
        #Play the file
        ctx.voice_client.play(FFmpegPCMAudio(source=source_path))

    @commands.command(aliases=['b'])
    async def pause(self, ctx):
        voice_client = ctx.message.guild.voice_client
        if voice_client.is_playing():
            await voice_client.pause()
        else:
            await ctx.send("СЕР, Я Ж НІЧОГО НЕ ГРАЮ, АХАХАХХА")
    
    @commands.command(aliases=['r'])
    async def resume(self, ctx):
        voice_client = ctx.message.guild.voice_client
        if voice_client.is_paused():
            await voice_client.resume()
        else:
            await ctx.send("СЕР, Я Ж НІЧОГО НЕ ГРАЮ, АХАХАХХА")

    @commands.command(aliases=['l'])
    async def leave(self, ctx):
        await ctx.voice_client.disconnect()

    @play.before_invoke
    @bar.before_invoke
    @barandom.before_invoke
    async def ensure_voice(self, ctx):
        if ctx.voice_client is None:
            if ctx.author.voice:
                await ctx.author.voice.channel.connect()
            else:
                await ctx.send("СЕР, ВИ НІКУДИ НЕ ПІДʼЄДНАНІ, АХАХА")
                raise commands.CommandError("Author not connected to a voice channel.")
        elif ctx.voice_client.is_playing():
            ctx.voice_client.stop()