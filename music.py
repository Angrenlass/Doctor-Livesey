import os
import asyncio
import discord
import random
import yt_dlp as youtube_dl
from collections import deque
from discord.ext import commands
from discord import FFmpegPCMAudio

# Конфігурація yt-dlp (тільки стрімінг)
ytdl_format_options = {
    'format': 'bestaudio[ext=webm]/bestaudio/best',
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


# Отримати інфу про трек
async def fetch_info(url: str, loop=None) -> dict:
    # Повертає словник з інфою про трек (без завантаження)
    loop = loop or asyncio.get_event_loop()
    data = await loop.run_in_executor(
        None, lambda: ytdl.extract_info(url, download=False)
    )
    if 'entries' in data:
        data = data['entries'][0]
    return data


# Джерело аудіо
class YTDLSource(discord.PCMVolumeTransformer):
    def __init__(self, source, *, data, volume=0.5):
        super().__init__(source, volume)
        self.data = data
        self.title = data.get('title')

    @classmethod
    def from_info(cls, data: dict):
        # Створює джерело зі стрім-URL
        source = discord.FFmpegPCMAudio(data['url'], **ffmpeg_options)
        return cls(source, data=data)

# Cog
class Music(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        # guild_id → deque of info-dicts
        self._queues: dict[int, deque] = {}

    # Внутрішні хелпери

    def get_queue(self, guild_id: int) -> deque:
        if guild_id not in self._queues:
            self._queues[guild_id] = deque()
        return self._queues[guild_id]

    def play_next(self, ctx):
        # Callback після завершення треку — запускає наступний з черги
        queue = self.get_queue(ctx.guild.id)
        if queue:
            info = queue.popleft()
            asyncio.run_coroutine_threadsafe(
                self._play_info(ctx, info), self.bot.loop
            )

    async def _play_info(self, ctx, info: dict):
        # Створити джерело і почати відтворення
        vc = ctx.guild.voice_client
        if not vc:
            return

        try:
            source = YTDLSource.from_info(info)
        except Exception as e:
            await ctx.send(f"АХАХ, СЕР, ЩОСЬ ПІШЛО НЕ ТАК: {e}")
            self.play_next(ctx)
            return

        vc.play(source, after=lambda e: self.play_next(ctx))
        await ctx.send(f"**Граю:** {info['title']}")

    # Команди
    @commands.command(aliases=['j'])
    async def join(self, ctx):
        # Зайти в голосовий канал і зіграти livesey.mp3
        channel = ctx.message.author.voice.channel
        await channel.connect()
        vc = ctx.guild.voice_client
        vc.play(FFmpegPCMAudio(source=os.path.join("bar", "livesey.mp3")))

    @commands.command(aliases=['p'])
    async def play(self, ctx, *, url: str):
        # Якщо нічого не грає — починає одразу. Якщо грає — додає в чергу
        async with ctx.typing():
            try:
                info = await fetch_info(url, loop=self.bot.loop)
            except Exception as e:
                await ctx.send(f"АХАХ, СЕР, НЕ ВДАЛОСЬ ЗНАЙТИ: {e}")
                return

        vc = ctx.guild.voice_client
        if vc and vc.is_playing():
            self.get_queue(ctx.guild.id).append(info)
            duration = info.get('duration') or 0
            mins, secs = divmod(duration, 60)
            await ctx.send(
                f"**Додано до черги:** {info['title']} "
                f"[{mins}:{secs:02d}] · позиція {len(self.get_queue(ctx.guild.id))}"
            )
        else:
            await self._play_info(ctx, info)

    @commands.command(aliases=['q'])
    async def queue(self, ctx, *, url: str = None):
        
        #.q <посилання> — додати трек в кінець черги.
        # .q             — показати поточну чергу.
        
        if url is None:
            q = self.get_queue(ctx.guild.id)
            vc = ctx.guild.voice_client

            if not q and (not vc or not vc.is_playing()):
                await ctx.send("АХАХ, СЕР, ЧЕРГА ПОРОЖНЯ!")
                return

            lines = []
            if vc and vc.is_playing() and hasattr(vc.source, 'title'):
                lines.append(f"🎵 **Зараз грає:** {vc.source.title}")

            if q:
                lines.append("\n**Черга:**")
                for i, info in enumerate(q, 1):
                    duration = info.get('duration') or 0
                    mins, secs = divmod(duration, 60)
                    lines.append(f"  {i}. {info['title']} [{mins}:{secs:02d}]")
            else:
                lines.append("\nЧерга порожня (це останній трек)")

            await ctx.send('\n'.join(lines))
            return

        # Додати в чергу
        async with ctx.typing():
            try:
                info = await fetch_info(url, loop=self.bot.loop)
            except Exception as e:
                await ctx.send(f"АХАХ, СЕР, НЕ ВДАЛОСЬ ЗНАЙТИ: {e}")
                return

        vc = ctx.guild.voice_client
        if not vc or not vc.is_playing():
            await self._play_info(ctx, info)
        else:
            self.get_queue(ctx.guild.id).append(info)
            duration = info.get('duration') or 0
            mins, secs = divmod(duration, 60)
            await ctx.send(
                f"**Додано до черги:** {info['title']} "
                f"[{mins}:{secs:02d}] · позиція {len(self.get_queue(ctx.guild.id))}"
            )

    @commands.command(aliases=['s'])
    async def skip(self, ctx):
        vc = ctx.guild.voice_client
        if vc and vc.is_playing():
            vc.stop()  # after= callback запустить наступний
            await ctx.send("АХАХ, ПРОПУСКАЮ!")
        else:
            await ctx.send("СЕР, Я Ж НІЧОГО НЕ ГРАЮ, АХАХАХХА")

    @commands.command(aliases=['qc'])
    @commands.has_permissions(administrator=True)
    async def qclear(self, ctx):
        self.get_queue(ctx.guild.id).clear()
        await ctx.send("АХАХ, ЧЕРГА ОЧИЩЕНА!")

    @commands.command(aliases=['br'])
    async def bar(self, ctx, args: str):
        vc = ctx.guild.voice_client
        if not args.endswith('.mp3'):
            args += '.mp3'
        vc.play(FFmpegPCMAudio(source=os.path.join("bar", args)))

    @commands.command(aliases=['brr'])
    async def barandom(self, ctx):
        directory = os.path.join("bar")
        files = [
            f for f in os.listdir(directory)
            if os.path.isfile(os.path.join(directory, f)) and f.endswith('.mp3')
        ]
        if not files:
            await ctx.send("АХАХ, СЕР, Я НЕ МАЮ ЩО ГРАТИ!!!!")
            return
        source = random.choice(files)
        ctx.voice_client.play(FFmpegPCMAudio(source=os.path.join(directory, source)))

    @commands.command(aliases=['b'])
    async def pause(self, ctx):
        vc = ctx.guild.voice_client
        if vc and vc.is_playing():
            await vc.pause()
        else:
            await ctx.send("СЕР, Я Ж НІЧОГО НЕ ГРАЮ, АХАХАХХА")

    @commands.command(aliases=['res'])
    async def resume(self, ctx):
        vc = ctx.guild.voice_client
        if vc and vc.is_paused():
            await vc.resume()
        else:
            await ctx.send("СЕР, Я Ж НІЧОГО НЕ ГРАЮ, АХАХАХХА")

    @commands.command(aliases=['l'])
    async def leave(self, ctx):
        self.get_queue(ctx.guild.id).clear()
        await ctx.voice_client.disconnect()

    # ── Before invoke ──────────────────────────

    @play.before_invoke
    @queue.before_invoke
    @bar.before_invoke
    @barandom.before_invoke
    async def ensure_voice(self, ctx):
        if ctx.voice_client is None:
            if ctx.author.voice:
                await ctx.author.voice.channel.connect()
            else:
                await ctx.send("СЕР, ВИ НІКУДИ НЕ ПІДʼЄДНАНІ, АХАХА")
                raise commands.CommandError("Author not connected to a voice channel.")