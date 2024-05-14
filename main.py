import os
import discord
import random
import openai
import asyncio
import yt_dlp as youtube_dl
from discord.ext import commands
from config import *
from dialogs import *

openai.api_key = OPENAI_TOKEN
intents = discord.Intents.default()
intents.voice_states = True
bot = commands.Bot(command_prefix=PREFIX, intents=discord.Intents.all())
bot.remove_command("help")

@bot.event
async def on_ready():
    print('Bot connected')
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name="карту"))

@bot.event
async def on_member_join(member):
    channel = bot.get_channel(CHANNEL_MAIN)
    role = discord.utils.get(member.guild.roles, id = NEW_MEMBER_ROLE)
    await member.add_roles(role)
    await channel.send(f'АХАХАХАХХА, СЕР ``{member.name}``, РАДІ ВАС БАЧИТИ!')

#leave event
@bot.event
async def on_member_remove(member):
    channel = bot.get_channel(CHANNEL_MAIN)
    await channel.send(f'АХАХАХАХХА, ПАН(І) ``{member.name}`` БІЛЬШЕ НЕ АХАХА УЧАСНИК НАШОГО ПРИТУЛКУ АХАХА')

# help command with permissions checking
@bot.command()
async def help(ctx):
    if ctx.author.guild_permissions.administrator:
        emb = discord.Embed(
            title="Навігація вказівками",
            color=0x969696
        )
        emb.add_field(name=".Грати", value="покличу всіх пограти", inline=False)
        emb.add_field(name=".Спати", value="вкладу всіх спати", inline=False)
        emb.add_field(name=".clear (число)", value="почистити чат на визначену кількість повідомлень, включно із командою", inline=False)
        emb.add_field(name=".mute (тег гравця)", value="замьютити учасника", inline=False)
        emb.add_field(name=".unmute (тег гравця)", value= "анмьютнути учасника", inline=False)
        emb.add_field(name=".kick (тег гравця)", value="кікнути учасника", inline=False)
        emb.add_field(name=".gpt (текст)", value="застосовуй chatgpt прям на сервері", inline=False)
        emb.add_field(name=".Лівсі (запитання)", value="запитати в мене щось та отримай передбачення", inline=False)
        emb.add_field(name=".Монетка", value="підкинути монетку", inline=False)
        await ctx.send(embed=emb)
    else:
        emb = discord.Embed(
            title="Навігація вказівками",
            color=0x969696
        )
        emb.add_field(name=".gpt (текст)", value="застосовуй chatgpt прям на сервері", inline=False)
        emb.add_field(name=".Лівсі (запитання)", value="запитати в мене щось та отримай передбачення", inline=False)
        emb.add_field(name=".Монетка", value="підкинути монетку", inline=False)
        await ctx.send(embed=emb)
    # if ctx.author.guild_permissions.administrator:
    #     for adm_key, adm_value in help_administrator_command.items():
    #         emb = discord.Embed(title='Навігація вказівками')
    #         emb.add_field(name=adm_key, value=adm_value, inline=False)
    #         await ctx.send(embed=emb)
    # else:
    #     for usr_key, usr_value in help_user_command:
    #         emb = discord.Embed(title='Навігація вказівками')
    #         emb.add_field(name=usr_key, value=usr_value)
    #         await ctx.send(embed=emb)

#preditctions for questions 
@bot.command(aliases = ['лівсі', 'Ливси', 'ливси'])
async def Лівсі(ctx):
    await ctx.reply(random.choice(list(predictions.items()))[1])

#сoin
@bot.command(aliases = ['монетка'])
async def Монетка(ctx):
    await ctx.reply(random.choice(list(coin.items()))[1])

#role mentioning with clearing written command
@bot.command(aliases = ['all', 'грати', '!'])
@commands.has_permissions(administrator = True)
async def Грати(ctx, amount = 1):
    await ctx.channel.purge(limit = amount)
    close_friends_role = discord.utils.get(ctx.message.guild.roles, id = CLOSE_FRIENDS_ROLE)
    role = discord.utils.get(ctx.message.guild.roles, id = NEW_MEMBER_ROLE)
    await ctx.send(f"{ close_friends_role.mention }, { role.mention }, ДРУЗІ ПРЕКРАСНІ, АХАХАХХАХА, КЛИЧУ ВАС ГРАТИ!")

@bot.command(aliases = ['спати', 'сон', 'Сон'])
@commands.has_permissions(administrator = True)
async def Спати(ctx, amount = 1):
    await ctx.channel.purge(limit = amount)
    close_friends_role = discord.utils.get(ctx.message.guild.roles, id = CLOSE_FRIENDS_ROLE)
    andrew_role = discord.utils.get(ctx.message.guild.roles, id = ANDREW_ROLE)
    await ctx.send(f"{ close_friends_role.mention }, АХАХАХ, МОЇ ДРУЗІ, ДЯКУЮ ЗА ПРОВЕДЕНИЙ ЧАС, ВСІМ ДОБРАНІЧ! А {andrew_role.mention} - ПРЕКРАСНОГО ДНЯ!!!")

#сlear messages
@bot.command()
@commands.has_permissions(administrator = True)
async def clear(ctx, amount = 2):
    await ctx.channel.purge(limit = amount)

#kick command
@bot.command()
@commands.has_permissions(administrator = True)
async def kick(ctx, member: discord.Member, *, reason = None):
    await ctx.channel.purge(limit = 1)
    await member.kick(reason = reason)
    await ctx.send(f"*ВДАРИВ { member.mention }* \nАХАХАХАХАХАХАХАХА, ВИБАЧТЕ-ВИБАЧТЕ")

#mute command
@bot.command()
@commands.has_permissions(administrator = True)
async def mute(ctx, member: discord.Member):
    await ctx.channel.purge(limit = 1)
    mute_role = discord.utils.get(ctx.message.guild.roles, name = "Muted")
    await member.add_roles(mute_role)
    await ctx.send(f"*СТУЛИВ ПЕЛЬКУ { member.mention }* \nАХАХАХАХАХАХХААХХАХАХАХ")

#unmute
@bot.command()
@commands.has_permissions(administrator = True)
async def unmute(ctx, member: discord.Member):
    await ctx.channel.purge(limit = 1)
    mute_role = discord.utils.get(ctx.message.guild.roles, id = MUTED_ROLE)
    await member.remove_roles(mute_role)
    await ctx.send(f"{ member.mention }, ПРЕПРОШУЮ, АХАХАХХА, ЩО ВИ ТАМ КАЗАЛИ?")

@bot.command()
async def gpt(ctx, *prompts: str):
    message_list = [{'role': 'user', 'content': prompt} for prompt in prompts]

    completion = openai.ChatCompletion.create(
        model='gpt-3.5-turbo',
        messages=message_list,
        max_tokens = 1000,
        frequency_penalty=0.0,
        temperature=0
    )
    
    response = completion['choices'][0]['message']['content']
    await ctx.send(response)

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


@bot.command(aliases = ['p'])
async def play(ctx, url):
    song_there = os.path.isfile('song.mp3')
    server = ctx.message.guild
    voice_channel = server.voice_client
    try:
        if song_there:
            os.remove(os.path.join(os.getcwd(),"song.mp3"))
            
        async with ctx.typing():
            info = await YTDLSource.from_url(url, loop=bot.loop, stream=True)
            filename = await YTDLSource.from_url(url, loop=bot.loop)
            voice_channel.play(discord.FFmpegPCMAudio(executable = "/bin/ffmpeg", source=filename))
        await ctx.send('**Now playing:** {}'.format(info['title']))
    except youtube_dl.utils.DownloadError as e:
        await ctx.send(f"Failed to play the song: {e}")

@bot.command(aliases=['s'])
async def stream(ctx, url):
    server = ctx.message.guild
    voice_channel = server.voice_client
    try:
        async with ctx.typing():
            # Fetch the stream URL instead of downloading
            info = await YTDLSource.from_url(url, loop=bot.loop, stream=True)
            source = discord.FFmpegPCMAudio(info['url'], **ffmpeg_options)
            voice_channel.play(source)
        await ctx.send('**Now playing:** {}'.format(info['title']))
    except youtube_dl.utils.DownloadError as e:
        await ctx.send(f"Failed to play the song: {e}")

@bot.command(aliases=['j'])
async def join(ctx):
    if not ctx.message.author.voice:
        await ctx.send("{} is not connected to a voice channel".format(ctx.message.author.name))
        return
    else:
        channel = ctx.message.author.voice.channel
    await channel.connect()

@bot.command(aliases=['h'])
async def halt(ctx):
    voice_client = ctx.message.guild.voice_client
    if voice_client.is_playing():
        await voice_client.pause()
    else:
        await ctx.send("The bot is not playing anything at the moment.")
    
@bot.command(aliases=['r'])
async def resume(ctx):
    voice_client = ctx.message.guild.voice_client
    if voice_client.is_paused():
        await voice_client.resume()
    else:
        await ctx.send("The bot was not playing anything before this. Use play_song command")

@bot.command()
async def volume(ctx, vol: int):
    voice_client = ctx.guild.voice_client
    if voice_client:
        if 0 <= vol <= 100:
            voice_client.source.volume = vol / 100
            await ctx.send(f"Volume set to {vol}%")
        else:
            await ctx.send("Volume must be between 0 and 100.")
    else:
        await ctx.send("Bot is not connected to a voice channel.")

@bot.command()
async def stop(ctx):
    voice_client = ctx.message.guild.voice_client
    if voice_client.is_playing():
        await voice_client.stop()
    else:
        await ctx.send("The bot is not playing anything at the moment.")

@bot.command()
async def leave(ctx):
    voice_client = ctx.message.guild.voice_client
    if voice_client.is_connected():
        await voice_client.disconnect()
    else:
        await ctx.send("The bot is not connected to a voice channel.")

bot.run(TOKEN)