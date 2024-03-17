import discord
from env import TOKEN

intents = discord.Intents.all()
intents.message_content = True

client = discord.Client(intents = intents)




client.run(TOKEN)







