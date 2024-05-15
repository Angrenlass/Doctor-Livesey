import os
import discord
import random
import openai
import asyncio
import yt_dlp as youtube_dl
from discord.ext import commands
from config import *
from dialogs import *
from music import *

openai.api_key = OPENAI_TOKEN
intents = discord.Intents.default()
intents.voice_states = True
bot = commands.Bot(command_prefix=PREFIX, intents=discord.Intents.all())
bot.remove_command("help")

@bot.event
async def on_ready():
    print('Bot connected')
    print(bot.cogs)
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

@bot.command(aliases=['j'])
async def join(ctx):
    if not ctx.message.author.voice:
        await ctx.send("{} is not connected to a voice channel".format(ctx.message.author.name))
        return
    else:
        channel = ctx.message.author.voice.channel
    await channel.connect()

async def main():
    async with bot:
        await bot.add_cog(Music(bot))
        await bot.start(TOKEN)


asyncio.run(main())