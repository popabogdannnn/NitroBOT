import discord
from discord.ext import commands
from discord.utils import get
from dotenv import load_dotenv
import os
import database
import subprocess

load_dotenv()

TOKEN = os.getenv('TOKEN')
DB_PATH = os.getenv('DB_PATH')
TEAM_NAME = 'Dacă da, care este numele echipei?'
DISCORD_USER = 'Username Discord'
TEAM_ROLE_COLOR = 0x2741F8

db = database.load(DB_PATH)

intents = discord.Intents.all()

bot = commands.Bot(command_prefix = '$', intents = intents)

async def add_info(ctx, team_name):
    guild = ctx.guild

    role = get(guild.roles, name = team_name)
    if(role is None):
        role = await guild.create_role(name = team_name, colour = discord.Colour(TEAM_ROLE_COLOR))
        await ctx.send(f"Am creat rolul {team_name}.")
    admin_role = get(guild.roles, name = "Admin")

    
    category = get(guild.categories, name = team_name)
    if(category is None):
        category = await guild.create_category(name = team_name)

        overwrites = {
            guild.default_role: discord.PermissionOverwrite(read_messages=False, connect=False),
            role: discord.PermissionOverwrite(read_messages=True, send_messages=True, connect=True, speak=True),
            admin_role: discord.PermissionOverwrite(read_messages=True, send_messages=True, connect=True, speak=True)
        }

        await category.edit(overwrites=overwrites)

        await guild.create_text_channel(name = "text", category = category)
        await guild.create_voice_channel(name = "voice", category = category)
        await ctx.send(f"Am creat categoria {team_name}")

async def assign_user(guild, discord_name, team_name):
    user = get(guild.members, name = discord_name)
    if(user is None):
        return
    role = get(guild.roles, name = team_name)
    await user.add_roles(role)


async def update_server_info(ctx, db): 
    for _, participant in db.iterrows():
        team_name = participant[TEAM_NAME].strip()
        discord_name = participant[DISCORD_USER].strip()

        await add_info(ctx, team_name)
        await assign_user(ctx.guild, discord_name, team_name)


@bot.command()
@commands.has_any_role("Admin")
async def update(ctx, url):
    # subprocess.run(
    #     args = ["wget", "-O", "new_db.csv", url],
    #     capture_output = True,
    # )
    
    await update_server_info(ctx, db)

    await ctx.send(f"Totul s-a desfasurat cu succes!")

@bot.event
async def on_ready():
    pass

@bot.event
async def on_member_join(member):
    for _, participant in db.iterrows():
        if(participant[DISCORD_USER].strip() == member.name):
            await assign_user(member.guild, member.name, participant[TEAM_NAME].strip())
            break
            



bot.run(TOKEN)







