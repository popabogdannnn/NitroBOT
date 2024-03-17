import discord
from discord.ext import commands
from discord.utils import get
from dotenv import load_dotenv
import os
import database

load_dotenv()

TOKEN = os.getenv('TOKEN')
DB_PATH = os.getenv('DB_PATH')
TEAM_NAME = 'Dacă da, care este numele echipei?'
DISCORD_USER = 'Username Discord'
TEAM_ROLE_COLOR = 0x2741F8

db = database.load(DB_PATH)

intents = discord.Intents.all()

bot = commands.Bot(command_prefix = '$', intents = intents)

async def add_info(guild, team_name):
    role = get(guild.roles, name = team_name)
    if(role is not None):
        return
    role = await guild.create_role(name = team_name, colour = discord.Colour(TEAM_ROLE_COLOR))
    category = await guild.create_category(name = team_name)

    overwrites = {
        guild.default_role: discord.PermissionOverwrite(read_messages=False, connect=False),
        role: discord.PermissionOverwrite(read_messages=True, send_messages=True, connect=True, speak=True)
    }

    await category.edit(overwrites=overwrites)

    await guild.create_text_channel(name = "text", category = category)
    await guild.create_text_channel(name = "voice", category = category)

async def update_server_info(ctx, db):    
    guild = ctx.guild
    for _, participant in db.iterrows():
        team_name = participant[TEAM_NAME].strip()
        
        await add_info(guild, team_name)




@bot.command()
async def update(ctx, url):
    print(url)

    await update_server_info(ctx, db)

@bot.event
async def on_ready():
    pass



bot.run(TOKEN)







