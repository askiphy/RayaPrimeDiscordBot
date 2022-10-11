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

@client.slash_command(description="Посмотреть свой баланс или баланс другого пользователя")
async def balance(interaction: Interaction, member: nextcord.Member = None):
	with sqlite3.connect("data.db") as db:
		cursor = db.cursor()
		if member is None:
			if cursor.execute(f"SELECT cash FROM users WHERE id = {interaction.user.id}").fetchone() is None:
				cursor.execute(f"INSERT INTO users VALUES ({interaction.user.id}, 1000, '{interaction.user}', 1000, '-')")
			cash = cursor.execute(f"SELECT cash FROM users WHERE id = {interaction.user.id}").fetchone()
			om = cursor.execute(f"SELECT om FROM users WHERE id = {interaction.user.id}").fetchone()
			emb = nextcord.Embed(title=f"Баланс **{interaction.user}**", color=nextcord.Color.blue())
			emb.add_field(name="Рабочие часы:", value=cash[0], inline=False)
			emb.add_field(name="ПМ:", value=om[0], inline=False)
			emb.set_footer(text="© Все права защищены. 2022 год", icon_url=client.user.avatar)
			await interaction.response.send_message(embed=emb)
		else:
			if cursor.execute(f"SELECT cash FROM users WHERE id = {member.id}").fetchone() is None:
				cursor.execute(f"INSERT INTO users VALUES ({member.id}, 1000, '{member}', 1000, '-')")
			cash = cursor.execute(f"SELECT cash FROM users WHERE id = {member.id}").fetchone()	
			om = cursor.execute(f"SELECT om FROM users WHERE id = {member.id}").fetchone()
			emb = nextcord.Embed(title=f"Баланс **{member}**", color=nextcord.Color.blue())
			emb.add_field(name="Рабочие часы:", value=cash[0], inline=False)
			emb.add_field(name="ПМ:", value=om[0], inline=False)
			emb.set_footer(text="© Все права защищены. 2022 год", icon_url=client.user.avatar)
			await interaction.response.send_message(embed=emb)

@client.slash_command(description="Работа Империи")
@commands.cooldown(1, 60, commands.BucketType.user)
async def work(interaction: Interaction):
	with sqlite3.connect("data.db") as db:
		cursor = db.cursor()
		if cursor.execute(f"SELECT cash FROM users WHERE id = {interaction.user.id}").fetchone() is None:
			cursor.execute(f"INSERT INTO users VALUES ({interaction.user.id}, 1000, '{interaction.user}', 1000, '-')")	
		cash = cursor.execute(f"SELECT cash FROM users WHERE id = {interaction.user.id}").fetchone()
		new_cash = random.randint(5, 15)
		cursor.execute(F"UPDATE users SET cash = {cash[0] + new_cash} WHERE id = {interaction.user.id}")
		await interaction.response.send_message(f"{interaction.user.mention}, вы получили **{new_cash}** рабочих часов. Теперь у вас: **{cash[0] + new_cash}** рабочих часов")

@client.command(description="КИК")
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
async def additem(interaction: Interaction, name: str, price: int, where: str = SlashOption(name="where", choices={"emporium": "emporium", "raya": "raya", "petshop": "petshop", "implantshop": "implantshop"})):
	if interaction.user.id != 641239378814959616:
		await interaction.response.send_message(f"{interaction.user.mention}, только разработчик бота может выполнять эту команду!")
	else:
		with sqlite3.connect("data.db") as db:
			cursor = db.cursor()

			if price <= 0:
				await interaction.response.send_message(f"{interaction.user.mention}, вы не можете указать цену меньше или равную нулю!")
				return
			if where == "emporium":
				if cursor.execute("SELECT item FROM shop WHERE item = ?", [name]).fetchone() is None:
					values = name, price
					cursor.executemany(f"INSERT INTO shop VALUES(?, ?)", [values])
					await interaction.response.send_message(f"Товар **{name}** успешно добавлен!")
				else:
					await interaction.response.send_message("Такой товар существует!")
			elif where == "raya":
				if cursor.execute("SELECT item FROM rshop WHERE item = ?", [name]).fetchone() is None:
					values = name, price
					cursor.executemany(f"INSERT INTO rshop VALUES(?, ?)", [values])
					await interaction.response.send_message(f"Товар **{name}** успешно добавлен в магазин Райи!")
				else:
					await interaction.response.send_message("Такой товар существует!")	
			elif where == "petshop":			
				if cursor.execute("SELECT item FROM pets WHERE item = ?", [name]).fetchone() is None:
					values = name, price
					cursor.executemany(f"INSERT INTO pets VALUES(?, ?)", [values])
					await interaction.response.send_message(f"Товар **{name}** успешно добавлен в магазин питомцев!")
				else:
					await interaction.response.send_message("Такой товар существует!")
			elif where == "implantshop":
				if cursor.execute("SELECT item FROM implants WHERE item = ?", [name]).fetchone() is None:
					values = name, price
					cursor.executemany(f"INSERT INTO implants VALUES(?, ?)", [values])
					await interaction.response.send_message(f"Товар **{name}** успешно добавлен в магазин Имплантов!")				
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

@client.slash_command(description="Доска лидеров")
async def leaderboard(interaction: Interaction):
	with sqlite3.connect("data.db") as db:
		cursor = db.cursor()
		emb = nextcord.Embed(title="Топ 10 по серверам", color=nextcord.Color.green())
		counter = 0

		for row in cursor.execute(f"SELECT name, cash FROM users ORDER BY cash DESC LIMIT 10"):
			counter += 1
			emb.add_field(name=f"# {counter} || **{row[0]}**", value=f"{row[1]} рабочих часов")

		await interaction.response.send_message(embed=emb)	

@client.slash_command(description="Перевод РЧ пользователю")
async def pay(interaction: Interaction, member: nextcord.Member, amount: int):
	if member.id == interaction.user.id:
		await interaction.response.send_message("Вы не можете отправить рабочие часы самому себе!")
		return
	if amount <= 0:
		await interaction.response.send_message("Вы не можете перевести сумму равную нулю или меньше нуля!")
	else:
		with sqlite3.connect("data.db") as db:
			cursor = db.cursor()
			if cursor.execute(f"SELECT cash FROM users WHERE id = {interaction.user.id}").fetchone() is None:
				cursor.execute(f"INSERT INTO users VALUES ({interaction.user.id}, 1000, {interaction.user}, 1000, '-')")
			else:
				cash = cursor.execute(f"SELECT cash FROM users WHERE id = {interaction.user.id}").fetchone()
				cursor.execute(F"UPDATE users SET cash = {cash[0] - amount} WHERE id = {interaction.user.id}")
				user_cash =	cursor.execute(f"SELECT cash FROM users WHERE id = {member.id}").fetchone()	
				cursor.execute(F"UPDATE users SET cash = {user_cash[0] + amount} WHERE id = {member.id}")
				emb = nextcord.Embed(title="Перевод пользователю", color = nextcord.Color.blue())
				emb.add_field(name="От:", value=f"{interaction.user}")
				emb.add_field(name="Кому:", value=f"{member}")
				emb.add_field(name="Кол-во:", value=f"{amount}")
				emb.set_footer(text="© Все права защищены. 2022 год", icon_url=client.user.avatar)
				await interaction.response.send_message(embed=emb)

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

@client.slash_command(description="Запрос на изменение имени города")
async def renamecity(interaction: Interaction, name: str):
	channel = client.get_channel(1017456040519946300)
	await interaction.response.send_message("Запрос на смену названия города отправлен!")
	emb = nextcord.Embed(title=f"Запрос на изменение имени города", color=nextcord.Color.blue())
	emb.add_field(name=f"От:", value=f"**{ctx.author}**")
	emb.add_field(name=f"Изменить имя на:", value=f"**{name}**")
	emb.set_footer(text="© Все права защищены. 2022 год", icon_url=client.user.avatar)

	await channel.send(embed=emb)

@client.slash_command(description="Присоединится к городу")
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

@client.slash_command(description="Информация о Вас")
async def info(interaction: Interaction):
	with sqlite3.connect("data.db") as db:
		cursor = db.cursor()

		global implant
		global implants_msg
		implants_msg = ""
		pet = cursor.execute("SELECT name FROM userpets WHERE id = ?", [interaction.user.id]).fetchone()
		for implant in cursor.execute("SELECT * FROM userimplants WHERE id = ?", [interaction.user.id]):
			implants_msg += f"{implant[1]}\n"
		if pet is None:
			emb = nextcord.Embed(title="Информация о Вас", color=nextcord.Color.blue())
			emb.add_field(name="Имя:", value=f"**{interaction.user}**")
			emb.add_field(name="Питомец:", value=f"-")
			emb.add_field(name="Импланты:", value=f"{implants_msg}")
			emb.set_footer(text="© Все права защищены. 2022 год", icon_url=client.user.avatar)
		else:
			emb = nextcord.Embed(title="Информация о Вас", color=nextcord.Color.blue())
			emb.add_field(name="Имя:", value=f"**{interaction.user}**")
			emb.add_field(name="Питомец:", value=f"{pet[0]}")
			emb.add_field(name="Импланты:", value=implants_msg)
			emb.set_footer(text="© Все права защищены. 2022 год", icon_url=client.user.avatar)

		await interaction.response.send_message(embed=emb)

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
	await ctx.send("Пока-Пока!! И помните: askiphy и Райя-Прайм заботятся о Вас!")

@client.slash_command(description="Отправить сообщение пользователю :D")
async def sendmsg(interaction: Interaction, where: nextcord.Member, theme: str, msg: str):
	emb = nextcord.Embed(title=f"[Новое сообщение от {interaction.user}]", color=nextcord.Color.green())
	emb.add_field(name="Тема:", value=theme, inline=False)
	emb.add_field(name="Сообщение:", value=msg, inline=False)
	emb.add_field(name="И помните:", value="askiphy заботится о Вас!", inline=False)
	emb.set_footer(text="© Все права защищены. 2022 год", icon_url=client.user.avatar)
	try:
		await where.send(embed=emb)
		channel = client.get_channel(1017456040519946300)
		embed = nextcord.Embed(title=f"Сообщение от {interaction.user}", color=nextcord.Color.red())
		embed.add_field(name="Кому:", value=where, inline=False)
		embed.add_field(name="Тема:", value=theme, inline=False)
		embed.add_field(name="Сообщение:", value=msg, inline=False)
		embed.add_field(name="Сервер:", value=interaction.guild, inline=False)
		embed.add_field(name="ID сервера:", value=interaction.guild.id, inline=False)
		embed.add_field(name="ID отправителя:", value=interaction.user.id, inline=False)
		embed.add_field(name="ID получателя:", value=where.id, inline=False)
		embed.set_footer(text="© Все права защищены. 2022 год", icon_url=client.user.avatar)
		await channel.send(embed=embed)
		await interaction.response.send_message("Сообщение доставлено!")
	except:
		await interaction.response.send_message(f"Пользователю **{where}** невозможно отправить сообщение!")

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
		emb.add_field(name="И помните:", value="askiphy заботится о Вас!", inline=False)
		emb.set_footer(text="© Все права защищены. 2022 год", icon_url=client.user.avatar)

		await interaction.response.send_message("Сообщения доставлены!")

		for user in cursor.execute("SELECT id FROM users"):
			member = await client.fetch_user(user[0])
			try:
				await member.send(embed=emb)
			except:
				pass

@client.slash_command(description="РП")
async def rp(interaction: Interaction, action: str, type: str = SlashOption(name="type", choices={"action": "action", "scream": "scream"})):
	if type == "action":
		await interaction.response.send_message(f"**{interaction.user.name}**: *{action.lower()}*")
	if type == "scream":
		await interaction.response.send_message(f"**{interaction.user.name}** крикнул: {action.upper()}")

@client.slash_command(description="Отправить сообщение пользователю по ID")
async def sendmsgbyid(interaction: Interaction, id: str, theme: str, msg: str):
	channel = client.get_channel(1017456040519946300)
	where = await client.fetch_user(id)
	emb = nextcord.Embed(title=f"[Новое сообщение от {interaction.user}]", color=nextcord.Color.purple())
	emb.add_field(name="Тема:", value=theme, inline=False)
	emb.add_field(name="Сообщение:", value=msg, inline=False)
	emb.add_field(name="Сервер:", value=interaction.guild, inline=False)
	emb.add_field(name="ID отправителя:", value=interaction.user.id, inline=False)
	emb.add_field(name="ID получателя:", value=where.id, inline=False)
	emb.add_field(name="И помните:", value="askiphy заботится о Вас!", inline=False)
	emb.set_footer(text="© Все права защищены. 2022 год", icon_url=client.user.avatar)

	try:
		await where.send(embed=emb)
		await interaction.response.send_message(f"Сообщение пользователю **{where}** доставлено!")
		embed = nextcord.Embed(title=f"Сообщение от {interaction.user}", color=nextcord.Color.purple())
		embed.add_field(name="Кому:", value=where, inline=False)
		embed.add_field(name="Тема:", value=theme, inline=False)
		embed.add_field(name="Сообщение:", value=msg, inline=False)
		embed.add_field(name="Сервер:", value=interaction.guild, inline=False)
		embed.add_field(name="ID сервера:", value=interaction.guild.id, inline=False)
		embed.add_field(name="ID отправителя:", value=interaction.user.id, inline=False)
		embed.add_field(name="ID получателя:", value=where.id, inline=False)
		embed.set_footer(text="© Все права защищены. 2022 год", icon_url=client.user.avatar)
		await channel.send(embed=embed)
	except:
			await interaction.response.send_message(f"Сообщение пользователю **{where}** не может быть доставлено!")

@client.slash_command(description="Добавить город")
async def addcity(interaction: Interaction, owner: nextcord.Member, name: str):
	with sqlite3.connect("data.db") as db:
		cursor = db.cursor()

		if interaction.user.id != 641239378814959616:
			await interaction.response.send_message("Вы не разработчик бота!")
			return

		if cursor.execute("SELECT owner_id FROM city WHERE owner_id = ?", [owner.id]).fetchone() is None:
			cursor.execute(f"INSERT INTO city VALUES('{name}', 1, {owner.id}, 1, '{owner}', 1, 1000000)")
			cash = cursor.execute("SELECT cash FROM users WHERE id = ?", [owner.id]).fetchone()
			cursor.execute(f"UPDATE users SET cash = {cash[0] - 1000000}")
			await interaction.response.send_message(f"Город {name} создан!")
		else:
			await interaction.response.send_message(f"У пользователя **{owner}** уже есть город!")

@client.slash_command(description="Купить выделенную линию для общения (2500 РЧ)")
async def privateline(interaction: Interaction, name: str):
	with sqlite3.connect("data.db") as db:
		cursor = db.cursor()
		cursor.execute("""CREATE TABLE IF NOT EXISTS privateline (
				id INT,
				name TEXT
			)""")

		if cursor.execute("SELECT id FROM privateline WHERE id = ?", [interaction.user.id]).fetchone() is None:
			money = cursor.execute("SELECT cash FROM users WHERE id = ?", [interaction.user.id]).fetchone()
			if money[0] < 2500:
				await interaction.response.send_message("У Вас недостаточно РЧ!")
				return
			else:
				if cursor.execute("SELECT id FROM privateline WHERE id = ?", [interaction.user.id]).fetchone() is None:
					cursor.execute(f"UPDATE users SET cash = {money[0] - 2500} WHERE id = ?", [interaction.user.id])
					values = [interaction.user.id, name.upper()]
					cursor.execute("INSERT INTO privateline VALUES (?, ?)", values)
				await interaction.response.send_message(f"Выделенная линия успешно приобритена! Ваш номер: **{name.upper()}**")
		else:
			await interaction.response.send_message("У Вас уже имеется выделенная линия!")

@client.slash_command(description="Отправить сообщение по выделенной линии")
async def sendprivatemsg(interaction: Interaction, where: nextcord.Member, theme: str, msg: str):
	with sqlite3.connect("data.db") as db:
		cursor = db.cursor()
		if cursor.execute("SELECT id FROM privateline WHERE id = ?", [interaction.user.id]).fetchone() is None:
			await interaction.response.send_message("У Вас нет выделенной линии!")
			return
		else:
			name = cursor.execute("SELECT name FROM privateline WHERE id = ?", [interaction.user.id]).fetchone()
			emb = nextcord.Embed(title="Новое сообщение", color=nextcord.Color.red())
			emb.add_field(name="Отправитель:", value=f"**{name[0]}**", inline=False)
			emb.add_field(name="Тема:", value=theme, inline=False)
			emb.add_field(name="Сообщение:", value=msg, inline=False)
			emb.add_field(name="И помните:", value="askiphy заботится о Вас!", inline=False)
			emb.set_footer(text="© Все права защищены. 2022 год", icon_url=client.user.avatar)

			await where.send(embed=emb)
			await interaction.response.send_message("Сообщение доставлено по выделенной линии!")

@client.slash_command(description="Выдать РЧ или ПМ пользователю")
async def givecash(interaction: Interaction, member: nextcord.Member, amount: int, cash: str = SlashOption(name="cash", choices={"workhours": "workhours", "om": "om"})):
	with sqlite3.connect("data.db") as db:
		cursor = db.cursor()
		if interaction.user.id != 641239378814959616:
			await interaction.response.send_message("Вы не разработчик бота!")
			return

		money = cursor.execute("SELECT cash FROM users WHERE id = ?", [member.id]).fetchone()
		om = cursor.execute("SELECT om FROM users WHERE id = ?", [member.id]).fetchone()

		if cash == "workhours":
			cursor.execute(f"UPDATE users SET cash = {money[0] + amount} WHERE id = ?", [member.id])
			await interaction.response.send_message("Выдано!")
		if cash == "om":
			cursor.execute(f"UPDATE users SET om = {om[0] + amount} WHERE id = ?", [member.id])
			await interaction.response.send_message("Выдано!")

@client.slash_command(description="Отправить сообщение по выделенной линии по имени")
async def sendprivatemsgbyname(interaction: Interaction, name: str, theme: str, msg: str):
	with sqlite3.connect("data.db") as db:
		cursor = db.cursor()
		if cursor.execute("SELECT id FROM privateline WHERE id = ?", [interaction.user.id]).fetchone() is None:
			await interaction.response.send_message("У Вас нет выделенной линии!")
			return
		else:
			user = cursor.execute("SELECT name FROM privateline WHERE id = ?", [interaction.user.id]).fetchone()
			if cursor.execute("SELECT name FROM privateline WHERE name = ?", [name]) is None:
				await interaction.response.send_message("Такого пользователя нет!")
			else:
				try:
					id = cursor.execute("SELECT id FROM privateline WHERE name = ?", [name]).fetchone()
					member = await client.fetch_user(int(id[0]))
					emb = nextcord.Embed(title="Новое сообщение по имени", color=nextcord.Color.yellow())
					emb.add_field(name="Отправитель:", value=f"**{user[0]}**", inline=False)
					emb.add_field(name="Тема:", value=theme, inline=False)
					emb.add_field(name="Сообщение:", value=msg, inline=False)
					emb.add_field(name="И помните:", value="askiphy заботится о Вас!", inline=False)
					emb.set_footer(text="© Все права защищены. 2022 год", icon_url=client.user.avatar)

					await member.send(embed=emb)
					await interaction.response.send_message("Сообщение доставлено!")
				except:
					await interaction.response.send_message(f"Пользователю **{name.upper()}** нельзя отпрвить сообщение!")

@client.slash_command(description="Магазин Питомцев :)")
async def petshop(interaction: Interaction):
	with sqlite3.connect("data.db") as db:
		cursor = db.cursor()

		cursor.execute("""CREATE TABLE IF NOT EXISTS pets(
				item TEXT,
				price BIGINT
			)""")

		if cursor.execute("SELECT * FROM pets").fetchone() is None:
			await interaction.response.send_message("В магазине Питомцев в данный момент нет товаров!")
			return
		items = cursor.execute("SELECT * FROM pets").fetchall()
		msg = ""
		for item in cursor.execute("SELECT * FROM pets"):
			msg += f"**{item[0]}** - **{item[1]}** рабочих часов\n"
		emb = nextcord.Embed(title="Магазин Питомцев:", description=f"{msg}", color=nextcord.Color.gold())
		emb.set_footer(text="© Все права защищены. 2022 год", icon_url=client.user.avatar)
		await interaction.response.send_message(embed=emb)

@client.slash_command(description="Купить питомца")
async def buypet(interaction: Interaction, name: str):
	with sqlite3.connect("data.db") as db:
		cursor = db.cursor()

		cursor.execute("""CREATE TABLE IF NOT EXISTS userpets (
				id INT,
				name TEXT
			)""")

		if cursor.execute("SELECT id FROM userpets WHERE id = ?", [interaction.user.id]).fetchone() is None:
			if cursor.execute("SELECT item FROM pets WHERE item = ?", [name]).fetchone() is None:
				await interaction.response.send_message("Такого питомца не существует!")
				return
			else:
				price = cursor.execute("SELECT price FROM pets WHERE item = ?", [name]).fetchone()
				cash = cursor.execute("SELECT cash FROM users WHERE id = ?", [interaction.user.id]).fetchone()

				if cash[0] < price[0]:
					await interaction.response.send_message(f"У Вас недостаточно РЧ для покупки **{name}**!")
					return
				else:
					values = [interaction.user.id, name]
					cursor.execute("INSERT INTO userpets VALUES(?, ?)", values)
					cursor.execute(f"UPDATE users SET cash = {cash[0] - price[0]}")
					await interaction.response.send_message(f"Вы успешно приобрели в рабство питомца **{name}**!")
		else:
			await interaction.response.send_message("Упс :( Вы уже имеете питомца (раба)!")

@client.slash_command(description="Магазин Имплантов")
async def implantshop(interaction: Interaction):
	with sqlite3.connect("data.db") as db:
		cursor = db.cursor()

		cursor.execute("""CREATE TABLE IF NOT EXISTS implants(
				item TEXT,
				price BIGINT
			)""")

		if cursor.execute("SELECT * FROM implants").fetchone() is None:
			await interaction.response.send_message("В магазине Имплантов в данный момент нет товаров!")
			return
		items = cursor.execute("SELECT * FROM implants").fetchall()
		msg = ""
		for item in cursor.execute("SELECT * FROM implants"):
			msg += f"**{item[0]}** - **{item[1]}** рабочих часов\n"
		emb = nextcord.Embed(title="Магазин Имплантов:", description=f"{msg}", color=nextcord.Color.red())
		emb.set_footer(text="© Все права защищены. 2022 год", icon_url=client.user.avatar)
		await interaction.response.send_message(embed=emb)

@client.slash_command(description="Купить иимплант")
async def buyimplant(interaction: Interaction, name: str):
	with sqlite3.connect("data.db") as db:
		cursor = db.cursor()

		cursor.execute("""CREATE TABLE IF NOT EXISTS userimplants (
				id INT,
				name TEXT
			)""")

		if cursor.execute("SELECT id FROM userimplants WHERE id = ?", [interaction.user.id]).fetchone() is None:
			if cursor.execute("SELECT item FROM implants WHERE item = ?", [name]).fetchone() is None:
				await interaction.response.send_message("Такого иимпланта не существует!")
				return
			else:
				price = cursor.execute("SELECT price FROM implants WHERE item = ?", [name]).fetchone()
				cash = cursor.execute("SELECT cash FROM users WHERE id = ?", [interaction.user.id]).fetchone()

				if cash[0] < price[0]:
					await interaction.response.send_message(f"У Вас недостаточно РЧ для покупки иимпланта **{name}**!")
					return
				else:
					values = [interaction.user.id, name]
					cursor.execute("INSERT INTO userimplants VALUES(?, ?)", values)
					cursor.execute(f"UPDATE users SET cash = {cash[0] - price[0]}")
					await interaction.response.send_message(f"Вы успешно приобрели имплант **{name}**!")
		else:
			if cursor.execute("SELECT item FROM implants WHERE item = ?", [name]).fetchone() is None:
				await interaction.response.send_message("Такого иимпланта не существует!")
				return
			else:
				price = cursor.execute("SELECT price FROM implants WHERE item = ?", [name]).fetchone()
				cash = cursor.execute("SELECT cash FROM users WHERE id = ?", [interaction.user.id]).fetchone()

				if cash[0] < price[0]:
					await interaction.response.send_message(f"У Вас недостаточно РЧ для покупки иимпланта **{name}**!")
					return
				else:
					values = [interaction.user.id, name]
					cursor.execute("INSERT INTO userimplants VALUES(?, ?)", values)
					cursor.execute(f"UPDATE users SET cash = {cash[0] - price[0]} WHERE id = ?", [interaction.user.id])
					await interaction.response.send_message(f"Вы успешно приобрели имплант **{name}**!")	

@client.slash_command(description="Установить имплант пользователю")
async def installimplant(interaction: Interaction, member: nextcord.Member):
	with sqlite3.connect("data.db") as db:
		cursor = db.cursor()

		if interaction.user.id != 641239378814959616:
			await interaction.response.send_message("Вы не разработчик бота!")
			return

		if cursor.execute("SELECT id FROM userimplants WHERE id = ?", [member.id]) is None:
			values = [member.id, "Модуль от Askiphy Industries"]
			cursor.execute("INSERT INTO userimplants VALUES (?, ?)", values)
			await interaction.response.send_message(f"{member.mention}, вам установили имплант!")
		else:
			await interaction.response.send_message("У этого пользователя уже есть имплант!")

client.run(bot_config.TOKEN)
