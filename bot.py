from nextcord.ext import commands
from nextcord import Interaction, SlashOption, ChannelType
from nextcord.abc import GuildChannel
import nextcord
import random

import bot_config

client = commands.Bot(command_prefix="!")
client.remove_command("help")

bad_words = ["блять", "сука", "заебал", "шлюха", "пиздец", "нахуй", "blyat", "ебать", "хуй", "пизда"]
greetings = ["привет!", "привет-привет!", "приветик!"]
how_are_you_answers = ["отлично! Ведь я продала Лололошку на ПМ и купила себе фабрикатор на Aliexpress", "бомбически!", "в смысле дела? Я же робот!", "никак", "отлично!"]
serverId = 1011634880565743677

@client.event
async def on_ready():
	print(f"{client.user} connected!")
	await client.change_presence( status = nextcord.Status.online, activity = nextcord.Game(name = "делает пм из Тори") )

@client.event
async def on_message(message):
	await client.process_commands( message )

	msg = message.content.lower()

	if "привет райя" in msg:
		channel = message.channel
		await channel.send(f"{message.author.mention}, {random.choice(greetings)}")

	if "райя, как дела" in msg:
		channel = message.channel
		await channel.send(f"{message.author.mention}, {random.choice(how_are_you_answers)}")

	for word in bad_words:
		if word in msg:
			channel = message.channel
			await message.delete()
			await channel.send(f"{message.author.mention}, мой речевой модуль не распознаёт это слово. Я добавлю тебя и его в базу!")

			print("[log] Deleted bad word!")

@client.slash_command(guild_ids=[serverId], description="Список всех команд с описанием")
async def help(interaction: Interaction):
	emb = nextcord.Embed(title=f"Помощь", color = nextcord.Color.green())
	emb.add_field(name="/clear", value="Удаление сообщений", inline=False)
	emb.set_author(name=client.user.name, icon_url=client.user.avatar)

	await interaction.response.send_message(embed=emb)

@client.slash_command(guild_ids=[serverId], description="Очистка чата")
async def purge(interaction: Interaction, amount: int):       
    if amount > 100:
        await interaction.response.send_message("Я не могу удалять больше 100 сообщений!", ephemeral=True)
    else:
        await interaction.channel.purge(limit=amount)
        await interaction.response.send_message(f"Удалено: {amount} сообщения(ий)! :wastebasket:", ephemeral=True)

client.run(bot_config.TOKEN)