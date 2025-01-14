import sys, os
import pandas as pd

class control_iptables():

	def read_actuals_rules():
		path = '/etc/iptables/rules.v4'

		with open(path) as file:
			lines = file.read().splitlines()
			
		df = pd.DataFrame()
		df['Правила'] = lines
		df = df.reset_index(drop=True)
		#print(df)
		return df

	def create_new_rule(text="sobaka"):
		print(10)

	def edit_rule(text="sobaka"):
		print(5)

	def drop_rule(text="sobaka"):
		print(5)