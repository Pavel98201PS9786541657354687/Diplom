import pandas as pd 
import csv, json, datetime
import pandas as pd
import psycopg2
from psycopg2 import Error
from sqlalchemy import create_engine
from control_actions_files import actions_file

class write_logs():

	def write_row(actions = "Не было действия"):

		filename = str(f"{actions_file.path()}/log.txt")
		file = open(filename, 'a')
		
		today = str(datetime.datetime.today())[:-7].replace(":","-")
		row = str(f"{actions} - {today}")
		try:
			file.write(f"\n{row}")
		except:
			file.write(f"Ошибка - {today}")
		finally:
			file.close()

	def read_row():

		path = str(f"{actions_file.path()}/log.txt")
		with open(path) as file:
			lines = file.read().splitlines()

		dict_logs = {}
		number = 1

		for line in lines:
			try:
				active,datetime = line.split(" - ",2)
				dict_logs[number] = [active, datetime]
				number += 1
			except:
				continue
		df = pd.DataFrame.from_dict(dict_logs, orient="index").\
		rename(columns={
			0:'Действие',
			1:'Дата и время'
			})
		dict_logs = None

		try:
			engine=create_engine(\
				'postgresql+psycopg2://postgres:admin@127.0.0.1:5432/diplom')
			conn=engine.raw_connection()
			cur = conn.cursor()
			str_connect = "Связь с БД установлена!"
		except:
			str_connect = "Что-то пошло не так! Связь с БД не построена"

		df.to_sql('logs', con=engine, index=False, if_exists='replace')
		df = pd.read_sql("SELECT * FROM logs;", con=conn)
		df2 = df.tail(20).copy()
		conn.commit()
		cur.close()
		conn.close()
		del df
		
		return df2