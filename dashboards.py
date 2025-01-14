from PyQt5 import QtCore, QtWidgets, QtWebEngineWidgets


import pandas as pd
import numpy as np
import datetime, os, json, random
from connect_db import control_db
import plotly.express as px
import plotly.graph_objs as go
from plotly.subplots import make_subplots

class Widget_plotly(QtWidgets.QWidget):
	def __init__(self, parent=None):
		super().__init__(parent)

		self.combo = QtWidgets.QComboBox(self)
		self.list_graph = ['Круговая диаграмма', 'Столбчатая диаграмма','Линейный график', 'Гистограмма', 'Свечи']
		self.combo.addItems(self.list_graph)
		self.combo.setFixedWidth(200)

		self.button = QtWidgets.QPushButton('Построить график', self)
		self.browser = QtWebEngineWidgets.QWebEngineView(self)

		vlayout = QtWidgets.QVBoxLayout(self)
		vlayout.addWidget(self.combo)  
		vlayout.addWidget(self.button, alignment=QtCore.Qt.AlignHCenter)
		vlayout.addWidget(self.browser)

		self.button.clicked.connect(self.show_graph)
		self.resize(1000,800)

	def pie_graph(self):
		#Круговая диаграмма		
		df = px.data.gapminder().query("year == 2007").\
		query("continent == 'Europe'")
		df.loc[df['pop'] < 2.e6, 'country'] = 'Other countries'
		fig = px.pie(df ,values='pop', names='country', \
			title="Population of European continental")

		print(df.head().reset_index(drop=True))

		return fig

	def bar_graph(self):
		#Столбчатая диаграмма
		fig = px.bar(x=["a","b","c","d"], y=[1,2.3,3,3.5])
		return fig

	def pivot_table_graph(self):
		#Сводная таблица
		print(10)

	def scatter_graph(self):
		#Линейный график
		x = np.arange(0,5,0.1)
		def f(x):
			return x**2
		fig = px.scatter(x=x, y=f(x))
		return fig

	def kpi_text_graph(self):
		#KPI

		#Текст
		print(10)

	def hist_graph(self):
		#Гистограмма
		dices = pd.DataFrame(np.random.randint(low=1, high=7, size=(100,2)),\
			columns=('1','2'))
		dices['сумма'] = dices['1'] + dices['2']
		fig = go.Figure(data=[go.Histogram(x=dices['сумма'])])
		return fig

	def box_graph(self):
		#Свечи
		df = px.data.tips()
		fig = px.box(df, y="total_bill", color="smoker")
		return fig

	def show_graph(self):
		choise = self.combo.currentText()

		if choise == self.list_graph[0]:
			fig = self.pie_graph()
		elif choise == self.list_graph[1]:
			fig = self.bar_graph()
		elif choise == self.list_graph[2]:
			fig = self.scatter_graph()
		elif choise == self.list_graph[3]:
			fig = self.hist_graph()
		elif choise == self.list_graph[4]:
			fig = self.box_graph()

		fig.update_traces()#quartilemethod="inclusive")
		self.browser.setHtml(fig.to_html(include_plotlyjs='cdn'))

if __name__ == "__main__":
	app = QtWidgets.QApplication([])
	widget = Widget_plotly()
	widget.show()
	app.exec()