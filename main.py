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
HAS_TEAM = 'Faci deja parte dintr-o echipă?'
IS_ONSITE = 'Vei participa fizic la competiție?'
TEAM_ROLE_COLOR = 0x2741F8
YES = "Da"
NO = "Nu"
SINGLE = "Single"
ONLINE_ROLE = "Online"
ONSITE_ROLE = "On-site"

intents = discord.Intents.all()

db = database.load(DB_PATH)

bot = commands.Bot(command_prefix = '$', intents = intents)

async def add_info(ctx, team_name):
    guild = ctx.guild

    role = get(guild.roles, name = team_name)
    if(role is None):
        role = await guild.create_role(name = team_name, colour = discord.Colour(TEAM_ROLE_COLOR))
        await ctx.send(f"Am creat rolul {team_name}")
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
        await ctx.send(f"Am creat categoria {team_name}")
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

async def update_server_info(ctx, db, old_db): 
    for _, participant in db.iterrows():
        discord_name = participant[DISCORD_USER].strip()

        await ctx.send(f"Verific participantul {discord_name}")

        if(participant[HAS_TEAM] == NO):
            team_name = SINGLE
        else:
            team_name = participant[TEAM_NAME].strip()
        
        location_role = ONLINE_ROLE
        if(participant[IS_ONSITE] == YES):
            location_role = ONSITE_ROLE

        user_old_info = old_db.loc[old_db[DISCORD_USER] == discord_name]

        old_team_name = None
        old_location_role = None
        for _, old_participant in user_old_info.iterrows():
            if(old_participant[HAS_TEAM] == NO):
                old_team_name = SINGLE
            else:
                old_team_name = participant[TEAM_NAME].strip()
            
            old_location_role = ONLINE_ROLE
            if(participant[IS_ONSITE] == YES):
                old_location_role = ONSITE_ROLE


        await add_info(ctx, team_name)
        await assign_user(ctx.guild, discord_name, team_name, old_team_name)
        await assign_user(ctx.guild, discord_name, location_role, old_location_role)


@bot.command()
@commands.has_any_role("Admin")
async def update(ctx):
    global db
    for att in ctx.message.attachments: 
        await att.save("new_db.csv")
        new_db = database.load("new_db.csv")
        await update_server_info(ctx, new_db, db)
        db = new_db

    database.save(db, "db.csv")
    await ctx.send(f"Totul s-a desfasurat cu succes!")

@bot.event
async def on_ready():
    pass

@bot.event
async def on_member_join(member):
    global db
    for _, participant in db.iterrows():
        if(participant[DISCORD_USER].strip() == member.name):
            if(participant[HAS_TEAM] == NO):
                team_name = SINGLE
            else:
                team_name = participant[TEAM_NAME].strip()

            location_role = ONLINE_ROLE
            if(participant[IS_ONSITE] == YES):
                location_role = ONSITE_ROLE
            
            await assign_user(member.guild, member.name, team_name)
            await assign_user(member.guild, member.name, location_role)
            break
            
bot.run(TOKEN)







