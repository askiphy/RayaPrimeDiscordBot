from nextcord.ext import commands
from nextcord import Interaction, SlashOption, ChannelType, ButtonStyle
from nextcord.abc import GuildChannel
from nextcord.ui import Button, View
import nextcord
import random
import requests

import bot_config
import sqlite3
import json

client = commands.Bot(command_prefix=bot_config.PREFIX)
client.remove_command("help")

bad_words = ["блять", "сука", "заебал", "шлюха", "пиздец", "нахуй", "blyat", "ебать", "хуй", "пизда", "ахуел"]
link = ["https", "https", ".gg", ".com", "://", ".ru", ".рф"]
greetings = ["привет!", "привет-привет!", "приветик!"]
how_are_you_answers = ["отлично! Ведь я продала Лололошку на ПМ и купила себе фабрикатор на Aliexpress", "бомбически!", "в смысле дела? Я же робот!", "никак", "отлично!"]
question_answers = ["а ты", "да ну", "разве"]
raya_answers = ["го", "давай", "конечно", "нет.", "не могу", "давай потом"]
serverId = 1011634880565743677
helpGuide = json.load(open("help.json"))

@client.event
async def on_ready():
	channel = client.get_channel(1012683077102874644)
	print(f"{client.user} connected!")
	await client.change_presence( status = nextcord.Status.online, activity = nextcord.Game(name = f"мой префикс: {bot_config.PREFIX}") )
	await channel.send("Инициализация модуля П.Е.Р.С.И.К... Модуль успешно запущен!")
	with sqlite3.connect("data.db") as db:
		cursor = db.cursor()

		cursor.execute("""CREATE TABLE IF NOT EXISTS users (
				id INT,
				cash BIGINT,
				name TEXT,
				om BIGINT,
				city TEXT
			)""")

		for guild in client.guilds:
			for member in guild.members:
				if cursor.execute(f"SELECT id FROM users WHERE id = {member.id}").fetchone() is None:
					cursor.execute(f"INSERT INTO users VALUES ({member.id}, 1000, '{member}', 1000, '-')")
				else:
					pass

@client.event
async def on_message(message):
	await client.process_commands( message )

	msg = message.content.lower()

	if message.author.id == 1011634458048335883:
		return

	if "райя го" in msg:
		channel = message.channel
		await channel.send(f"{message.author.mention}, {random.choice(raya_answers)}")


	if "райя," in msg:
		channel = message.channel
		await channel.send(f"{message.author.mention}, {random.choice(question_answers)}")

	if "привет райя" in msg:
		channel = message.channel
		await channel.send(f"{message.author.mention}, {random.choice(greetings)}")

	if "райя как жизнь" in msg:
		channel = message.channel
		await channel.send(f"{message.author.mention}, {random.choice(how_are_you_answers)}")

	if "райя как дела" in msg:
		channel = message.channel
		await channel.send(f"{message.author.mention}, {random.choice(how_are_you_answers)}")

	for word in bad_words:
		if word in msg:
			channel = message.channel
			if message.author.id == 641239378814959616:
				return
			await message.delete()
			await channel.send(f"{message.author.mention}, мой речевой модуль не распознаёт это слово. Я добавлю тебя и его в базу!")

			print("[log] Deleted bad word!")

	for word in link:
		if word in msg:
			channel = message.channel
			if message.author.id == 641239378814959616:
				return
			await message.delete()
			await channel.send(f"{message.author.mention}, мой речевой модуль не распознаёт эту ссылку. Поэтому я удалю её :D")

@client.event
async def on_member_join(member):
	ctx.send(f"{member.mention}, добро пожаловать на завод по производству ПМ :D")

@client.event
async def on_command_error(ctx, error):
	if isinstance(error, commands.CommandOnCooldown):
		msg = f"Подождите {error.retry_after:.2f} секунд"
		await ctx.send(msg)

def createHelpEmbed(pageNum=0, inline=False):
	pageNum = pageNum % len(list(helpGuide))
	pageTitle = list(helpGuide)[pageNum]
	emb = nextcord.Embed(title=pageTitle, color = nextcord.Color.green(), description=f"Страница {pageNum+1}/{len(list(helpGuide))}")
	for key, val in helpGuide[pageTitle].items():
		emb.add_field(name=key, value=val, inline=inline)
		emb.set_author(name=client.user.name, icon_url=client.user.avatar)
		emb.set_footer(text="© Все права защищены. 2022 год", icon_url=client.user.avatar)
	return emb

@client.slash_command(description="Список всех команд с описанием")
async def help(interaction: Interaction):
	currentPage = 0

	async def next_callback(interaction):
		nonlocal currentPage
		currentPage += 1
		await interaction.response.edit_message(embed=createHelpEmbed(pageNum=currentPage), view=view)

	async def previous_callback(interaction):
		nonlocal currentPage
		currentPage -= 1
		await interaction.response.edit_message(embed=createHelpEmbed(pageNum=currentPage), view=view)		

	nextButton = Button(label=">>", style=ButtonStyle.blurple)
	nextButton.callback = next_callback
	previousButton = Button(label="<<", style=ButtonStyle.blurple)
	previousButton.callback = previous_callback

	view = View(timeout=180)
	view.add_item(previousButton)
	view.add_item(nextButton)
	msg = await interaction.response.send_message(embed=createHelpEmbed(), view=view)

@client.slash_command(description="Фото с собачкой)")
async def dog(interaction: Interaction):
	response = requests.get("https://dog.ceo/api/breeds/image/random")
	image_link = response.json()["message"]
	emb = nextcord.Embed(title="Собачка", color=nextcord.Color.blue())
	emb.set_image(url=image_link)
	emb.set_author(name=client.user.name, icon_url=client.user.avatar)
	emb.set_footer(text="© Все права защищены. 2022 год", icon_url=client.user.avatar)	
	await interaction.response.send_message(embed=emb)

@client.slash_command(guild_ids=[serverId], description="Очистка чата")
@commands.has_permissions( administrator = True )
async def purge(interaction: Interaction, amount: int):       
    if amount > 100:
        await interaction.response.send_message("Я не могу удалять больше 100 сообщений!", ephemeral=True)
    else:
        await interaction.channel.purge(limit=amount)
        await interaction.response.send_message(f"Удалено: {amount} сообщения(ий)! :wastebasket:", ephemeral=True)

@client.command(aliases=["bal"])
async def balance(ctx, member: nextcord.Member = None):
	with sqlite3.connect("data.db") as db:
		cursor = db.cursor()
		if member is None:
			if cursor.execute(f"SELECT cash FROM users WHERE id = {ctx.author.id}").fetchone() is None:
				cursor.execute(f"INSERT INTO users VALUES ({ctx.author.id}, 1000, '{ctx.author}', 1000, '-')")
			cash = cursor.execute(f"SELECT cash FROM users WHERE id = {ctx.author.id}").fetchone()
			om = cursor.execute(f"SELECT om FROM users WHERE id = {ctx.author.id}").fetchone()
			emb = nextcord.Embed(title=f"Баланс **{ctx.author}**", color=nextcord.Color.blue())
			emb.add_field(name="Рабочие часы:", value=cash[0], inline=False)
			emb.add_field(name="ПМ:", value=om[0], inline=False)
			emb.set_footer(text="© Все права защищены. 2022 год", icon_url=client.user.avatar)
			await ctx.send(embed=emb)
		else:
			if cursor.execute(f"SELECT cash FROM users WHERE id = {member.id}").fetchone() is None:
				cursor.execute(f"INSERT INTO users VALUES ({member.id}, 1000, '{member}', 1000, '-')")
			cash = cursor.execute(f"SELECT cash FROM users WHERE id = {member.id}").fetchone()	
			om = cursor.execute(f"SELECT om FROM users WHERE id = {ctx.author.id}").fetchone()
			emb = nextcord.Embed(title=f"Баланс **{member}**", color=nextcord.Color.blue())
			emb.add_field(name="Рабочие часы:", value=cash[0], inline=False)
			emb.add_field(name="ПМ:", value=om[0], inline=False)
			emb.set_footer(text="© Все права защищены. 2022 год", icon_url=client.user.avatar)
			await ctx.send(embed=emb)

@client.command()
@commands.cooldown(1, 60, commands.BucketType.user)
async def work(ctx):
	with sqlite3.connect("data.db") as db:
		cursor = db.cursor()
		if cursor.execute(f"SELECT cash FROM users WHERE id = {ctx.author.id}").fetchone() is None:
			cursor.execute(f"INSERT INTO users VALUES ({ctx.author.id}, 1000, '{ctx.author}', 1000, '-')")	
		cash = cursor.execute(f"SELECT cash FROM users WHERE id = {ctx.author.id}").fetchone()
		new_cash = random.randint(5, 15)
		cursor.execute(F"UPDATE users SET cash = {cash[0] + new_cash} WHERE id = {ctx.author.id}")
		await ctx.send(f"{ctx.author.mention}, вы получили **{new_cash}** рабочих часов. Теперь у вас: **{cash[0] + new_cash}** рабочих часов")

@client.command()
@commands.has_permissions( administrator = True )
async def kick(ctx, *, member: nextcord.Member, reason: str):
	await member.kick(reason=reason)
	try:
		await member.send(f"Вы были превращены в ПМ по причине: **{reason}**")
	except:
		pass
	await ctx.send(f"Ура-ура! Я превратила {member.name} в ПМ по причине: **{reason}**!")

@client.slash_command(description="Магазин Эмпориума")
async def shop(interaction: Interaction):
	with sqlite3.connect("data.db") as db:
		cursor = db.cursor()

		cursor.execute("""CREATE TABLE IF NOT EXISTS shop(
				item TEXT,
				price BIGINT
			)""")

		if cursor.execute("SELECT * FROM shop").fetchone() is None:
			await interaction.response.send_message("В магазине Эмпориума в данный момент нет товаров!")
			return
		items = cursor.execute("SELECT * FROM shop").fetchall()
		msg = ""
		for item in cursor.execute("SELECT * FROM shop"):
			msg += f"**{item[0]}** - **{item[1]}** рабочих часов\n"
		emb = nextcord.Embed(title="Магазин Эмпориума:", description=f"{msg}", color=nextcord.Color.blue())
		emb.set_footer(text="© Все права защищены. 2022 год", icon_url=client.user.avatar)
		await interaction.response.send_message(embed=emb)

@client.slash_command(description="Добавить товар в магазин")
async def additem(interaction: Interaction, where: str, name: str, price: int):
	if interaction.user.id != 641239378814959616:
		await interaction.response.send_message(f"{interaction.user.mention}, только разработчик бота может выполнять эту команду!")
	else:
		with sqlite3.connect("data.db") as db:
			cursor = db.cursor()

			if price <= 0:
				await interaction.response.send_message(f"{interaction.user.mention}, вы не можете указать цену меньше или равную нулю!")
				return
			if where == "эмпориум":
				if cursor.execute("SELECT item FROM shop WHERE item = ?", [name]).fetchone() is None:
					values = name, price
					cursor.executemany(f"INSERT INTO shop VALUES(?, ?)", [values])
					await interaction.response.send_message(f"Товар **{name}** успешно добавлен!")
				else:
					await interaction.response.send_message("Такой товар существует!")
			elif where == "райя":
				if cursor.execute("SELECT item FROM rshop WHERE item = ?", [name]).fetchone() is None:
					values = name, price
					cursor.executemany(f"INSERT INTO rshop VALUES(?, ?)", [values])
					await interaction.response.send_message(f"Товар **{name}** успешно добавлен в магазин Райи!")
				else:
					await interaction.response.send_message("Такой товар существует!")				

@client.slash_command(description="Удалить товар из магазина")
async def removeitem(interaction: Interaction, name: str, where: str):
	if interaction.user.id != 641239378814959616:
		await interaction.response.send_message(f"{interaction.user.mention}, только разработчик бота может выполнять эту команду!")
	else:
		with sqlite3.connect("data.db") as db:
			cursor = db.cursor()
			if cursor.execute(f"SELECT item FROM {where} WHERE item = ?", [name]).fetchone() is None:
				await interaction.response.send_message(f"Товара с именем **{name}** не существует!")
			else:
				cursor.execute(f"DELETE FROM {where} WHERE item = ?", [name])
				await interaction.response.send_message(f"Товар **{name}** успешно удалён!")

@client.command(aliases=["lb"])
async def leaderboard(ctx):
	with sqlite3.connect("data.db") as db:
		cursor = db.cursor()
		emb = nextcord.Embed(title="Топ 10 по серверам", color=nextcord.Color.green())
		counter = 0

		for row in cursor.execute(f"SELECT name, cash FROM users ORDER BY cash DESC LIMIT 10"):
			counter += 1
			emb.add_field(name=f"# {counter} || **{row[0]}**", value=f"{row[1]} рабочих часов")

		await ctx.send(embed=emb)	

@client.command()
async def pay(ctx, member: nextcord.Member = None, amount: int = None):
	if member is None:
		await ctx.send(f"{ctx.author.mention}, укажите пользователя!")
	if member.id == ctx.author.id:
		await ctx.send("Вы не можете отправить рабочие часы самому себе!")
		return
	if amount is None:
		await ctx.send(f"{ctx.author.mention}, укажите сумму рабочих часов для перевода!")
	if amount <= 0:
		await ctx.send("Вы не можете перевести сумму равную нулю или меньше нуля!")
	else:
		with sqlite3.connect("data.db") as db:
			cursor = db.cursor()
			if cursor.execute(f"SELECT cash FROM users WHERE id = {ctx.author.id}").fetchone() is None:
				cursor.execute(f"INSERT INTO users VALUES ({ctx.author.id}, 1000, {ctx.author}, 1000, '-')")
			else:
				cash = cursor.execute(f"SELECT cash FROM users WHERE id = {ctx.author.id}").fetchone()
				cursor.execute(F"UPDATE users SET cash = {cash[0] - amount} WHERE id = {ctx.author.id}")
				user_cash =	cursor.execute(f"SELECT cash FROM users WHERE id = {member.id}").fetchone()	
				cursor.execute(F"UPDATE users SET cash = {user_cash[0] + amount} WHERE id = {member.id}")
				emb = nextcord.Embed(title="Перевод пользователю", color = nextcord.Color.blue())
				emb.add_field(name="От:", value=f"{ctx.author}")
				emb.add_field(name="Кому:", value=f"{member}")
				emb.add_field(name="Кол-во:", value=f"{amount}")
				emb.set_footer(text="© Все права защищены. 2022 год", icon_url=client.user.avatar)
				await ctx.send(embed=emb)

@client.command()
async def convert(ctx, value: str = None, amount: int = None):
	with sqlite3.connect("data.db") as db:
		cursor = db.cursor()

		if value is None:
			await ctx.send(f"{ctx.author.mention}, введите валюту в которую вы желаете перевести! (Валюта: ПМ, РЧ | Курс: 2 рабочих часа - 1ПМ, 25ПМ - 2 рабочих часа)")
			return
		if amount is None:
			await ctx.send(f"{ctx.author.mention}, введите сумму для конвертации! (2 рабочих часа - 1ПМ, 25ПМ - 2 рабочих часа)")
			return
		if amount <= 0:
			await ctx.send(f"{ctx.author.mention}, нельзя конвертировать сумму равную нулю или меньше нуля!")
			return
		if value == "ПМ":
			cash = cursor.execute(f"SELECT cash FROM users WHERE id = {ctx.author.id}").fetchone()
			om = cursor.execute(f"SELECT om FROM users WHERE id = {ctx.author.id}").fetchone()
			if cash[0] < amount:
				await ctx.send(f"{ctx.author.mention}, у вас недостаточно средств для конвертации в ПМ!")
				return
			cursor.execute(f"UPDATE users SET cash = {cash[0] - amount}")
			cursor.execute(f"UPDATE users SET om = {om[0] + amount}")
			emb = nextcord.Embed(title="Конвертация валюты", color=nextcord.Color.blue())
			emb.add_field(name="Конвертация в:", value="ПМ")
			emb.add_field(name="Преобразовала в:", value=f"{amount}ПМ")
			emb.set_footer(text="© Все права защищены. 2022 год", icon_url=client.user.avatar)

			await ctx.send(embed=emb)
		if value == "РЧ":
			cash = cursor.execute(f"SELECT cash FROM users WHERE id = {ctx.author.id}").fetchone()
			om = cursor.execute(f"SELECT om FROM users WHERE id = {ctx.author.id}").fetchone()
			if om[0] < amount:
				await ctx.send(f"{ctx.author.mention}, у вас недостаточно средств для конвертации в Рабочие часы!")
				return
			cursor.execute(f"UPDATE users SET cash = {cash[0] + amount} WHERE id = {ctx.author.id}")
			cursor.execute(f"UPDATE users SET om = {om[0] - 25 * amount} WHERE id = {ctx.author.id}")
			emb = nextcord.Embed(title="Конвертация валюты", color=nextcord.Color.blue())
			emb.add_field(name="Конвертация в:", value="Рабочие часы")
			emb.add_field(name="Преобразовала в:", value=f"{amount} рабочих часа")
			emb.set_footer(text="© Все права защищены. 2022 год", icon_url=client.user.avatar)

			await ctx.send(embed=emb)

@client.slash_command(description="Магазинчик Райи")
async def rshop(interaction: Interaction):
	with sqlite3.connect("data.db") as db:
		cursor = db.cursor()

		cursor.execute("""CREATE TABLE IF NOT EXISTS rshop(
				item TEXT,
				price BIGINT
			)""")

		if cursor.execute("SELECT * FROM rshop").fetchone() is None:
			await interaction.response.send_message("В магазине Райи в данный момент нет товаров!")
			return
		items = cursor.execute("SELECT * FROM rshop").fetchall()
		msg = ""
		for item in cursor.execute("SELECT * FROM rshop"):
			msg += f"**{item[0]}** - {item[1]}ПМ\n"
		emb = nextcord.Embed(title="loloshkashop.net", description=msg, color=nextcord.Color.blue())
		emb.set_footer(text="© Все права защищены. 2022 год", icon_url=client.user.avatar)
		await interaction.response.send_message(embed=emb)

@client.slash_command(description="Выпустить информацию о обновлении бота")
async def update(interaction: Interaction, version: str, description: str):
	if interaction.user.id != 641239378814959616:
		await interaction.response.send_message(f"{interaction.user.mention}, вы не разработчик бота!")
	else:
		emb = nextcord.Embed(title=f"Обновление **v{version}**", description=description, color=nextcord.Color.blue())
		emb.set_footer(text="© Все права защищены. 2022 год", icon_url=client.user.avatar)
		await interaction.response.send_message(embed=emb)

@client.command()
async def city(ctx, name: str = None, member: nextcord.Member = None):
	with sqlite3.connect("data.db") as db:
		cursor = db.cursor()

		cursor.execute("""CREATE TABLE IF NOT EXISTS city (
				name TEXT,
				lvl INT,
				owner_id INT,
				villagers BIGINT,
				owner_name TEXT,
				buildings BIGINT,
				cash BIGINT
			)""")
		if cursor.execute(f"SELECT owner_id FROM city WHERE owner_id = {ctx.author.id}").fetchone() is None:
			if cursor.execute(f"SELECT cash FROM users WHERE id = {ctx.author.id}").fetchone()[0] < 1000000:
				await ctx.send(f"{ctx.author.mention}, вам не хватает средств для создания города! Необходимо 1000000 рабочих часов!")
				return
			else:
				if name is None:
					await ctx.send(f"{ctx.author.mention}, укажите название города для создания!")

				cash = cursor.execute(f"SELECT cash FROM users WHERE id = {ctx.author.id}").fetchone() 
				cursor.execute(f"UPDATE users SET cash = {cash[0] - 1000000}")

				values = [name, 1, ctx.author.id, 1, ctx.author, 1, 1000000]
				cursor.execute(f"INSERT INTO city VALUES(?, ?, ?, ?, ?, ?, ?)", values)

				emb = nextcord.Embed(title="Новый город", color=nextcord.Color.blue())
				emb.add_field(name="Владелец города:", value=f"{ctx.author}")
				emb.add_field(name="Название города:", value=f"{name}")
				emb.set_footer(text="© Все права защищены. 2022 год", icon_url=client.user.avatar)

				await ctx.send(embed=emb)
		else:
			if member is None:
				city = cursor.execute(f"SELECT * FROM city WHERE owner_id = {ctx.author.id}").fetchone()
				emb = emb = nextcord.Embed(title="Информация о городе", color=nextcord.Color.blue())
				emb.add_field(name="Владелец города:", value=f"**{city[4]}**")
				emb.add_field(name="Название города:", value=f"**{city[0]}**")
				emb.add_field(name="Уровень города:", value=f"{city[1]}")
				emb.add_field(name="Кол-во жителей:", value=f"{city[3]}")
				emb.add_field(name="Кол-во зданий:", value=f"{city[5]}")
				emb.add_field(name="Бюджет города:", value=f"{city[6]}")
				emb.set_footer(text="© Все права защищены. 2022 год", icon_url=client.user.avatar)
			else:
				if cursor.execute(f"SELECT * FROM city WHERE owner_id = {member.id}").fetchone() is None:
					await ctx.send("Данный пользователь не имеет город!")
				else:
					city = cursor.execute(f"SELECT * FROM city WHERE owner_id = {member.id}").fetchone()
					emb = emb = nextcord.Embed(title="Информация о городе", color=nextcord.Color.blue())
					emb.add_field(name="Владелец города:", value=f"**{city[4]}**")
					emb.add_field(name="Название города:", value=f"**{city[0]}**")
					emb.add_field(name="Уровень города:", value=f"{city[1]}")
					emb.add_field(name="Кол-во жителей:", value=f"{city[3]}")
					emb.add_field(name="Кол-во зданий:", value=f"{city[5]}")
					emb.add_field(name="Бюджет города:", value=f"{city[6]}")
					emb.set_footer(text="© Все права защищены. 2022 год", icon_url=client.user.avatar)				

			await ctx.send(embed=emb)

@client.command()
async def renamecity(ctx, name: str = None):
	channel = client.get_channel(1017456040519946300)
	await ctx.send("Запрос на смену названия города отправлен!")
	emb = nextcord.Embed(title=f"Запрос на изменение имени города", color=nextcord.Color.blue())
	emb.add_field(name=f"От:", value=f"**{ctx.author}**")
	emb.add_field(name=f"Изменить имя на:", value=f"**{name}**")
	emb.set_footer(text="© Все права защищены. 2022 год", icon_url=client.user.avatar)

	await channel.send(embed=emb)

@client.slash_command()
async def join(interaction: Interaction, owner: nextcord.Member):
	with sqlite3.connect("data.db") as db:
		cursor = db.cursor()
		if cursor.execute(f"SELECT city FROM users WHERE id = {interaction.user.id}").fetchone() == cursor.execute(f"SELECT name FROM city WHERE owner_id = {owner.id}").fetchone():
			await interaction.response.send_message(f"{interaction.user.mention}, вы уже находитесь в этом городе!")
			return
		if cursor.execute(f"SELECT name FROM city WHERE owner_id = {owner.id}") is None:
			await interaction.response.send_message(f"{interaction.user.mention}, у этого пользователя нет города!")
			return
		name = cursor.execute(f"SELECT name FROM city WHERE owner_id = {owner.id}").fetchone()
		villagers = cursor.execute(f"SELECT villagers FROM city WHERE owner_id = {owner.id}").fetchone()
		values = [name[0], interaction.user.id]
		cursor.execute(f"UPDATE users SET city = ? WHERE id = ?", values)
		cursor.execute(f"UPDATE city SET villagers = {villagers[0] + 1}")
		await interaction.response.send_message(f"{interaction.user.mention}, вы успешно присоединились к **{name[0]}**!")

@client.command()
async def info(ctx):
	with sqlite3.connect("data.db") as db:
		cursor = db.cursor()
		city = cursor.execute("SELECT city FROM users WHERE id = ?", ctx.author.id).fetchone()[0]
		emb = nextcord.Embed(title="Информация о вас", color=nextcord.Color.blue())
		emb.add_field(name="Имя:", value=f"**{ctx.author}**")
		emb.add_field(name="Город:", value=f"**{city}**")
		emb.set_footer(text="© Все права защищены. 2022 год", icon_url=client.user.avatar)

		await ctx.send(embed=emb)

@client.slash_command(description="Управление Вашим городом")
async def citycontrol(interaction: Interaction):
	with sqlite3.connect("data.db") as db:
		cursor = db.cursor()

		async def upgrade_callback(interaction):
			channel = client.get_channel(1017456040519946300)
			lvl = cursor.execute(f"SELECT lvl FROM city WHERE owner_id = {interaction.user.id}").fetchone()
			name = cursor.execute(f"SELECT name FROM city WHERE owner_id = {interaction.user.id}").fetchone()
			await interaction.response.send_message(f"Запрос на улучшение города **{name[0]}** до уровня **{lvl[0] + 1}** отправлен!")
			await channel.send(f"Запрос на улучшение города **{name[0]}** до уровня **{lvl[0] + 1}**")

		upgradeButton = Button(label="Улучшить город", style=ButtonStyle.blurple)
		upgradeButton.callback = upgrade_callback

		view = View(timeout=180)
		view.add_item(upgradeButton)
		await interaction.response.send_message("Управление Вашим городом:", view=view)

@client.command()
async def msg(ctx, msg: str):
	if ctx.author.id == 641239378814959616:
		print(msg)

@client.command()
async def off(ctx):
	await ctx.send("@everyone Пока-Пока!! И помните: askiphy и Райя-Прайм заботятся о Вас!")

@client.slash_command(description="Отправить сообщение пользователю :D")
async def sendmsg(interaction: Interaction, where: nextcord.Member, theme: str, msg: str):
	emb = nextcord.Embed(title=f"[Новое сообщение от {interaction.user}]", color=nextcord.Color.green())
	emb.add_field(name="Тема:", value=theme, inline=False)
	emb.add_field(name="Сообщение:", value=msg, inline=False)
	emb.set_footer(text="© Все права защищены. 2022 год", icon_url=client.user.avatar)
	await interaction.response.send_message("Сообщение доставлено!")

	await where.send(embed=emb)

@client.slash_command(description="Разослать всем сообщение от имени Империи")
async def sendnews(interaction: Interaction, theme: str, msg: str):
	with sqlite3.connect("data.db") as db:
		cursor = db.cursor()
		if interaction.user.id != 641239378814959616:
			await interaction.response.send_message("Вы не разработчик бота!")
			return
		emb = nextcord.Embed(title="[Оповещение Аллотеры]", color=nextcord.Color.blue())
		emb.add_field(name="Отправитель:", value="Аллотера", inline=False)
		emb.add_field(name="Тема:", value=theme, inline=False)
		emb.add_field(name="Сообщение:", value=msg, inline=False)

		cursor.execute("SELECT id FROM users").fetchone()
		await interaction.response.send_message("Сообщения доставлены!")

client.run(bot_config.TOKEN)