import discord
import random
import asyncio
import yt_dlp as youtube_dl
from discord import FFmpegPCMAudio
from discord.ext import commands
from config import *
from dialogs import *
from music import *

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

async def help_adm_embed(ctx, category):
    embed = discord.Embed(title=f'Help - {category.capitalize()} Commands', color=0x969696)
    for command, description in help_adm_pages[category].items():
        embed.add_field(name=bot.command_prefix+command, value=description, inline=False)
    return embed

async def help_usr_embed(ctx, category):
    embed = discord.Embed(title=f'Help - {category.capitalize()} Commands', color=0x969696)
    for command, description in help_usr_pages[category].items():
        embed.add_field(name=bot.command_prefix+command, value=description, inline=False)
    return embed

@bot.command()
async def help(ctx):
    if ctx.author.guild_permissions.administrator:
        categories = list(help_adm_pages.keys())
        page = 0
        message = await ctx.send(embed=await help_adm_embed(ctx, categories[page]))

        await message.add_reaction('◀️')
        await message.add_reaction('▶️')

        def check(reaction, user):
            return user == ctx.author and str(reaction.emoji) in ['◀️', '▶️']

        while True:
            try:
                reaction, user = await bot.wait_for('reaction_add', timeout=60.0, check=check)

                if str(reaction.emoji) == '▶️':
                    page = (page + 1) % len(categories)
                elif str(reaction.emoji) == '◀️':
                    page = (page - 1) % len(categories)

                await message.edit(embed=await help_adm_embed(ctx, categories[page]))
                await message.remove_reaction(reaction, user)

            except asyncio.TimeoutError:
                break
    else:
        categories = list(help_usr_pages.keys())
        page = 0
        message = await ctx.send(embed=await help_usr_embed(ctx, categories[page]))

        await message.add_reaction('◀️')
        await message.add_reaction('▶️')

        def check(reaction, user):
            return user == ctx.author and str(reaction.emoji) in ['◀️', '▶️']

        while True:
            try:
                reaction, user = await bot.wait_for('reaction_add', timeout=60.0, check=check)

                if str(reaction.emoji) == '▶️':
                    page = (page + 1) % len(categories)
                elif str(reaction.emoji) == '◀️':
                    page = (page - 1) % len(categories)

                await message.edit(embed=await help_usr_embed(ctx, categories[page]))
                await message.remove_reaction(reaction, user)

            except asyncio.TimeoutError:
                break

#preditctions for questions 
@bot.command(aliases = ['Лівсі', 'лівсі', 'Ливси', 'ливси'])
async def livesey(ctx):
    await ctx.reply(random.choice(list(predictions.items()))[1])

#сoin
@bot.command(aliases = ['монетка', 'Монетка'])
async def coin(ctx):
    await ctx.reply(random.choice(list(coin.items()))[1])

#role mentioning with clearing written command
@bot.command(aliases = ['all', 'грати', 'Грати', '!'])
@commands.has_permissions(administrator = True)
async def game(ctx, amount = 1):
    await ctx.channel.purge(limit = amount)
    close_friends_role = discord.utils.get(ctx.message.guild.roles, id = CLOSE_FRIENDS_ROLE)
    role = discord.utils.get(ctx.message.guild.roles, id = NEW_MEMBER_ROLE)
    await ctx.send(f"{ close_friends_role.mention }, { role.mention }, ДРУЗІ ПРЕКРАСНІ, АХАХАХХАХА, КЛИЧУ ВАС ГРАТИ!")

@bot.command(aliases = ['Спати', 'спати', 'сон', 'Сон'])
@commands.has_permissions(administrator = True)
async def sleep(ctx, amount = 1):
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

async def main():
    async with bot:
        await bot.add_cog(Music(bot))
        await bot.start(TOKEN)

asyncio.run(main())