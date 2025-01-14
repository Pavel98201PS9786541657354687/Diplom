import pandas as pd
import datetime, os, json
from connect_db import control_db

class analyser():

	def main_stat_traffic(table_name = "contact"):
		
		df = control_db.select_db(table_name)[0]

		try:
			df['Layer WLAN - addr'] = df['Layer WLAN - addr'].astype(str).str.\
			replace("[","", regex=True).str.replace("]","", regex=True).\
			str.replace("' ' ",":", regex=True).\
			str.replace("' ","", regex=True).str.replace("'","", regex=True)

			result = df.groupby('Layer WLAN - addr', as_index=False).agg({
				'Frame number':'nunique',
				'Layer RADIOTAP - length':'mean',
				'Layer RADIOTAP - rate':'mean',
				'Layer WLAN - duration':'mean',
				'Layer WLAN_RADIO - signal_dbm':'mean',
				'Layer WLAN - retry':'sum'
				})
		
			result = result.rename(columns={
				'Layer WLAN - addr':'MAC-адрес',
				'Frame number':'Количество пакетов',
				'Layer RADIOTAP - length':'Средняя длина пактеов (bytes)',
				'Layer RADIOTAP - rate':'Средняя скорость передачи',
				'Layer WLAN - duration':'Средняя длительность передачи',
				'Layer WLAN_RADIO - signal_dbm':'Средний уровень сигнала (Дбм)',
				'Layer WLAN - retry':'Количество паетов с заголовком retry'
				})
		except:

			list_cols = ['layers.frame.frame.number','layers.wlan.wlan.sa',
			'layers.frame.frame.len','layers.frame.frame.time_relative',
			'layers.wlan_radio.wlan_radio.signal_dbm',
			'layers.wlan_radio.wlan_radio.data_rate',
			'layers.wlan.wlan.fc_tree.wlan.flags_tree.wlan.fc.retry']

			list_need_cols = []

			df2 = pd.DataFrame()
			df2['need'] = df.columns.to_list()

			for i in list_cols:
				j = str(df2.loc[df2['need'].str.contains(f"{i}_\d"),\
				 'need'].to_list())[2:-2]
				list_need_cols.append(j)
				del j

			
			df2 = df[list_need_cols].copy()

			del df
			del list_need_cols


			j = 0
			for i in df2.columns:
				df2 = df2.rename(columns={
					i : list_cols[j]
					})
				j += 1


			df2 = df2.rename(columns={'layers.frame.frame.number': 'number_frame',
				'layers.wlan.wlan.sa': 'mac_addr',
				'layers.wlan_radio.wlan_radio.data_rate': 'speed',
				'layers.frame.frame.len': 'length',
				'layers.frame.frame.time_relative': 'duration',
				'layers.wlan_radio.wlan_radio.signal_dbm':'signal_dbm',
				'layers.wlan.wlan.fc_tree.wlan.flags_tree.wlan.fc.retry': 'retry'})

			df2[['number_frame', 'length', 'duration', 'signal_dbm', 'speed', 'retry']] = \
			df2[['number_frame', 'length', 'duration', 'signal_dbm', 'speed', 'retry']].\
			apply(lambda x : x.astype(float))

			df2.mac_addr = df2.mac_addr.fillna("empty")
			result = df2.groupby('mac_addr', as_index=False).agg({\
				'number_frame':'count',
				'length':'mean',
				'speed':'mean',
				'duration':'mean',
				'signal_dbm':'mean',
				'retry':'sum'
				})

			del df2

			result = result.rename(columns={
				'mac_addr':'MAC-адрес',
				'number_frame':'Количество пакетов',
				'length':'Средння длина пактеов (bytes)',
				'speed':'Средняя скорость передачи',
				'duration':'Средняя длительность передачи',
				'signal_dbm':'Средний уровень сигнала (Дбм)',
				'retry':'Количество паетов с заголовком retry'
				})

		return result

	def retry():
		print(10)

	def ddos():
		print(10)

	def anomalyies_on_wifi():
		print(10)