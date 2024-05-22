import discord
import random
import openai
import asyncio
from discord.ext import commands
from discord import Embed
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

help_pages = {
    'general': {
        'Command 1': 'Description 1',
        'Command 2': 'Description 2',
        'Command 3': 'Description 3'
    },
    'administrator': {
        'Admin Command 1': 'Admin Description 1',
        'Admin Command 2': 'Admin Description 2',
        'Admin Command 3': 'Admin Description 3'
    }
}

async def help_embed(ctx, category):
    embed = discord.Embed(title=f'Help - {category.capitalize()} Commands')
    for command, description in help_pages[category].items():
        embed.add_field(name=command, value=description, inline=False)
    return embed

@bot.command()
async def help(ctx):
    categories = list(help_pages.keys())
    page = 0
    message = await ctx.send(embed=await help_embed(ctx, categories[page]))

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

            await message.edit(embed=await help_embed(ctx, categories[page]))
            await message.remove_reaction(reaction, user)

        except asyncio.TimeoutError:
            break


# async def help_parser(ctx, category):
#     if ctx.author.guild_permissions.administrator:
#         if category == 'administrator':
#             emb = discord.Embed(title='Навігація вказівками для адміністраторів')
#             for adm_key, adm_value in help_administrator_command.items():
#                 emb.add_field(name=bot.command_prefix+adm_key, value=adm_value, inline=False)
#             return emb
#         elif category == 'music':
#             emb = discord.Embed(title='Навігація вказівками для музики')
#             for music_key, music_value in music_command.items():
#                 emb.add_field(name=bot.command_prefix+music_key, value=music_value, inline=False)
#             return emb
#         else:
#             return discord.Embed(title='Невірна категорія')
#     else:
#         return discord.Embed(title='Навігація вказівками')

# @bot.command()
# async def help(ctx, category='general'):
#     await ctx.send(embed=await help_parser(ctx, category))
        
          

#help command with permissions checking
# @bot.command()
# async def help(ctx):
#     if ctx.author.guild_permissions.administrator:
#         emb = discord.Embed(
#             title="Навігація вказівками",
#             color=0x969696
#         )
#         emb.add_field(name=".Грати", value="покличу всіх пограти", inline=False)
#         emb.add_field(name=".Спати", value="вкладу всіх спати", inline=False)
#         emb.add_field(name=".clear (число)", value="почистити чат на визначену кількість повідомлень, включно із командою", inline=False)
#         emb.add_field(name=".mute (тег гравця)", value="замьютити учасника", inline=False)
#         emb.add_field(name=".unmute (тег гравця)", value= "анмьютнути учасника", inline=False)
#         emb.add_field(name=".kick (тег гравця)", value="кікнути учасника", inline=False)
#         emb.add_field(name=".gpt (текст)", value="застосовуй chatgpt прям на сервері", inline=False)
#         emb.add_field(name=".Лівсі (запитання)", value="запитати в мене щось та отримай передбачення", inline=False)
#         emb.add_field(name=".Монетка", value="підкинути монетку", inline=False)
#         await ctx.send(embed=emb)
#     else:
#         emb = discord.Embed(
#             title="Навігація вказівками",
#             color=0x969696
#         )
#         emb.add_field(name=".gpt (текст)", value="застосовуй chatgpt прям на сервері", inline=False)
#         emb.add_field(name=".Лівсі (запитання)", value="запитати в мене щось та отримай передбачення", inline=False)
#         emb.add_field(name=".Монетка", value="підкинути монетку", inline=False)
#         await ctx.send(embed=emb)
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