import hfun as h
import sqlite3

conn = sqlite3.connect('mydatadb.sqlite')
cur = conn.cursor()

h.starter(conn, cur)
uid = h.user_detect(conn, cur)
if uid == None : 
	uid = h.user_detect(conn, cur)

def create_list_of_names(cur) :
	list_of_names = list()
	cur.execute('SELECT name FROM Foodtype')
	names_raw = cur.fetchall()
	for row in names_raw :
		list_of_names.append(row[0])
	return(list_of_names)

list_of_names = create_list_of_names(cur)

print('\nHello! More information: "/help". If you dont want to continue just enter')
while True :
	data = input('<•>').lower()
	if len(data) < 1 : break
	food = data.split(', ')

	if data.startswith('/') : 
		if data[1:] == 'alldata' : h.alldata(list_of_names)
		elif data[1:] == 'addtype' : 
			h.new_foodtype_data(conn, cur)
			list_of_names = create_list_of_names(cur)
		elif data[1:] == 'help' : h.help()
		elif data[1:] == 'info' : h.info(cur, uid)
		elif data[1:] == 'statistic' : h.statistic(cur, uid)
		elif data[1:] == 'changestyle' : h.change_lifestyle(conn, cur, uid)
		elif data[1:] == 'changepd' : h.change_personal_data(conn, cur, uid)
		elif data[1:] == 'changediet' : h.change_diet(conn, cur, uid)
		elif data[1:] == 'adduser' : h.add_user(conn, cur)
		else : print('I dont know such command')

	elif len(food) == 2 : 
		try : gramm = float(food[1])
		except:
			print('Wrong data for food (no digit for mass)')
			continue

		detected_name = None
		for real_name in list_of_names :
			if real_name == food[0] :
				detected_name = real_name
				break
		if detected_name == None : 
			print('There is no such food')
			continue
		h.foodfull(food[0], gramm, conn, cur, uid)

	else : print('I cant understand you (•)_(•)')

cur.close()