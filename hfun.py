import sqlite3
from datetime import datetime 
from prettytable import PrettyTable

def starter(conn, cur) : 
	cur.executescript('''
	CREATE TABLE IF NOT EXISTS Foodtype (
	id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
	name TEXT UNIQUE,
	factor REAL
	);

	CREATE TABLE IF NOT EXISTS Dates (
	id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
	keydate TEXT UNIQUE,
	day INTEGER, 
	month TEXT, 
	year INTEGER, 
	total INTEGER NOT NULL, 
	status INTEGER,
	user_id INTEGER
	);

	CREATE TABLE IF NOT EXISTS Eating (
	user_id INTEGER,
	mass REAL,
	calories REAL,
	dates_id 	INTEGER,
	foodtype_id INTEGER
	);

	CREATE TABLE IF NOT EXISTS User (
	id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
	name TEXT,
	weight INTEGER,
	growth INTEGER,
	age INTEGER,
	gender TEXT,
	cindex INTEGER,
	bmi REAL,
	lifestyle TEXT,
	goal TEXT
	)

	''')
	conn.commit()
	return()

def user_detect(conn, cur) :
	user_name = input('Lets login! ').lower()

	cur.execute('SELECT id FROM User WHERE name = ? ', (user_name, ))
	try: 
		askname = cur.fetchone()[0]
		return(askname)
	except: 
		add_user(conn, cur)

def add_user(conn, cur) :
	print("\nLet's get acquainted!")
	nname = input('Please enter your name: ').lower()

	while True :
		ngender = input('What is your gender? Male or Female? Just write M or F: ').lower()
		if ngender == 'm' or ngender == 'f' : 
			break
		else : print('Please, try again:) ')
	
	while True:
		try:
			nweight = int(input('Your weight, without dot: '))
			break
		except: 
			print('Wrong weight, please try again')
			continue

	while True:
		try:
			ngrowth = int(input('Your growth, without dot: '))
			break
		except: 
			print('Wrong growth, please try again')
			continue

	while True:
		try:
			nage = int(input('How old are you? '))
			print(' ')
			break
		except: 
			print('Wrong age, please try again')
			continue

	while True :
		lifestyle = input('You are: active/normal/passive ? ').lower()
		if lifestyle == 'active' or lifestyle == 'normal' or lifestyle == 'passive' :
			break
		else : print('Please, try again')

	while True :
		goal = input('Your weight shuold be: less/same/more ? ').lower()
		if goal == 'less' or goal == 'same' or goal == 'more' :
			print(' ')
			break
		else : print('Please, try again')

	BMI = det_bmi(nweight, ngrowth)
	print('Your BMI is', BMI)

	cindex = det_cindex(nweight, ngrowth, nage, lifestyle, goal, ngender)
	print('Your calories limit per day:', cindex)

	cur.execute('''INSERT OR IGNORE INTO User (name, weight, growth, age, gender, cindex, bmi, lifestyle, goal)
		VALUES ( ?, ?, ?, ?, ?, ?, ?, ?, ? )''', ( nname, nweight, ngrowth, nage, ngender, cindex, BMI, lifestyle, goal ))
	conn.commit()
	print('\n******************************************************')

	return()

def new_foodtype_data(conn, cur) : 
	print("Enter new type of food and factor (Newtype|factor), if you don't want to continue, just enter")
	while True:
		value = input('>')
		if len(value) < 1 : break
		try :
			keys = value.split('|')
			ntype = keys[0].lower()
			nfactor = keys[1].lower()
			if type(nfactor) == 'str' :
				print('Wrong data')
				continue
			nfactor = float(nfactor)
		except :
			print('Wrong data')
			continue

		cur.execute('''INSERT OR IGNORE INTO Foodtype (name, factor)
		VALUES ( ?, ? )''', ( ntype, nfactor ))

		conn.commit()

	return()

def detectmonth(month):
	if month == 1 : return('January')
	elif month == 2 : return('February')
	elif month == 3 : return('March')
	elif month == 4 : return('April')
	elif month == 5 : return('May')
	elif month == 6 : return('June')
	elif month == 7 : return('July')
	elif month == 8 : return('August')
	elif month == 9 : return('September')
	elif month == 10 : return('October')
	elif month == 11 : return('November')
	elif month == 12 : return('December')

def det_bmi(weight, growth) :
	BMI = weight / (growth * growth) * 10000
	if BMI < 18.5 : 
		print('\nUnderweight!')
	elif BMI < 24.99 : 
		print("\nYou are absolutely healthy!")
	elif BMI < 29.99 : 
		print('\nOverweight!')
	elif BMI > 30 : 
		print('\nObese!!!') 
	return(BMI)

def det_cindex(weight, growth, age, lifestyle, goal, gender) :
	if lifestyle == 'active' : actindex = 1.55
	elif lifestyle == 'normal' : actindex = 1.375
	elif lifestyle == 'passive' : actindex = 1.2

	if goal == 'more' : Dindex = 1.15
	elif goal == 'same' : Dindex = 1
	elif goal == 'less' : Dindex = 0.85

	if gender == 'm' : cindex = int(Dindex * actindex * (88.362 + (4.799 * growth) + (13.397 * weight) - (5.677 * age)))
	elif gender == 'f' : cindex = int(Dindex * actindex * (447.593 + (3.098 * growth) + (9.247 * weight) - (4.33 * age)))

	return(cindex)

def foodfull(ftype, gramm, conn, cur, uid) :
	current_dt = datetime.now()
	day = current_dt.day
	month = detectmonth(current_dt.month)
	year = current_dt.year
	keydate = str(current_dt.date()) + ' ' + str(uid)

	try: 
		cur.execute('''SELECT total FROM Dates WHERE keydate = ? ''', (keydate, ))
		total = cur.fetchone()[0]
	except: total = 0

	cur.execute('''INSERT OR IGNORE INTO Dates (keydate, day, month, year, total, user_id)
		VALUES ( ?, ?, ?, ?, ?, ? )''', ( keydate, day, month, year, total , uid))
	cur.execute('''SELECT id FROM Dates WHERE keydate = ? ''', (keydate, ))
	dates_id = cur.fetchone()[0]

	cur.execute('''SELECT id, factor FROM Foodtype WHERE name = ? ''', (ftype, ))
	stuff = cur.fetchone()
	foodtype_id = stuff[0]
	factor = stuff[1]

	calories = factor * gramm
	cur.execute('''INSERT INTO Eating (mass, calories, dates_id, foodtype_id, user_id)
		VALUES ( ?, ?, ?, ?, ? )''', ( gramm, calories, dates_id, foodtype_id, uid ))

	total = total + calories
	cur.execute('UPDATE Dates SET total = ? WHERE keydate = ? ', (total, keydate))

	cur.execute('SELECT cindex FROM User WHERE id = ?', (uid, ))
	cindex = cur.fetchone()[0]
	 

	print('Your day plan: ', int(total), '/', cindex, sep = '')
	if total - 100 >= cindex : print('>>>>>>> Done! <<<<<<<')

	if total <= cindex + 100 and total >= cindex - 100 : 
		cur.execute('UPDATE Dates SET status = ? WHERE keydate = ? ', (0, keydate))
	elif total < cindex - 100 : 
		cur.execute('UPDATE Dates SET status = ? WHERE keydate = ? ', (-1, keydate))
	elif total > cindex + 100 : 
		cur.execute('UPDATE Dates SET status = ? WHERE keydate = ? ', (1, keydate))

	conn.commit()
	return()

def help() :
	print('\n=========================================================================')
	print('If you want to add some data just write: "name of food", "mass in gramm"')
	print('COMMANDS:')
	print('>/alldata - to see all types of food')
	print('>/addtype - to add new type of food')
	print('>/info - to see information about user')
	print('>/statistic - to see some your statistic')
	print('>/changestyle - to change yuor lifestyle (active, passive and normal)')
	print('>/changepd - to change personal data like weight and e.t.c.')
	print('>/changediet - to change your goal about your weight')
	print('>/adduser - to add new user')
	print('=========================================================================\n')
	return()

def info(cur, uid) :
	cur.execute('SELECT * FROM User WHERE id = ? ', (uid, ))
	data = cur.fetchone()
	name = data[1]
	weight = data[2]
	growth = data[3]
	age = data[4]
	gender = data[5]
	cindex = data[6]
	bmi = data[7]
	lifestyle = data[8]
	diet = data[9]

	cur.execute('SELECT total FROM Dates WHERE user_id = ? ', (uid, ))
	try : eaten = cur.fetchone()[0]
	except : eaten = 0

	if gender == 'm' : new_gender = 'Male'
	elif gender == 'f' : new_gender = 'Female'

	print('\n================================')
	print('Name:', name.capitalize())
	print('Age:', age, 'y.o.')
	print('Gender:', new_gender)
	print('Weight:', weight, 'kg')
	print('Growth:', growth, 'cm')
	print('Calories already eaten:', eaten, 'cal')
	print('Calories limit:', cindex, 'cal')
	print('BMI:', bmi)
	print('Your lifestyle:', lifestyle)
	print('Your goal for weight:', diet)
	print('================================\n')
	return()

def change_lifestyle(conn, cur, uid) :
	cur.execute('SELECT lifestyle, weight, growth, age, goal, gender FROM User WHERE id = ?', (uid, ))
	data = cur.fetchone()
	nowls = data[0]
	weight = data[1]
	growth = data[2]
	age = data[3]
	goal = data[4]
	gender = data[5]

	print('\n=============================================================')
	print('If dont want to continue write enter')
	print('Your present lifestyle is', nowls)
	while True :
		lifestyle = input('Which you want to choose now? active/normal/passive ? ').lower()
		if len(lifestyle) < 1 : return()
		elif lifestyle == 'active' or lifestyle == 'normal' or lifestyle == 'passive' :
			break
		else : print('Please, try again')

	cindex = det_cindex(weight, growth, age, lifestyle, goal, gender)

	print('Your new lifestyle is', lifestyle.upper(), 'and new day limit is', cindex)
	print('=============================================================\n')

	cur.execute('UPDATE User SET lifestyle = ? WHERE id = ? ', (lifestyle, uid))
	cur.execute('UPDATE User SET cindex = ? WHERE id = ? ', (cindex, uid))

	conn.commit()
	return()

def change_diet(conn, cur, uid) :
	cur.execute('SELECT lifestyle, weight, growth, age, goal, gender FROM User WHERE id = ? ', (uid, ))
	data = cur.fetchone()
	lifestyle = data[0]
	weight = data[1]
	growth = data[2]
	age = data[3]
	nowgoal = data[4]
	gender = data[5]

	print('\n=============================================================')
	print('If dont want to continue write enter')
	print('Your present goal is', nowgoal, 'weight')
	while True :
		goal = input('Your weight shuold be: less/same/more ? ').lower()
		if len(goal) < 1 : return()
		elif goal == 'less' or goal == 'same' or goal == 'more' :
			break
		else : print('Please, try again')

	cindex = det_cindex(weight, growth, age, lifestyle, goal, gender)

	print('Your new weight goal is', goal.upper(), 'and new day limit is', cindex)
	print('=============================================================\n')

	cur.execute('UPDATE User SET goal = ? WHERE id = ? ', (goal, uid))
	cur.execute('UPDATE User SET cindex = ? WHERE id = ? ', (cindex, uid))

	conn.commit()
	return()

def statistic(cur, uid) :
	print('\n=============================================================')
	print('If you dont want to continue, just write enter')
	print('Which statistich do you want to see')
	current_dt = datetime.now()
	day = current_dt.day
	month = detectmonth(current_dt.month)
	year = current_dt.year
	keydate = str(current_dt.date()) + ' ' + str(uid)

	while True:
		type_of_stat = input('Which period of time? day/month/year ').lower()
		if len(type_of_stat) < 1 : return()
		elif type_of_stat == 'day' or type_of_stat == 'month' or type_of_stat == 'year' : 
			break
		else : 
			print('Wrong period')
			continue

	if type_of_stat == 'day' :

		th = ['Type', 'Mass, g', 'Calories']
		td = list()

		cur.execute('SELECT id, total FROM Dates WHERE keydate = ? ', (keydate, ))
		date_data = cur.fetchone()
		try : 
			dates_id = date_data[0] 
			total = date_data[1]
		except : 
			print('No data')
			return()

		cur.execute('SELECT cindex FROM User WHERE id = ?', (uid, ))
		cindex = cur.fetchone()[0]

		cur.execute('''SELECT Foodtype.name, Eating.mass, Eating.calories 
			FROM Eating JOIN Foodtype on Eating.foodtype_id = Foodtype.id WHERE dates_id = ? ''', (dates_id, ))
		data = cur.fetchall()
		if data[0][0] == None : 
			print('No data')
			return()

		for row in data :
			for word in row :
				td.append(word)

		table_of_day = PrettyTable(th)
		while td:
			table_of_day.add_row(td[:3])
			td = td[3:]

		print(table_of_day)
		print('   eaten/limit : ', total, '/', cindex, sep = '')
		
		return()

	elif type_of_stat == 'month' :
		print('No function')
		# th_1 = ['Day', 'Mass, g', 'Calories', 'Status']
		# td_1 = list()
		# th_2 = ['Type', 'Mass, g', 'Calories', 'Times']
		# td_2 = list()

		# cur.execute('SELECT month FROM Dates WHERE keydate = ? ', (keydate, ))

		# try : main_month = cur.fetchone()[0]
		# except : 
		# 	print('No data')
		# 	return()

		# cur.execute('SELECT ')



		# cur.execute('SELECT cindex FROM User WHERE id = ?', (uid, ))
		# cindex = cur.fetchone()[0]

		# cur.execute('''SELECT Foodtype.name, Eating.mass, Eating.calories 
		# 	FROM Eating JOIN Foodtype on Eating.foodtype_id = Foodtype.id WHERE dates_id = ? ''', (dates_id, ))
		# data = cur.fetchall()
		# if data[0][0] == None : 
		# 	print('No data')
		# 	return()

		# for row in data :
		# 	for word in row :
		# 		td.append(word)

		# table_of_day = PrettyTable(th)
		# while td:
		# 	table_of_day.add_row(td[:3])
		# 	td = td[3:]

		# print(table_of_day)
		# print('   eaten/limit : ', total, '/', cindex, sep = '')

	elif type_of_stat == 'year' :
		print('No function')
	#print('\n=============================================================')

def alldata(list_of_names) :
	print('\nYou have', len(list_of_names), 'positions:')
	count = 0
	for i in list_of_names : 
		print(i, end = ' ')
		count = count + 1
		if count % 10 == 0 : print('')
	print('\n')
	return()

def change_personal_data(conn, cur, uid) :
	print('\n=============================================================')
	print('If dont want to continue write enter')

	cur.execute('SELECT name, weight, growth, age, gender, bmi, lifestyle, goal From User WHERE id = ? ', (uid, ))
	data = cur.fetchone()
	name = data[0]
	weight = data[1]
	growth = data[2]
	age = data[3]
	gender = data[4]
	BMI = data[5]
	lifestyle = data[6]
	goal = data[7]

	print('\nDo you want to change your name:', name.capitalize(), '?')	
	while True:
		ask = input('y/n ').lower()
		if len(ask) < 1 : return()
		elif ask == 'n' : break
		elif ask == 'y' : 
			name = input('Enter your new name: ')
			cur.execute('UPDATE User SET name = ? WHERE id = ? ', (name.lower(), uid))
			conn.commit()
			break
		else : print('Please, try again')

	print('\nDo you want to change your weight:', weight, '?')
	while True:
		ask = input('y/n ').lower()
		if len(ask) < 1 : return()
		elif ask == 'n' : break
		elif ask == 'y' : 
			while True :
				weight = input('Enter your new weight: ')
				try : 
					weight = int(weight)
					break

				except :
					print('Wrong data')
					continue

			BMI = det_bmi(weight, growth)
			print('Your actual BMI is', BMI)

			cur.execute('UPDATE User SET weight = ? WHERE id = ? ', (weight, uid))
			cur.execute('UPDATE User SET bmi = ? WHERE id = ? ', (BMI, uid))

			cindex = det_cindex(weight, growth, age, lifestyle, goal, gender)

			print('Your actual day limit is', cindex)

			cur.execute('UPDATE User SET cindex = ? WHERE id = ? ', (cindex, uid))

			conn.commit()
			break

		else : print('Please, try again')

	cur.execute('SELECT weight FROM User WHERE id = ? ', (uid, ))
	weight = cur.fetchone()[0]

	print('\nDo you want to change your growth:', growth,'?')
	while True:
		ask = input('y/n ').lower()
		if len(ask) < 1 : return()
		elif ask == 'n' : break
		elif ask == 'y' : 
			while True :
				growth = input('Enter your new growth: ')
				try : 
					growth = int(growth)
					break
				except :
					print('Wrong data')
					continue

			BMI = det_bmi(weight, growth)
			print('Your actual BMI is', BMI)

			cur.execute('UPDATE User SET growth = ? WHERE id = ? ', (growth, uid))
			cur.execute('UPDATE User SET bmi = ? WHERE id = ? ', (BMI, uid))

			cindex = det_cindex(weight, growth, age, lifestyle, goal, gender)

			print('Your actual day limit is', cindex)

			cur.execute('UPDATE User SET cindex = ? WHERE id = ? ', (cindex, uid))

			conn.commit()
			break

		else : print('Please, try again')

	cur.execute('SELECT growth FROM User WHERE id = ? ', (uid, ))
	growth = cur.fetchone()[0]

	print('\nDo you want to change your age:', age,'?')	
	while True:
		ask = input('y/n ').lower()
		if len(ask) < 1 : return()
		elif ask == 'n' : break
		elif ask == 'y' : 
			while True :
				age = input('Enter your new age: ')
				try : 
					age = int(age)
					break
				except :
					print('Wrong data')
					continue

			cindex = det_cindex(weight, growth, age, lifestyle, goal, gender)

			print('Your actual day limit is', cindex)

			cur.execute('UPDATE User SET age = ? WHERE id = ? ', (age, uid))
			cur.execute('UPDATE User SET cindex = ? WHERE id = ? ', (cindex, uid))

			conn.commit()
			break

		else : print('Please, try again')

	cur.execute('SELECT age FROM User WHERE id = ? ', (uid, ))
	age = cur.fetchone()[0]
	
	if gender == 'm' : full_gender = 'Male'
	elif gender == 'f' : full_gender = 'Female'
	print('\nDo you want to change your gender:', full_gender,'?')
	while True:
		ask = input('y/n ').lower()
		if len(ask) < 1 : return()
		elif ask == 'n' : break
		elif ask == 'y' : 
			while True :
				gender = input('Enter your new gender: M or F ? ').lower()
				if gender == 'm' or gender == 'f' : break
				else : 
					print('Wrong data')
					continue 

			cindex = det_cindex(weight, growth, age, lifestyle, goal, gender)

			print('Your actual day limit is', cindex)

			cur.execute('UPDATE User SET gender = ? WHERE id = ? ', (gender, uid))
			cur.execute('UPDATE User SET cindex = ? WHERE id = ? ', (cindex, uid))

			conn.commit()
			break

		else : print('Please, try again')

	print('=============================================================\n')
