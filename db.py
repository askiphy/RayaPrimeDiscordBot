import sqlite3

def get_cash(user_id):
	with sqlite3.connect("data.db") as db:
		cursor = db.cursor()

		cash = cursor.execute(f"SELECT cash FROM users WHERE id = {user_id}").fetchone()

		return cash[0]

def get_om(user_id):
	with sqlite3.connect("data.db") as db:
		cursor = db.cursor()

		om = cursor.execute(f"SELECT om FROM users WHERE id = {user_id}").fetchone()

		return om[0]

def add_cash(user_id, amount: int):
	with sqlite3.connect("data.db") as db:
		cursor = db.cursor()
		try:
			cash = cursor.execute(f"SELECT cash FROM users WHERE id = {user_id}").fetchone()
			cursor.execute(f"UPDATE users SET cash = {cash[0] + int(amount)} WHERE id = ?", [user_id])

			return True
		except:
			return False

def remove_cash(user_id, amount: int):
	with sqlite3.connect("data.db") as db:
		cursor = db.cursor()

		cash = cursor.execute(f"SELECT cash FROM users WHERE id = {user_id}").fetchone()
		if cash[0] < amount:
			return False
		cursor.execute(f"UPDATE users SET cash = {cash[0] - int(amount)} WHERE id = ?", [user_id])

		return True

def add_data(where: str, name: str, price: int):
	with sqlite3.connect("data.db") as db:
		cursor = db.cursor()

		if where == "emporium":
			if cursor.execute("SELECT item FROM shop WHERE item = ?", [name]).fetchone() is None:
				values = name, price
				cursor.executemany(f"INSERT INTO shop VALUES(?, ?)", [values])
				return True
			else:
				return False

		elif where == "raya":
			if cursor.execute("SELECT item FROM rshop WHERE item = ?", [name]).fetchone() is None:
				values = name, price
				cursor.executemany(f"INSERT INTO rshop VALUES(?, ?)", [values])
				return True
			else:
				return False

		elif where == "petshop":
			if cursor.execute("SELECT item FROM pets WHERE item = ?", [name]).fetchone() is None:
				values = name, price
				cursor.executemany(f"INSERT INTO pets VALUES(?, ?)", [values])
				return True
			else:
				return False

		elif where == "implantshop":
			if cursor.execute("SELECT item FROM implants WHERE item = ?", [name]).fetchone() is None:
				values = name, price
				cursor.executemany(f"INSERT INTO implants VALUES(?, ?)", [values])
				return True
			else:
				return False