import psycopg2, datetime, pyodbc, sqlalchemy
import pandas as pd
import numpy as np
from psycopg2 import Error
from sqlalchemy import create_engine
from sqlalchemy.engine.url import URL
from control_actions_files import actions_file

class control_db():

	def connect_db():
		#Функция для соединения с бд

		try:
			connection_string = "DRIVER={PostgreSQL Unicode};\
				SERVER=127.0.0.1;\
				DATABASE=diplom;\
				UID=postgres;\
				PWD=admin"

			connection_url = URL.create("postgresql+psycopg2", \
				query={"odbc_connect": connection_string})

			engine = create_engine(connection_url)
			conn = engine.raw_connection()
		except:
			engine=create_engine(\
				'postgresql+psycopg2://postgres:admin@127.0.0.1:5432/diplom')
			conn = engine.raw_connection()
		try:
			cur = conn.cursor()
			str_connect = "Связь с БД установлена!"
		
		except:
			cur = None
			engine = None
			str_connect = "Что-то пошло не так! Связь с БД не построена"


		return [cur,conn, engine, str_connect]

	def status_db():
		list_conn = control_db.connect_db()
		cur = list_conn[0]
		conn = list_conn[1]
		engine = list_conn[2]

		sql = "SELECT table_name FROM information_schema.tables WHERE table_schema='public'"
		cur.execute(sql)
		tables = cur.fetchall()

		list_table_names = []
		for i in tables:
			list_table_names.append(str(i)[2:-3])

		list_table_names.remove("logs")
		list_table_names.remove("info_for_tables")

		table_name = "info_for_tables_view"
		df = pd.read_sql(f"SELECT * FROM {table_name};", con=conn)

		return df

	def update_status_db():
		list_conn = control_db.connect_db()
		cur = list_conn[0]
		conn = list_conn[1]
		engine = list_conn[2]	
		
		table_name = "info_for_tables"
		df = pd.read_sql(f"SELECT * FROM {table_name};", con=conn)
		df = df.drop_duplicates(['Таблица'], keep="last")

		sql = "SELECT table_name FROM information_schema.tables WHERE table_schema='public'"
		cur.execute(sql)
		tables = cur.fetchall()

		list_table_names = []
		for i in tables:
			list_table_names.append(str(i)[2:-3])

		list_table_names.remove("logs")
		list_table_names.remove("info_for_tables")
		list_table_names.remove("info_for_tables_view")

		df = df[df['Таблица'].isin(list_table_names)]

		table_name = "info_for_tables_view"
		df.to_sql(table_name, con=engine, index=False, if_exists='replace')

		#table_name = "info_for_tables"
		#df.to_sql(table_name, con=engine, index=False, if_exists='replace')

		del table_name
		conn.commit()
		cur.close()
		conn.close()

		return df

	def close_connect(cur, conn):
		#Функция для закрытия соединения с БД
		conn.commit()
		cur.close()
		conn.close()

	def db_names():
		list_conn = control_db.connect_db()
		cur = list_conn[0]
		conn = list_conn[1]
		engine = list_conn[2]

		sql = "SELECT table_name FROM information_schema.tables WHERE table_schema='public'"
		cur.execute(sql)
		tables = cur.fetchall()

		conn.commit()
		cur.close()
		conn.close()
		list_table_names = list(tables)		

		return list_table_names

	def select_db(table_name = 'oleg'):
		#Функция для выбора данных из таблицы
		list_conn = control_db.connect_db()
		cur = list_conn[0]
		conn = list_conn[1]
		engine = list_conn[2]
		try:
			table_name = table_name
		except:
			table_name = 'test_insert'

		df = pd.read_sql(f"SELECT * FROM {table_name};", con=conn)
		
		conn.commit()
		cur.close()
		conn.close()
		label = str(f"Выбрана таблица {table_name}, в ней {df.shape[0]} строк и {df.shape[1]} колонок")
		list_result = [df, label]
		return list_result

	def select_top_10(table_name = 'test_for_analyze'):
		#Функция для выбора данных из таблицы
		list_conn = control_db.connect_db()
		cur = list_conn[0]
		conn = list_conn[1]
		engine = list_conn[2]
		try:
			table_name = table_name
		except:
			table_name = 'test_insert'

		df = pd.read_sql(f"SELECT * FROM {table_name} LIMIT 10;", con=conn)
		
		conn.commit()
		cur.close()
		conn.close()
		return df	

	def select_unique_columns(table_name = 'test_for_analyze'):
		list_conn = control_db.connect_db()
		cur = list_conn[0]
		conn = list_conn[1]
		engine = list_conn[2]
		
		sql = str(f"SELECT column_name\
			FROM INFORMATION_SCHEMA.COLUMNS\
			WHERE table_name = '{table_name}';")
		cur.execute(sql)
		df = pd.DataFrame()
		list_unique_values = cur.fetchall()
		df['need'] = list_unique_values
		df['need'] = df['need'].astype(str).str.replace("(","").\
		str.replace(")","").str.replace("'","").str.replace(",","")
		list_unique_values = df.need.to_list()
		
		del df

		conn.commit()
		cur.close()
		conn.close()
		return list_unique_values

	def select_unique_columns_float(table_name = 'oleg'):
		list_conn = control_db.connect_db()
		cur = list_conn[0]
		conn = list_conn[1]
		engine = list_conn[2]
		
		sql = str(f"SELECT column_name\
			FROM INFORMATION_SCHEMA.COLUMNS\
			WHERE table_name = '{table_name}';")
		cur.execute(sql)
		list_unique_values = cur.fetchall()
		df = pd.DataFrame()
		df['need'] = list_unique_values

		sql = str(f"SELECT data_type\
			FROM INFORMATION_SCHEMA.COLUMNS\
			WHERE table_name = '{table_name}';")
		cur.execute(sql)
		list_unique_values = cur.fetchall()

		df['type'] = list_unique_values
		
		df = df[df['type'].astype(str).str.contains("double precision")].copy()
		df['need'] = df['need'].astype(str).str.replace("(","").\
		str.replace(")","").str.replace("'","").str.replace(",","")
		
		list_unique_values = df.need.to_list()
		del df

		conn.commit()
		cur.close()
		conn.close()
		return list_unique_values
		
	def create_table(table_name):
		list_conn = control_db.connect_db()
		cur = list_conn[0]
		conn = list_conn[1]
		engine = list_conn[2]
		
		cur.execute(f"CREATE TABLE {str(table_name)} ();")
		
		conn.commit()
		cur.close()
		conn.close()

	def drop_table(table_name):
		list_conn = control_db.connect_db()
		cur = list_conn[0]
		conn = list_conn[1]
		engine = list_conn[2]

		cur.execute(f"DROP TABLE {str(table_name)};")

		conn.commit()
		cur.close()
		conn.close()
		label = str(f"Таблица {table_name} удалена")
		return label

	def our_sql_text(sql_text = "SELECT * FROM oleg LIMIT 10;"):
		
		list_conn = control_db.connect_db()
		cur = list_conn[0]
		conn = list_conn[1]
		engine = list_conn[2]
		try:
			cur.execute(sql_text)
			try:
				df = pd.read_sql(sql_text, con=conn)
			except:
				list_need = cur.fetchall()
				df = pd.DataFrame()
				df['need'] = list_need
				del list_need
		except:
			df = pd.DataFrame()

		conn.commit()
		cur.close()
		conn.close()
		return df

	def insert_(table_name, filename):
		#Функция для записи в БД
		list_conn = control_db.connect_db()
		cur = list_conn[0]
		conn = list_conn[1]
		engine = list_conn[2]
		try:
			df = pd.read_csv(f"{actions_file.path()}/files_for_bd/{filename}",\
				low_memory=False)

			list_cols = []
			for i in df.columns:
				if len(str(i)) > 55:
					i = str(i)[-55:]
				else:
					i = i
				list_cols.append(i)

			df.columns = list_cols
			del list_cols

			for i in df.columns:
				list_cols = [name + str('_') + str(num)\
				for num,name in enumerate(df.columns)]

			try:
				for i in df.columns[df.columns.str.contains("=")]:
					j = str(i).split(" = ")[1]
					df = df.rename(columns={
						i:j
						})
			except:
				a = 10

			df.columns = list_cols

		except:
			df = pd.DataFrame()

		try:
			df.to_sql(table_name, con=engine, index=False, if_exists='replace')
			text = "обновлены"
			print("Данные обновлены")
		except:
			text = "не обновлены - Ошибка"
		
		table_name2 = "info_for_tables"

		dict_result = {'Таблица':table_name,
			'Количество колонок':df.shape[1],
			'Количество строк':df.shape[0],
			'Дата создания':str(datetime.datetime.today())[:-7]
			}

		result = pd.DataFrame.from_dict(dict_result, orient="index").T

		del dict_result
		del df

		result.to_sql(table_name2, con=engine, index=False, if_exists='append')

		del result
		del table_name
		del table_name2

		conn.commit()
		cur.close()
		conn.close()

		return text


#control_db.insert_("test_new", "test_old_data.csv")