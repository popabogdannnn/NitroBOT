import discord
from discord.ext import commands, tasks
from discord.utils import get
from dotenv import load_dotenv
import os
import database
import subprocess

load_dotenv()

TOKEN = os.getenv('TOKEN')
DB_PATH = os.getenv('DB_PATH')
TEAM_NAME = 'Daca da, care este numele echipei'
DISCORD_USER = 'Username Discord'
HAS_TEAM = 'Faci parte deja dintr-o echipă?'
IS_ONSITE = 'Vei participa fizic la competiție?'
TEAM_ROLE_COLOR = 0x2741F8
YES = "Da"
NO = "Nu"
NO_PARTICIPATION = "Nu voi participa la hackathon"
SINGLE = "Single"

GUILD_ID = 1348244782178107462
GUILD = None

intents = discord.Intents.all()

db = database.load()

bot = commands.Bot(command_prefix = '$', intents = intents)

async def add_info(team_name):
    guild = GUILD

    role = get(guild.roles, name = team_name)
    if(role is None):
        role = await guild.create_role(name = team_name, colour = discord.Colour(TEAM_ROLE_COLOR))

    admin_role = get(guild.roles, name = "Admin")
    volunteer_role = get(guild.roles, name = "Voluntar")
    mentor_role = get(guild.roles, name = "Mentor")

    team_name = team_name.lower()

    category = get(guild.categories, name = team_name)
    
    overwrites = {
        guild.default_role: discord.PermissionOverwrite(read_messages=False, connect=False),
        role: discord.PermissionOverwrite(read_messages=True, send_messages=True, connect=True, speak=True),
        admin_role: discord.PermissionOverwrite(read_messages=True, send_messages=True, connect=True, speak=True),
        mentor_role: discord.PermissionOverwrite(read_messages=True, send_messages=True, connect=True, speak=True),
        volunteer_role: discord.PermissionOverwrite(read_messages=True, send_messages=True, connect=True, speak=True),
    }

    if(category is None):
        category = await guild.create_category(name = team_name)

        await category.edit(overwrites=overwrites)

        await guild.create_text_channel(name = "text", category = category)
        await guild.create_voice_channel(name = "voice", category = category)
    else:
        await category.edit(overwrites=overwrites)

async def assign_user(guild, discord_name, role_name, old_role_name = None):
    user = get(guild.members, name = discord_name)
    if(user is None):
        return
    if(old_role_name is not None):
        old_role = get(guild.roles, name = old_role_name)
        await user.remove_roles(old_role)
    new_role = get(guild.roles, name = role_name)
    await user.add_roles(new_role)

async def update_server_info(db, old_db): 
    global GUILD
    for _, participant in db.iterrows():
        if(participant[HAS_TEAM] == NO_PARTICIPATION):
            continue
        discord_name = participant[DISCORD_USER].strip()

        if(participant[HAS_TEAM] == NO):
            team_name = SINGLE
        else:
            team_name = participant[TEAM_NAME].strip()

        user_old_info = old_db.loc[old_db[DISCORD_USER] == discord_name]

        old_team_name = None
        

        for _, old_participant in user_old_info.iterrows():
            if(old_participant[HAS_TEAM] == NO):
                old_team_name = SINGLE
            else:
                old_team_name = participant[TEAM_NAME].strip()
            

        
        print(f"Discord {discord_name}, team: {team_name}, old_team: {old_team_name}")
        await add_info(team_name)
        await assign_user(GUILD, discord_name, team_name, old_team_name)


@tasks.loop(seconds = 300)
async def loop_update():
    global db
    new_db = database.load()
    if(new_db.equals(db)):
        return
    await update_server_info(new_db, db)
    db = new_db

@bot.event
async def on_ready():
    global GUILD, GUILD_ID
    for guild in bot.guilds:
        if(guild.id == GUILD_ID):
            GUILD = guild
    if not loop_update.is_running():
        loop_update.start()

@bot.event
async def on_member_join(member):
    global db
    if(member.guild.id != GUILD_ID):
        return
    for _, participant in db.iterrows():
        if(participant[DISCORD_USER].strip() == member.name):
            if(participant[HAS_TEAM] == NO):
                team_name = SINGLE
            else:
                team_name = participant[TEAM_NAME].strip()
            await assign_user(GUILD, team_name)
            break

@bot.command()
async def update(ctx):
    global db
    await ctx.send(f"Adaug echipe...")
    new_db = database.load()
    await update_server_info(new_db, db)
    db = new_db
    await ctx.send(f"Totul s-a desfasurat cu succes!")

bot.run(TOKEN)







