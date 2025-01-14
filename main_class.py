#!/usr/bin/env python3

import sys, time, os, select, termios, curses 
import pandas as pd
import numpy as np
from PyQt5 import QtCore, QtWidgets, QtWebEngineWidgets
from PyQt5.QtWidgets import (QMainWindow, QApplication, QVBoxLayout, 
    QSplitter, QButtonGroup, QFormLayout, QLabel, QFrame, QPushButton, 
    QAbstractButton, QMenu, QAction, QRadioButton, QLCDNumber, QSlider, 
    QLineEdit, QTableWidget, QTableWidgetItem, QTableView, 
    QTableWidgetItem, QComboBox, QPlainTextEdit, QHBoxLayout, 
    QWidget, QFileDialog, QPlainTextEdit, QAbstractScrollArea)                                      
from PyQt5.QtCore import (Qt, QAbstractTableModel)
from PyQt5 import QtGui
from PyQt5.QtGui import QFont, QIcon, QBrush, QPixmap

#Подключение внутренних классов
import style
from connect_db import control_db
from control_actions_files import actions_file
from logs import write_logs
from analyse_traffic import analyser
from iptables import control_iptables
from control_capture_traffic import control_capture 
from dashboards import Widget_plotly

#Подключение plotly
import datetime, os, json, random
import plotly.express as px
import plotly.graph_objs as go
from plotly.subplots import make_subplots

class PdTable(QAbstractTableModel):
    def __init__(self, df):
        QAbstractTableModel.__init__(self)
        self.df = df

    def rowCount(self, parent=None):
        return self.df.shape[0]

    def columnCount(self, parent=None):
        return self.df.shape[1]

    #Данные дисплея
    def data(self, index, role=Qt.DisplayRole):
        if index.isValid():
            if role == Qt.DisplayRole:
                return str(self.df.iloc[index.row(), index.column()])
        return None

    #Отображение загловка строки и столбца
    def headerData(self, col, orientation, role):
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            return self.df.columns[col]
        elif orientation == Qt.Vertical and role == Qt.DisplayRole:
            return self.df.axes[0][col]
        return None

class main_window(QMainWindow):
    def __init__(self):
        super().__init__()

        self.create_body()

    def btn_controls_file(self):

        actions = "Перешли на панель управления файлами"
        write_logs.write_row(actions)

        #Удаление всех виджетов 
        for i in range(self.addwid.count()):
            self.addwid.itemAt(i).widget().deleteLater()

        text = "Управление репозиторием"
        self.lbl = QLabel(text, self)
        self.lbl.setFont(QFont('Serif', 16))
        self.addwid.addWidget(self.lbl)

        self.getFileNameButton = QPushButton("Добавить файл", self)
        self.getFileNameButton.clicked.connect(self.getFileName)
        self.getFileNameButton.setFixedWidth(400)
        self.addwid.addWidget(self.getFileNameButton)

        self.btn_remove_file = QPushButton("Удалить файл", self)
        self.btn_remove_file.clicked.connect(self.remove_file)
        self.btn_remove_file.setFixedWidth(400)
        self.addwid.addWidget(self.btn_remove_file)

    def remove_file(self):
        actions = "Перешли к удалению файла"
        write_logs.write_row(actions)
        
        for i in range(self.addwid.count())[1:]:
            self.addwid.itemAt(i).widget().deleteLater()

        text = "Выберите файл"
        self.lbl2 = QLabel(text, self)
        self.lbl2.setFont(QFont('Serif', 16))
        self.addwid.addWidget(self.lbl2)
        self.combo = QComboBox(self)
        files = actions_file.list_files()
        self.combo.addItems(files)
        self.combo.setFixedWidth(400)
        self.addwid.addWidget(self.combo)  

        btn_remove_actions = QPushButton("Удалить файл")
        self.addwid.addWidget(btn_remove_actions)
        btn_remove_actions.clicked.connect(self.button_clicked_remove_file)
        btn_remove_actions.setFixedWidth(400)

        back_to_control_files = QPushButton("Вернуться назад")
        self.addwid.addWidget(back_to_control_files)
        back_to_control_files.clicked.connect(self.btn_controls_file)
        back_to_control_files.setFixedWidth(400)

    def button_clicked_remove_file(self):

        actions = 'Нажата кнопка удалить файл'
        write_logs.write_row(actions)

        for i in range(self.addwid.count())[1:]:
            self.addwid.itemAt(i).widget().deleteLater()

        try:
            actions_file.remove_file(self.combo.currentText())
            text = str(f"файл: {self.combo.currentText()} удалён")
        except:
            text = str(f"файл: {self.combo.currentText()} не удалён")

        self.lbl2 = QLabel(text, self)
        self.lbl2.setFont(QFont('Serif', 14))
        self.addwid.addWidget(self.lbl2)

        back_to_control_files = QPushButton("Вернуться назад")
        self.addwid.addWidget(back_to_control_files)
        back_to_control_files.clicked.connect(self.remove_file)
        back_to_control_files.setFixedWidth(400)

        back_to_control_files = QPushButton("Вернуться в меню управления файлами")
        self.addwid.addWidget(back_to_control_files)
        back_to_control_files.clicked.connect(self.btn_controls_file)
        back_to_control_files.setFixedWidth(400)

    def getFileName(self):

        actions = "Окно выбора файла"
        write_logs.write_row(actions)

        for i in range(self.addwid.count())[1:]:
            self.addwid.itemAt(i).widget().deleteLater()

        self.filename_for_save, filetype = QFileDialog.getOpenFileName(self,
                             "Выбрать файл",
                             ".",
                             "Text Files(*.txt);;JPEG Files(*.jpeg);;\
                             PNG Files(*.png);;GIF File(*.gif);;All Files(*)")
        if self.filename_for_save == "":
            text = str(f"Вы не выбрали файл, попробуйте снова.")
            self.lbl2 = QLabel(text, self)
            self.lbl2.setFont(QFont('Serif', 14))
            self.addwid.addWidget(self.lbl2)
            back_to_control_files = QPushButton("Вернуться назад")
            self.addwid.addWidget(back_to_control_files)
            back_to_control_files.clicked.connect(self.btn_controls_file)
            back_to_control_files.setFixedWidth(400)                
        else:
            filename_str = str(self.filename_for_save).split("diplom_maga/")[1]
            text = str(f"Вы выбрали файл: {filename_str}")
            self.lbl2 = QLabel(text, self)
            self.lbl2.setFont(QFont('Serif', 14))
            self.addwid.addWidget(self.lbl2)

            self.text = "Введите название файла"
            self.lbl3 = QLabel(self.text, self)
            self.lbl3.setFont(QFont('Serif', 14))
            self.addwid.addWidget(self.lbl3)

            self.qle2 = QLineEdit(self)
            self.qle2.setFixedWidth(400)
            self.addwid.addWidget(self.qle2)

            #Сохранение файла
            saveFileNameButton = QPushButton("Сохранить файл")
            saveFileNameButton.setFixedWidth(400)
            self.addwid.addWidget(saveFileNameButton)
            saveFileNameButton.clicked.connect(self.saveFile)

            back_to_control_files = QPushButton("Вернуться назад")
            back_to_control_files.setFixedWidth(400)
            self.addwid.addWidget(back_to_control_files)
            back_to_control_files.clicked.connect(self.btn_controls_file)                

    def saveFile(self):

        actions = 'Нажата кнопка Сохранить файл'
        write_logs.write_row(actions)

        for i in range(self.addwid.count())[1:]:
            self.addwid.itemAt(i).widget().deleteLater()

        if self.qle2.text() == "":
            text = "Вы не ввели название файла"
            self.lbl2 = QLabel(text, self)
            self.lbl2.setFont(QFont('Serif', 14))
            self.addwid.addWidget(self.lbl2)
            back_to_save_file = QPushButton("Попробовать снова")
            self.addwid.addWidget(back_to_save_file)
            back_to_save_file.clicked.connect(self.getFileName)
            back_to_save_file.setFixedWidth(400)
        else:
            #Место под сохранение файла
            symbol = actions_file.control_load_files(\
                self.filename_for_save, self.qle2.text())

            if symbol == 0:
                new_filename = str(f"{self.qle2.text()}.csv")
                text = str(f"файл: {new_filename} сохранён")
                self.lbl2 = QLabel(text, self)
                self.lbl2.setFont(QFont('Serif', 14))
                self.addwid.addWidget(self.lbl2)
            elif symbol == 1:
                new_filename = str(f"{self.qle2.text()}.csv").split("/")[-1]
                text = str(f"файл: {new_filename} не сохранён\nОшибка в коде")
                self.lbl2 = QLabel(text, self)
                self.lbl2.setFont(QFont('Serif', 14))
                self.addwid.addWidget(self.lbl2)

                back_to_save_file = QPushButton("Попробовать снова")
                self.addwid.addWidget(back_to_save_file)
                back_to_save_file.clicked.connect(self.getFileName)
                back_to_save_file.setFixedWidth(400)

            elif symbol == 2:
                new_filename = str(f"{self.qle2.text()}.csv").split("/")[-1]
                text = str(f"файл: {new_filename} не сохранён\nТакой формат обработать пока что нельзя")
                self.lbl2 = QLabel(text, self)
                self.lbl2.setFont(QFont('Serif', 14))
                self.addwid.addWidget(self.lbl2)

                back_to_save_file = QPushButton("Попробовать снова")
                self.addwid.addWidget(back_to_save_file)
                back_to_save_file.clicked.connect(self.getFileName)
                back_to_save_file.setFixedWidth(400)

            else:
                new_filename = str(f"{self.qle2.text()}.csv").split("/")[-1]
                text = str(f"файл: {new_filename} не сохранён\n Неизвестная ошибка")
                self.lbl2 = QLabel(text, self)
                self.lbl2.setFont(QFont('Serif', 14))
                self.addwid.addWidget(self.lbl2)

                back_to_save_file = QPushButton("Попробовать снова")
                self.addwid.addWidget(back_to_save_file)
                back_to_save_file.clicked.connect(self.getFileName)
                back_to_save_file.setFixedWidth(400)

        back_to_control_files = QPushButton("Вернуться в меню управления файлами")
        self.addwid.addWidget(back_to_control_files)
        back_to_control_files.clicked.connect(self.btn_controls_file)
        back_to_control_files.setFixedWidth(400)            

    def btn_logs_control(self):
        
        actions = "Перешли на уровень управления логами"
        write_logs.write_row(actions)

        text = "История действий пользователей"
        
        #Удаление всех виджетов 
        for i in range(self.addwid.count()):
            self.addwid.itemAt(i).widget().deleteLater()

        self.lbl = QLabel(text, self)
        self.lbl.setFont(QFont('Serif', 16))
        self.addwid.addWidget(self.lbl)

        df = write_logs.read_row()
        model = PdTable(df)
        self.table = QTableView()
        self.table.setModel(model)
        self.lbl2 = QLabel("Последние 20 действий пользователей")
        self.lbl2.setFont(QFont('Serif', 12))
        self.addwid.addWidget(self.lbl2)
        self.table.setWindowTitle(text)
        self.table.setAlternatingRowColors(True)
        self.table.show()
        self.addwid.addWidget(self.table)                
        
    def btn_update_firewall(self):

        actions = "Перешли на уровень управления браэндмауэром"
        write_logs.write_row(actions)

        #Удаление всех виджетов 
        for i in range(self.addwid.count()):
            self.addwid.itemAt(i).widget().deleteLater()

        text = "Управление правилами браэндмауэром"
        self.lbl = QLabel(text, self)
        self.lbl.setFont(QFont('Serif', 16))
        self.addwid.addWidget(self.lbl)
        self.btn_create_rules = QPushButton("Создать новое правило", self)
        self.btn_create_rules.clicked.connect(self.btn_create_new_rule)
        self.btn_create_rules.setFixedWidth(400)
        self.addwid.addWidget(self.btn_create_rules)
        self.btn_view_rules = QPushButton("Посмотреть существующие правила", self)
        self.btn_view_rules.clicked.connect(self.btn_view_actual_rules)
        self.btn_view_rules.setFixedWidth(400)
        self.addwid.addWidget(self.btn_view_rules)
        self.btn_edit_rules = QPushButton("Изменить существующее правила", self)
        self.btn_edit_rules.clicked.connect(self.btn_edit_actual_rules)
        self.btn_edit_rules.setFixedWidth(400)
        self.addwid.addWidget(self.btn_edit_rules)
        self.btn_remove_rules = QPushButton("Удалить существующее правила", self)
        self.btn_remove_rules.clicked.connect(self.btn_remove_actual_rules)
        self.btn_remove_rules.setFixedWidth(400)
        self.addwid.addWidget(self.btn_remove_rules)

    def btn_create_new_rule(self):

        actions = "Перешли на панель создания нового правила в браэндмауэре"
        write_logs.write_row(actions)

        #Удаление всех виджетов 
        for i in range(self.addwid.count()):
            self.addwid.itemAt(i).widget().deleteLater()
        text = "Создание нового правила"
        self.lbl2 = QLabel(text, self)
        self.lbl2.setFont(QFont('Serif', 16))
        self.addwid.addWidget(self.lbl2)
        text_2 = "Примеры правил:"
        self.lbl3 = QLabel(text_2, self)
        self.lbl3.setFont(QFont('Serif', 14))
        self.addwid.addWidget(self.lbl3)
        example_drop = str(f"Запрещающее правило:\n\
        iptables -A INPUT -s 10.10.10.10 -j DROP")
        self.lbl4 = QLabel(example_drop, self)
        self.lbl4.setFont(QFont('Serif', 12))
        self.addwid.addWidget(self.lbl4)
        example_accept = str(f"Разрешающее правило:\n\
        iptables -A INPUT -p tcp --dport 80 -j ACCEPT")
        self.lbl5 = QLabel(example_accept, self)
        self.lbl5.setFont(QFont('Serif', 12))
        self.addwid.addWidget(self.lbl5)
        example_connect_ports = str(f"Правило для проброса портов:\n\
        iptables -I FORWARD 1 -i eth0 -o eth1 -d $LAN_IP -p tcp\n\
        -m tcp --dport #SRV_PORT -j ACCEPT")
        self.lbl6 = QLabel(example_connect_ports, self)
        self.lbl6.setFont(QFont('Serif', 12))
        self.addwid.addWidget(self.lbl6)

        text_lbl = "Введите новое правило"
        self.lbl7 = QLabel(text_lbl, self)
        self.lbl7.setFont(QFont('Serif', 12))
        self.addwid.addWidget(self.lbl7)        
        self.qle = QLineEdit(self)
        self.addwid.addWidget(self.qle)
        self.qle.setFixedWidth(400)
        self.btn_post_rules = QPushButton("Создать новое правило", self)
        self.btn_post_rules.setFixedWidth(400)
        self.addwid.addWidget(self.btn_post_rules)

        back_to_control_files = QPushButton("Вернуться назад")
        self.addwid.addWidget(back_to_control_files)
        back_to_control_files.clicked.connect(self.btn_update_firewall)
        back_to_control_files.setFixedWidth(400)

    def btn_view_actual_rules(self):

        actions = "Перешли на панель просмотра всех существующих правил браэндмауэра"
        write_logs.write_row(actions)

        #Удаление всех виджетов 
        for i in range(self.addwid.count())[1:]:
            self.addwid.itemAt(i).widget().deleteLater()

        text = "Список существующих правил"
        self.lbl2 = QLabel(text, self)
        self.lbl2.setFont(QFont('Serif', 12))
        self.addwid.addWidget(self.lbl2)

        df = control_iptables.read_actuals_rules()
        model = PdTable(df[1:])
        self.table = QTableView()
        self.table.setModel(model)
        self.table.resize(410, 250)
        self.table.setWindowTitle(text)
        self.table.setAlternatingRowColors(True)
        self.table.show()
        self.addwid.addWidget(self.table)

        back_to_control_files = QPushButton("Вернуться назад")
        self.addwid.addWidget(back_to_control_files)
        back_to_control_files.clicked.connect(self.btn_update_firewall)
        back_to_control_files.setFixedWidth(400)

    def btn_edit_actual_rules(self):
        
        actions = "Перешли на панель редактирования существующих правил браэндмауэра"
        write_logs.write_row(actions)

        #Удаление всех виджетов 
        for i in range(self.addwid.count()):
            self.addwid.itemAt(i).widget().deleteLater()        

        label = "Раздел редактирования правил браэндмауэра"
        self.lbl = QLabel(label, self)
        self.lbl.setFont(QFont('Serif', 16))
        self.addwid.addWidget(self.lbl)

        text = "Выберите правило"
        self.lbl2 = QLabel(text, self)
        self.lbl2.setFont(QFont('Serif', 12))
        self.addwid.addWidget(self.lbl2)   

        self.combo = QComboBox(self)
        list_table_names = ["rule1",  "rule2", "rule3"]
        self.combo.addItems(list_table_names)
        self.combo.setFixedWidth(400)
        self.addwid.addWidget(self.combo)     

        self.button_edit_rules_cl = QPushButton("Редактировать правило")
        self.addwid.addWidget(self.button_edit_rules_cl)
        #back_to_control_files.clicked.connect(self.btn_update_firewall)
        self.button_edit_rules_cl.setFixedWidth(400)

        back_to_control_files = QPushButton("Вернуться назад")
        self.addwid.addWidget(back_to_control_files)
        back_to_control_files.clicked.connect(self.btn_update_firewall)
        back_to_control_files.setFixedWidth(400)

    def btn_remove_actual_rules(self):
        
        actions = "Перешли на панель удаления существующих правил браэндмауэра"
        write_logs.write_row(actions)

        #Удаление всех виджетов 
        for i in range(self.addwid.count()):
            self.addwid.itemAt(i).widget().deleteLater()        

        label = "Раздел удаления правил браэндмауэра"
        self.lbl = QLabel(label, self)
        self.lbl.setFont(QFont('Serif', 16))
        self.addwid.addWidget(self.lbl)

        text = "Выберите правило"
        self.lbl2 = QLabel(text, self)
        self.lbl2.setFont(QFont('Serif', 12))
        self.addwid.addWidget(self.lbl2)   

        self.combo = QComboBox(self)
        list_table_names = ["rule1",  "rule2", "rule3"]
        self.combo.addItems(list_table_names)
        self.combo.setFixedWidth(400)
        self.addwid.addWidget(self.combo)     

        self.button_remove_rules_cl = QPushButton("Удалить правило")
        self.addwid.addWidget(self.button_remove_rules_cl)
        #back_to_control_files.clicked.connect(self.btn_update_firewall)
        self.button_remove_rules_cl.setFixedWidth(400)     

        back_to_control_files = QPushButton("Вернуться назад")
        self.addwid.addWidget(back_to_control_files)
        back_to_control_files.clicked.connect(self.btn_update_firewall)
        back_to_control_files.setFixedWidth(400)
        
    def btn_instruction(self):
        
        actions = "Перешли на уровень инструкции"
        write_logs.write_row(actions)

        #Удаление всех виджетов 
        for i in range(self.addwid.count())[1:]:
            self.addwid.itemAt(i).widget().deleteLater()
        
        text = 'Инструкция'
        self.lbl.setText(text)

        instruction = f"Для анализа трафика беспроводных сетей, \nнеобходимо придерживаться следующего алгоритма:\n\
        1. Захват трафика\n\
        2. Конвертация данных\n\
        3. Нормализация данных\n\
        4. Обработка данных\n\
        5. Построение матиматической модели\n\
        6. Рассчёт статистики\n\
        7. Выявление аномалий\n\
        8. Обработка результатов"
        self.lbl2 = QLabel(instruction, self)
        self.lbl2.setFont(QFont('Serif', 14))
        self.addwid.addWidget(self.lbl2)  

        goodluck = "Удачной игры-анализа беспроводной сети"
        self.lbl3 = QLabel(goodluck, self)
        self.lbl3.setFont(QFont('Serif', 14))
        self.addwid.addWidget(self.lbl3)

        no_game = "Не уверен, не играй!!!"   
        self.lbl4 = QLabel(no_game, self)
        self.lbl4.setFont(QFont('Serif', 14))
        self.addwid.addWidget(self.lbl4)
        
    def create_body(self):
        
        p_push = QPushButton('Управление файлами')
        p_push.setContentsMargins(10, 20, 10, 10)
        p_push1 = QPushButton('Логгирование')
        p_push1.setContentsMargins(10, 40, 10, 30)
        p_push2 = QPushButton('Управление браэндмауэром')
        p_push2.setContentsMargins(10, 60, 10, 50)
        p_push3 = QPushButton('Инструкция')
        p_push3.setContentsMargins(10, 80, 10, 70)
        
        #Создание левой колонки
        form_frame = QFrame()
        form_frame.setFrameShape(QFrame.StyledPanel)
        form_frame.setMinimumWidth(300)
        form_frame.setMaximumWidth(300)

        #Создание формы
        form_lay = QFormLayout()
        form_lay.addRow(p_push)
        form_lay.addRow(p_push1)
        form_lay.addRow(p_push2)
        form_lay.addRow(p_push3)
        form_frame.setLayout(form_lay)

        #Создание основного поля
        ver_frame = QFrame()
        ver_frame.setFrameShape(QFrame.StyledPanel)

        #Добавление label
        label = "Основное меню программы"
        self.lbl = QLabel(label, self)
        self.lbl.setFont(QFont('Serif', 16))

        self.addwid = QVBoxLayout()
        self.addwid.setContentsMargins(25, 20, 25, 25)        
        self.addwid.addWidget(self.lbl)
        ver_frame.setLayout(self.addwid)

        #Создание разделителя
        splitter = QSplitter(Qt.Horizontal)
        splitter.addWidget(form_frame)
        splitter.addWidget(ver_frame)

        self.vbox = QVBoxLayout()
        self.vbox.addWidget(splitter)
        self.setCentralWidget(splitter)

        p_push.clicked.connect(self.btn_controls_file)
        p_push1.clicked.connect(self.btn_logs_control)
        p_push2.clicked.connect(self.btn_update_firewall)
        p_push3.clicked.connect(self.btn_instruction)

class capture_trafic_window(QMainWindow):
    def __init__(self):
        super().__init__()

        self.create_body() 

    def kbhit(self):
        r = select.select([sys.stdin], [], [], 0)
        return bool(r[0])
           
    def btn_capture_traffic(self):

        actions = "Перешли на панель управления захвата трафика"
        write_logs.write_row(actions)

        text = 'Захваченный трафик'

        #Удаление всех виджетов 
        for i in range(self.addwid.count()):
            self.addwid.itemAt(i).widget().deleteLater()

        self.lbl = QLabel(text, self)
        self.lbl.setFont(QFont('Serif', 16))
        self.addwid.addWidget(self.lbl)
        self.qle = QLineEdit(self)
        self.qle2 = QLineEdit(self)
        self.lbl3 = QLabel('Введите название файла',self)
        self.lbl4 = QLabel('Выберите интерфейс',self)
        self.lbl5 = QLabel('Введите количество секунд',self)
        self.lbl.setFont(QFont('Serif', 16))
        self.lbl3.setFont(QFont('Serif', 12))
        self.lbl4.setFont(QFont('Serif', 12))
        self.lbl5.setFont(QFont('Serif', 12))
        
        table_name = self.qle.text()
        self.qle.setFixedWidth(400)
        self.qle2.setFixedWidth(400)
        self.addwid.addWidget(self.lbl3)
        self.addwid.addWidget(self.qle)
        self.addwid.addWidget(self.lbl5)
        self.addwid.addWidget(self.qle2)
        self.addwid.addWidget(self.lbl4)
        self.combo = QComboBox(self)
        list_table_names = control_capture.list_interfaces()
        self.combo.addItems(list_table_names)
        self.combo.setFixedWidth(400)
        self.addwid.addWidget(self.combo)
        
        self.btn_capture_traffic_widget = QPushButton("Перейти к захвату пакетов", self)
        self.addwid.addWidget(self.btn_capture_traffic_widget)
        self.btn_capture_traffic_widget.clicked.connect(self.btn_capture_trafic_activated)
        self.btn_capture_traffic_widget.setFixedWidth(400)  

        back_to_control_traffic = QPushButton("Вернуться назад")
        self.addwid.addWidget(back_to_control_traffic)
        back_to_control_traffic.clicked.connect(self.create_body)
        back_to_control_traffic.setFixedWidth(400)        

    def btn_capture_trafic_activated(self):

        actions = "Нажали на кнопку Перейти к захвату пакетов"
        write_logs.write_row(actions)

        self.lbl.setText("Происходит захват трафика")
        
        int_cap = str(self.combo.currentText())
        filename = str(f"{self.qle.text()}")
        seconds = int(f"{self.qle2.text()}")
        
        #Удаление ненужных виджетов
        for i in range(self.addwid.count())[1:]:
            self.addwid.itemAt(i).widget().deleteLater()

        if (filename != "") & (seconds != ""):

            list_result = control_capture.main_func(\
                filename, int_cap, seconds)
            df = list_result[0]
            self.text = list_result[1]

            if df.shape[0] == 0:
                self.lbl.setText(self.text)
            else:
                self.lbl.setText(self.text)
                text = self.qle.text()
                #Отрисовка таблицы
                model = PdTable(df.head(10))
                self.lbl2 = QLabel(f"Первые 10 строк захваченного трафика")
                self.lbl2.setFont(QFont('Serif', 12))
                self.addwid.addWidget(self.lbl2)
                self.table = QTableView()
                self.table.setModel(model)
                self.table.resize(410, 250)
                self.table.setWindowTitle(text)
                self.table.setAlternatingRowColors(True)
                self.table.show()
                self.addwid.addWidget(self.table)

        else:
            self.lbl.setText("Введите все параметры!")
        
        back_to_control_traffic = QPushButton("Вернуться назад")
        self.addwid.addWidget(back_to_control_traffic)
        back_to_control_traffic.clicked.connect(self.btn_capture_traffic)
        back_to_control_traffic.setFixedWidth(400)

        back_to_control_files = QPushButton("Вернуться в главное меню захвата трафика")
        self.addwid.addWidget(back_to_control_files)
        back_to_control_files.clicked.connect(self.btn_capture_traffic)
        back_to_control_files.setFixedWidth(400)


    def btn_time_capture_traffic(self):

        actions = "Перешли на панель управления захвата трафика по расписанию"
        write_logs.write_row(actions)

        text = 'Настройка захвата трафика по расписанию'

        #Удаление всех виджетов 
        for i in range(self.addwid.count()):
            self.addwid.itemAt(i).widget().deleteLater()


        self.lbl = QLabel(text, self) 
        self.lbl.setFont(QFont('Serif', 16))
        self.addwid.addWidget(self.lbl)

        time_text = "Выберите дату и время начала захвата трафика"
        self.lbl1 = QLabel(time_text, self) 
        self.lbl1.setFont(QFont('Serif', 12))
        self.addwid.addWidget(self.lbl1)
        self.dateEdit = QtWidgets.QDateTimeEdit()
        self.dateEdit.setGeometry(QtCore.QRect(10,10,110,22))
        self.dateEdit.setCalendarPopup(True)
        self.dateEdit.setDate(QtCore.QDate.currentDate())
        self.dateEdit.setObjectName("dateEdit")
        self.addwid.addWidget(self.dateEdit)
        self.dateEdit.setFixedWidth(400)        

        date_text = "Введите период захвата (сек.)"
        self.lbl7 = QLabel(date_text, self) 
        self.lbl7.setFont(QFont('Serif', 12))
        self.addwid.addWidget(self.lbl7)
        self.qle7 = QLineEdit(self)
        self.qle7.setFixedWidth(400)
        self.addwid.addWidget(self.qle7)

        date_text = "Выберете период повторения"
        self.lbl2 = QLabel(date_text, self) 
        self.lbl2.setFont(QFont('Serif', 12))
        self.addwid.addWidget(self.lbl2)
        self.qle1 = QLineEdit(self)
        self.qle1.setFixedWidth(400)
        self.addwid.addWidget(self.qle1)
        list_timer = ["мин.","час.","сут.","мес.","год"]
        self.combo1 = QComboBox(self)
        self.combo1.addItems(list_timer)
        self.combo1.setFixedWidth(400)
        self.addwid.addWidget(self.combo1)

        int_text = "Выберете интерфейс"
        self.lbl3 = QLabel(int_text, self) 
        self.lbl3.setFont(QFont('Serif', 12))
        self.addwid.addWidget(self.lbl3)
        self.combo = QComboBox(self)
        list_table_names = control_capture.list_interfaces()
        self.combo.addItems(list_table_names)
        self.combo.setFixedWidth(400)
        self.addwid.addWidget(self.combo)

        filename_text = "Введите название файла"
        self.lbl4 = QLabel(filename_text, self) 
        self.lbl4.setFont(QFont('Serif', 12))
        self.addwid.addWidget(self.lbl4)
        self.qle2 = QLineEdit(self)
        self.qle2.setFixedWidth(400)
        self.addwid.addWidget(self.qle2)

        btn_control_capture_traffic_for_time = QPushButton("Настроить захват трафика")
        self.addwid.addWidget(btn_control_capture_traffic_for_time)
        btn_control_capture_traffic_for_time.clicked.connect(self.btn_time_capture_traffic_activated)
        btn_control_capture_traffic_for_time.setFixedWidth(400)

        back_to_control_traffic = QPushButton("Вернуться назад")
        self.addwid.addWidget(back_to_control_traffic)
        back_to_control_traffic.clicked.connect(self.create_body)
        back_to_control_traffic.setFixedWidth(400)

    def btn_time_capture_traffic_activated(self):

        actions = "Нажали на кнопку настроить захват трафика"
        write_logs.write_row(actions)

        var_name = self.dateEdit.dateTime()
        date_start = var_name.toPyDateTime()
        int_time = int(self.qle1.text())
        filename = str(self.qle2.text())
        period_time = self.combo1.currentText()
        int_cap = self.combo.currentText()
        period_capture = self.qle7.text()

        #print(date_start, int_time, period_time, int_cap, filename )

        #Удаление всех виджетов 
        for i in range(self.addwid.count()):
            self.addwid.itemAt(i).widget().deleteLater()

        text = "Захват трафика будет произведён"
        self.lbl = QLabel(text, self) 
        self.lbl.setFont(QFont('Serif', 16))
        self.addwid.addWidget(self.lbl)

        info_timer_text = str(f"Параметры:\n\
        1.Дата и время начала захвата\n\
            {date_start}\n\
        2.Период повторения захвата:\n\
            {int_time} {period_time}\n\
        3.Период захвата:\n\
            {period_capture}\n\
        4.Интерфейс:\n\
            {int_cap}\n\
        5.Имя сохранённого файла:\n\
            {filename}.pcap\n")

        self.lbl2 = QLabel(info_timer_text, self) 
        self.lbl2.setFont(QFont('Serif', 16))
        self.addwid.addWidget(self.lbl2)

        back_to_timer_traffic = QPushButton("Вернуться назад")
        self.addwid.addWidget(back_to_timer_traffic)
        back_to_timer_traffic.clicked.connect(self.btn_time_capture_traffic)
        back_to_timer_traffic.setFixedWidth(400)

        back_to_control_traffic = QPushButton("Вернуться в меню управления захвата трафиком")
        self.addwid.addWidget(back_to_control_traffic)
        back_to_control_traffic.clicked.connect(self.create_body)
        back_to_control_traffic.setFixedWidth(400)

    def create_body(self):

        form_frame = QFrame()
        form_frame.setFrameShape(QFrame.StyledPanel)
        form_frame.setMaximumWidth(300)
        
        p_push = QPushButton('Захват трафика')
        p_push.setContentsMargins(10, 20, 10, 10)
        p_push1 = QPushButton('Захват трафика по расписанию')
        p_push1.setContentsMargins(10, 40, 10, 30)
        
        p_push.clicked.connect(self.btn_capture_traffic)
        p_push1.clicked.connect(self.btn_time_capture_traffic)

        form_lay = QFormLayout()
        form_lay.addRow(p_push)
        form_lay.addRow(p_push1)
        form_frame.setLayout(form_lay)

        ver_frame = QFrame()
        ver_frame.setFrameShape(QFrame.StyledPanel)
        
        label = "Перехват трафика"
        self.addwid = QVBoxLayout()
        self.lbl = QLabel(label, self)
        self.lbl.setFont(QFont('Serif', 16))
        self.addwid.setContentsMargins(25, 40, 25, 40)
        self.addwid.addWidget(self.lbl)

        self.lbl5 = QLabel('Пример захваченного трафика после обработки',self)
        self.lbl5.setFont(QFont('Serif', 14))
        self.addwid.addWidget(self.lbl5)

        #Отрисовка таблицы
        text = 'Захваченный трафик'
        list_result = control_db.select_db()
        df = list_result[0]
        table_name = list_result[1]
        model = PdTable(df.head(15))
        self.table = QTableView()
        self.table.setModel(model)
        self.table.resize(410, 250)
        self.table.setWindowTitle(text)
        self.table.setAlternatingRowColors(True)
        self.table.show()
        self.addwid.addWidget(self.table)

        ver_frame.setLayout(self.addwid)

        splitter = QSplitter(Qt.Horizontal)
        splitter.addWidget(form_frame)
        splitter.addWidget(ver_frame)

        self.vbox = QVBoxLayout()
        self.vbox.addWidget(splitter)
        self.setCentralWidget(splitter)

class control_db_window(QMainWindow):

    def __init__(self):
        super().__init__()

        self.create_body()

    def btn_status_db(self):

        actions = "Перешли в раздел общее состояние БД"
        write_logs.write_row(actions)

        #Удаление всех виджетов         
        for i in range(self.addwid.count()):
            self.addwid.itemAt(i).widget().deleteLater()
        text = "Состояние всех таблиц"
        self.lbl = QLabel(text, self)
        self.lbl.setFont(QFont('Serif', 16))
        self.addwid.addWidget(self.lbl)

        self.btn_update_status_db = QPushButton("Обновить данные", self)
        self.addwid.addWidget(self.btn_update_status_db)
        self.btn_update_status_db.clicked.connect(self.update_table_status_db)
        self.btn_update_status_db.setFixedWidth(400)

        #Отрисовка таблицы
        df = control_db.status_db()
        model = PdTable(df)
        self.table = QTableView()
        self.table.setModel(model)
        self.table.resize(410, 250)
        self.table.setWindowTitle(text)
        self.table.setAlternatingRowColors(True)
        self.table.show()
        self.addwid.addWidget(self.table)


    def update_table_status_db(self):

        actions = "Обновили таблицу общее состояние БД"
        write_logs.write_row(actions)

        #Удаление всех виджетов         
        for i in range(self.addwid.count()):
            self.addwid.itemAt(i).widget().deleteLater()
        text = "Состояние всех таблиц"
        self.lbl = QLabel(text, self)
        self.lbl.setFont(QFont('Serif', 16))
        self.addwid.addWidget(self.lbl)

        self.btn_update_status_db = QPushButton("Обновить данные", self)
        self.addwid.addWidget(self.btn_update_status_db)
        self.btn_update_status_db.clicked.connect(self.update_table_status_db)
        self.btn_update_status_db.setFixedWidth(400)

        df = control_db.update_status_db()
        model = PdTable(df)
        self.table = QTableView()
        self.table.setModel(model)
        self.table.resize(410, 250)
        self.table.setWindowTitle(text)
        self.table.setAlternatingRowColors(True)
        self.table.show()
        self.addwid.addWidget(self.table)

    def btn_select_table(self):

        actions = "Перешли в раздел Посмотреть данные"
        write_logs.write_row(actions)

        text = "Выберите таблицу"
        
        #Удаление всех виджетов 
        for i in range(self.addwid.count()):
            self.addwid.itemAt(i).widget().deleteLater()

        self.lbl = QLabel(text, self)
        self.lbl.setFont(QFont('Serif', 16))
        self.addwid.addWidget(self.lbl)

        self.combo = QComboBox(self)
        self.combo.setFixedWidth(400)
        list_table_names = []
        tupple_names = control_db.db_names()
        for i in tupple_names:
            list_table_names.append(str(i)[2:-3])

        list_table_names.remove("logs")
        list_table_names.remove("info_for_tables")
        list_table_names.remove("info_for_tables_view")
        self.combo.addItems(list_table_names)
        self.addwid.addWidget(self.combo)
        self.btn_select_data = QPushButton("Выбрать данные", self)
        self.addwid.addWidget(self.btn_select_data)
        self.btn_select_data.clicked.connect(self.select_table_activated)
        self.btn_select_data.setFixedWidth(400)

        list_result = control_db.select_db()
        df = list_result[0]
        model = PdTable(df)
        self.table = QTableView()
        self.table.setModel(model)
        self.table.resize(410, 250)
        self.lbl2 = QLabel("Пример получаемой таблицы")
        self.lbl2.setFont(QFont('Serif', 12))
        self.addwid.addWidget(self.lbl2)
        self.table.setWindowTitle(text)
        self.table.setAlternatingRowColors(True)
        self.table.show()
        self.addwid.addWidget(self.table)

    def select_table_activated(self):

        actions = "Нажата кнопка выбрать данные"
        write_logs.write_row(actions)

        text = self.combo.currentText()
        list_db = control_db.select_db(text)
        df = list_db[0]
        text2 = list_db[1]

        #Удаление таблицы и label
        for i in range(self.addwid.count())[3:]:
            self.addwid.itemAt(i).widget().deleteLater() 

        #Отрисовка label
        self.lbl = QLabel(text2, self)
        self.lbl.setFont(QFont('Serif', 16))
        self.addwid.addWidget(self.lbl)

        #Отрисовка таблицы
        model = PdTable(df.head(1000))
        self.table = QTableView()
        self.table.setModel(model)
        self.table.resize(410, 250)
        self.table.setWindowTitle(text)
        self.table.setAlternatingRowColors(True)
        self.table.show()
        self.addwid.addWidget(self.table)

    def btn_create_table(self):
        
        actions = "Перешли в раздел Создать таблицу"
        write_logs.write_row(actions)

        text = "Введите название таблицы"
        
        for i in range(self.addwid.count()):
            self.addwid.itemAt(i).widget().deleteLater()
        self.qle = QLineEdit(self)
        table_name = self.qle.text()
        self.lbl = QLabel(text, self)
        self.lbl.setFont(QFont('Serif', 16))
        self.addwid.addWidget(self.lbl)

        create_text = "Название таблицы нужно вводить без пробелов\nПример: test_for_db"
        self.lbl3 = QLabel(create_text, self)
        self.lbl3.setFont(QFont('Serif', 14))
        self.addwid.addWidget(self.lbl3) 


        self.addwid.addWidget(self.qle)
        self.qle.setFixedWidth(400)
        self.btn_create = QPushButton("Создать таблицу", self)
        self.addwid.addWidget(self.btn_create)
        self.btn_create.clicked.connect(self.create_table_activate)
        self.btn_create.setFixedWidth(400)

    def create_table_activate(self):

        actions = "Нажали на кнпоку Создать таблицу"
        write_logs.write_row(actions)

        text = self.qle.text()
        control_db.create_table(text)
        label = str(f"Таблица {text} создана")
        for i in range(self.addwid.count())[1:]:
            self.addwid.itemAt(i).widget().deleteLater()
        self.qle.clear()
        self.lbl2 = QLabel(label, self)
        self.lbl2.setFont(QFont('Serif', 16))
        self.addwid.addWidget(self.lbl2)

        back_to_create_table = QPushButton("Вернуться назад")
        self.addwid.addWidget(back_to_create_table)
        back_to_create_table.clicked.connect(self.btn_create_table)
        back_to_create_table.setFixedWidth(400)

    def btn_insert_data(self):

        actions = "Перешли в раздел Обновить данные"
        write_logs.write_row(actions)

        text = "Панель управления \nобновлением данных"

        for i in range(self.addwid.count()):
            self.addwid.itemAt(i).widget().deleteLater()
        self.combo = QComboBox()
        self.combo1 = QComboBox()
        list_table_names = []
        tupple_names = control_db.db_names()
        for i in tupple_names:
            list_table_names.append(str(i)[2:-3])
        list_table_names.remove("logs")


        list_table_names.remove("info_for_tables")
        list_table_names.remove("info_for_tables_view")
        self.combo.addItems(list_table_names)
        files = actions_file.list_files()
        self.combo1.addItems(files)
        self.lbl = QLabel(text, self)
        self.lbl.setFont(QFont('Serif', 16))
        self.addwid.addWidget(self.lbl)
        self.addwid.addWidget(self.combo)
        self.addwid.addWidget(self.combo1)
        self.btn_insert_data = QPushButton("Загрузить данные", self)
        self.addwid.addWidget(self.btn_insert_data)
        self.btn_insert_data.clicked.connect(self.btn_insert_data_activated)
        self.combo.setFixedWidth(400)
        self.combo1.setFixedWidth(400)
        self.btn_insert_data.setFixedWidth(400)

    def btn_insert_data_activated(self):

        actions = "Нажата кнопка Загрузить данные"
        write_logs.write_row(actions)

        filename = self.combo1.currentText()
        table = self.combo.currentText()
        for i in range(self.addwid.count())[1:]:
            self.addwid.itemAt(i).widget().deleteLater()

        text = control_db.insert_(table, filename)
        label = str(f"Для таблицы {table} данные - {text}")
        self.lbl2 = QLabel(label, self)
        self.lbl2.setFont(QFont('Serif', 16))
        self.addwid.addWidget(self.lbl2)


    def btn_drop_table(self):

        actions = "Перешли в раздел Удалить таблицу"
        write_logs.write_row(actions)

        text = "Выберите название таблицы"
        for i in range(self.addwid.count()):
            self.addwid.itemAt(i).widget().deleteLater()
        self.combo = QComboBox()
        list_table_names = []
        tupple_names = control_db.db_names()
        for i in tupple_names:
            list_table_names.append(str(i)[2:-3])
        list_table_names.remove("logs")


        list_table_names.remove("info_for_tables")
        list_table_names.remove("info_for_tables_view")
        self.combo.addItems(list_table_names)
        self.btn_drop = QPushButton("Удалить таблицу", self)
        self.lbl = QLabel(text, self)
        self.lbl.setFont(QFont('Serif', 16))
        self.addwid.addWidget(self.lbl)

        #Подпись
        text_drop = "Помните, что при удалении таблицы,\nвсе данные удаляются навсегда"
        self.lbl2 = QLabel(text_drop, self)
        self.lbl2.setFont(QFont('Serif', 14))
        self.addwid.addWidget(self.lbl2)        

        self.addwid.addWidget(self.combo)
        self.addwid.addWidget(self.btn_drop)
        self.combo.setFixedWidth(400)
        self.btn_drop.clicked.connect(self.btn_drop_table_activated)
        self.btn_drop.setFixedWidth(400)

    def btn_drop_table_activated(self):

        actions = "Нажали на кнопку Удалить таблицу"
        write_logs.write_row(actions)

        text = self.combo.currentText()
        control_db.drop_table(text)
        text = str(f"Таблица {text} удалена")
        self.combo.clear()
        #Удаление всех виджетов 
        for i in range(self.addwid.count())[4:]:
            self.addwid.itemAt(i).widget().deleteLater()

        list_table_names = []
        tupple_names = control_db.db_names()
        for i in tupple_names:
            list_table_names.append(str(i)[2:-3])
        list_table_names.remove("logs")
        list_table_names.remove("info_for_tables")
        list_table_names.remove("info_for_tables_view")
        self.combo.addItems(list_table_names)

        self.lbl = QLabel(text, self)
        self.lbl.setFont(QFont('Serif', 16))
        self.addwid.addWidget(self.lbl)

    def btn_select_edit(self):
        actions = "Перешли в раздел создания своего запроса"
        write_logs.write_row(actions)

        text = "Раздел написания запросов в БД"
        for i in range(self.addwid.count()):
            self.addwid.itemAt(i).widget().deleteLater()

        self.lbl = QLabel(text, self)
        self.lbl.setFont(QFont('Serif', 16))
        self.addwid.addWidget(self.lbl)

        text_list = "Список таблиц"
        self.lbl2 = QLabel(text_list, self)
        self.lbl2.setFont(QFont('Serif', 12))
        self.addwid.addWidget(self.lbl2)

        list_table_names = []
        tupple_names = control_db.db_names()
        for i in tupple_names:
            list_table_names.append(str(i)[2:-3])
        list_table_names.remove("logs")
        list_table_names.remove("info_for_tables")
        list_table_names.remove("info_for_tables_view")

        self.combo = QComboBox(self)
        self.combo.addItems(list_table_names)
        self.combo.setFixedWidth(400)
        self.addwid.addWidget(self.combo)

        #Подпись
        text_drop = "Примеры запрсов к БД:\n\
        1. SELECT * FROM logs;\n\
        2. CREATE TABLE test;\n\
        3. INSERT INTO test (a,b,c) VALUES('a','b','c')\n\
        4. DROP TABLE test;\n"
        self.lbl4 = QLabel(text_drop, self)
        self.lbl4.setFont(QFont('Serif', 12))
        self.addwid.addWidget(self.lbl4)        

        self.qle = QLineEdit(self)
        self.qle.setFixedWidth(400)
        self.addwid.addWidget(self.qle)

        self.btn_select_activated = QPushButton("Отправить запрос", self)
        self.addwid.addWidget(self.btn_select_activated)
        self.btn_select_activated.clicked.connect(self.btn_select_edit_activated)
        self.btn_select_activated.setFixedWidth(400)

    def btn_select_edit_activated(self):

        actions = "Ввели свой запрос"
        write_logs.write_row(actions)
        
        sql_text = self.qle.text()

        for i in range(self.addwid.count()):
            self.addwid.itemAt(i).widget().deleteLater()

        text = "Раздел написания запросов в БД"
        self.lbl = QLabel(text, self)
        self.lbl.setFont(QFont('Serif', 16))
        self.addwid.addWidget(self.lbl)

        text2 = str(f"Результат вашего запроса - {sql_text}")
        self.lbl2 = QLabel(text2, self)
        self.lbl2.setFont(QFont('Serif', 14))
        self.addwid.addWidget(self.lbl2)

        df = control_db.our_sql_text(sql_text)

        #Отрисовка таблицы
        model = PdTable(df.head(1000))
        self.table = QTableView()
        self.table.setModel(model)
        self.table.resize(410, 250)
        self.table.setWindowTitle(text)
        self.table.setAlternatingRowColors(True)
        self.table.show()
        self.addwid.addWidget(self.table)

        back_to_create_sql = QPushButton("Вернуться назад")
        self.addwid.addWidget(back_to_create_sql)
        back_to_create_sql.clicked.connect(self.btn_select_edit)
        back_to_create_sql.setFixedWidth(400)        
        
        back_to_create_body = QPushButton("Вернуться в меню управления БД")
        self.addwid.addWidget(back_to_create_body)
        back_to_create_body.clicked.connect(self.create_body)
        back_to_create_body.setFixedWidth(400)
        
    def create_body(self):
        form_frame = QFrame()
        form_frame.setFrameShape(QFrame.StyledPanel)
        form_frame.setMinimumWidth(300)
        form_frame.setMaximumWidth(300)

        p_push = QPushButton('Общее состояние БД')
        p_push.setContentsMargins(10, 20, 10, 10)
        p_push1 = QPushButton('Посмотреть данные')
        p_push1.setContentsMargins(10, 40, 10, 30)
        p_push2 = QPushButton('Создать таблицу')
        p_push2.setContentsMargins(10, 60, 10, 50)
        p_push3 = QPushButton('Обновить данные')
        p_push3.setContentsMargins(10, 80, 10, 70)
        p_push4 = QPushButton('Удалить таблицу')
        p_push4.setContentsMargins(10, 80, 10, 70)
        p_push5 = QPushButton('Написать свой запрос')
        p_push5.setContentsMargins(10, 80, 10, 70)

        form_lay = QFormLayout()
        form_lay.addRow(p_push)
        form_lay.addRow(p_push1)
        form_lay.addRow(p_push2)
        form_lay.addRow(p_push3)
        form_lay.addRow(p_push4)
        form_lay.addRow(p_push5)
        form_frame.setLayout(form_lay)

        ver_frame = QFrame()
        ver_frame.setFrameShape(QFrame.StyledPanel)
        
        label = "Модуль управления БД"

        self.addwid = QVBoxLayout()
        self.lbl = QLabel(label, self)
        self.lbl.setFont(QFont('Serif', 16))
        self.addwid.setContentsMargins(25, 40, 25, 40)
        self.addwid.addWidget(self.lbl)
        ver_frame.setLayout(self.addwid)

        splitter = QSplitter(Qt.Horizontal)
        splitter.addWidget(form_frame)
        splitter.addWidget(ver_frame)

        p_push.clicked.connect(self.btn_status_db)
        p_push1.clicked.connect(self.btn_select_table)
        p_push2.clicked.connect(self.btn_create_table)
        p_push3.clicked.connect(self.btn_insert_data)
        p_push4.clicked.connect(self.btn_drop_table)
        p_push5.clicked.connect(self.btn_select_edit)

        self.vbox = QVBoxLayout()
        self.vbox.addWidget(splitter)
        self.setCentralWidget(splitter) 

class analyse_trafic_window(QMainWindow):

    def __init__(self):
        super().__init__()

        self.create_body()

    def btn_status_wifi(self):

        text = "Выберите таблицу"
        text2 = "Общее состояние беспроводной сети"
        
        actions = str(f"Перешли на страницу {text2}")
        write_logs.write_row(actions)

        #Удаление всех виджетов 
        for i in range(self.addwid.count()):
            self.addwid.itemAt(i).widget().deleteLater()

        self.lbl2 = QLabel(text2, self)
        self.lbl2.setFont(QFont('Serif', 16))
        self.addwid.addWidget(self.lbl2)
        self.lbl = QLabel(text, self)
        self.lbl.setFont(QFont('Serif', 14))
        self.addwid.addWidget(self.lbl)

        self.combo = QComboBox(self)
        list_table_names = []
        tupple_names = control_db.db_names()
        for i in tupple_names:
            list_table_names.append(str(i)[2:-3])
        list_table_names.remove("logs")


        list_table_names.remove("info_for_tables")
        list_table_names.remove("info_for_tables_view")
        self.combo.addItems(list_table_names)
        self.addwid.addWidget(self.combo)
        self.btn_select_data = QPushButton("Выбрать данные", self)
        self.addwid.addWidget(self.btn_select_data)
        self.btn_select_data.clicked.connect(self.main_status_wifi_activated)

        table_name = str(list_table_names[0])
        df = analyser.main_stat_traffic(table_name)
        model = PdTable(df)
        self.table = QTableView()
        self.table.setModel(model)
        self.table.resize(410, 250)
        self.lbl2 = QLabel("Пример получаемой таблицы")
        self.lbl2.setFont(QFont('Serif', 12))
        self.addwid.addWidget(self.lbl2)
        self.table.setWindowTitle(text)
        self.table.setAlternatingRowColors(True)
        self.table.show()
        self.addwid.addWidget(self.table)

    def main_status_wifi_activated(self):

        actions = str("Нажата кнопка выбора таблицы")
        write_logs.write_row(actions)


        #Удаление таблицы и label
        for i in range(self.addwid.count())[4:]:
            self.addwid.itemAt(i).widget().deleteLater() 
        
        text = self.combo.currentText()
        df = analyser.main_stat_traffic(text)
        text2 = str(f"Выбрана таблица {text}")

        #Отрисовка label
        self.lbl = QLabel(text2, self)
        self.lbl.setFont(QFont('Serif', 16))
        self.addwid.addWidget(self.lbl)

        #Отрисовка таблицы
        model = PdTable(df)
        self.table = QTableView()
        self.table.setModel(model)
        self.table.resize(410, 250)
        self.table.setWindowTitle(text)
        self.table.setAlternatingRowColors(True)
        self.table.show()
        self.addwid.addWidget(self.table)

    def btn_retry(self):
        
        text = "Выберите таблицу"
        text2 = "Статистика retry пакетов в сети"

        actions = str(f"Перешли на страницу {text2}")
        write_logs.write_row(actions)
        
        #Удаление всех виджетов 
        for i in range(self.addwid.count()):
            self.addwid.itemAt(i).widget().deleteLater()

        self.lbl2 = QLabel(text2, self)
        self.lbl2.setFont(QFont('Serif', 16))
        self.addwid.addWidget(self.lbl2)
        self.lbl = QLabel(text, self)
        self.lbl.setFont(QFont('Serif', 14))
        self.addwid.addWidget(self.lbl)

        self.combo = QComboBox(self)
        list_table_names = []
        tupple_names = control_db.db_names()
        for i in tupple_names:
            list_table_names.append(str(i)[2:-3])
        list_table_names.remove("logs")


        list_table_names.remove("info_for_tables")
        list_table_names.remove("info_for_tables_view")
        self.combo.addItems(list_table_names)
        self.addwid.addWidget(self.combo)
        self.btn_select_data = QPushButton("Выбрать данные", self)
        self.addwid.addWidget(self.btn_select_data)
        self.btn_select_data.clicked.connect(self.select_table_retry)

        list_result = control_db.select_db()
        df = list_result[0]
        model = PdTable(df)
        self.table = QTableView()
        self.table.setModel(model)
        self.table.resize(410, 250)
        self.lbl2 = QLabel("Пример получаемой таблицы")
        self.lbl2.setFont(QFont('Serif', 12))
        self.addwid.addWidget(self.lbl2)
        self.table.setWindowTitle(text)
        self.table.setAlternatingRowColors(True)
        self.table.show()
        self.addwid.addWidget(self.table)

    def select_table_retry(self):

        actions = str("Нажата кнопка выбора таблицы")
        write_logs.write_row(actions)

        text = self.combo.currentText()
        list_db = control_db.select_db(text)
        df = list_db[0]
        text2 = list_db[1]

        #Удаление таблицы и label
        for i in range(self.addwid.count())[4:]:
            self.addwid.itemAt(i).widget().deleteLater() 

        #Отрисовка label
        self.lbl = QLabel(text2, self)
        self.lbl.setFont(QFont('Serif', 16))
        self.addwid.addWidget(self.lbl)

        #Отрисовка таблицы
        model = PdTable(df)
        self.table = QTableView()
        self.table.setModel(model)
        self.table.resize(410, 250)
        self.table.setWindowTitle(text)
        self.table.setAlternatingRowColors(True)
        self.table.show()
        self.addwid.addWidget(self.table)

    def btn_ddos(self):
        
        text = "Выберите таблицу"
        text2 = "Вероятные DDoS атаки"

        actions = str(f"Перешли на страницу {text2}")
        write_logs.write_row(actions)
        
        #Удаление всех виджетов 
        for i in range(self.addwid.count()):
            self.addwid.itemAt(i).widget().deleteLater()

        self.lbl2 = QLabel(text2, self)
        self.lbl2.setFont(QFont('Serif', 16))
        self.addwid.addWidget(self.lbl2)
        self.lbl = QLabel(text, self)
        self.lbl.setFont(QFont('Serif', 14))
        self.addwid.addWidget(self.lbl)

        self.combo = QComboBox(self)
        list_table_names = []
        tupple_names = control_db.db_names()
        for i in tupple_names:
            list_table_names.append(str(i)[2:-3])
        list_table_names.remove("logs")


        list_table_names.remove("info_for_tables")
        list_table_names.remove("info_for_tables_view")
        self.combo.addItems(list_table_names)
        self.addwid.addWidget(self.combo)
        self.btn_select_data = QPushButton("Выбрать данные", self)
        self.addwid.addWidget(self.btn_select_data)
        self.btn_select_data.clicked.connect(self.select_table_ddos)

        list_result = control_db.select_db()
        df = list_result[0]
        model = PdTable(df)
        self.table = QTableView()
        self.table.setModel(model)
        self.table.resize(410, 250)
        self.lbl2 = QLabel("Пример получаемой таблицы")
        self.lbl2.setFont(QFont('Serif', 12))
        self.addwid.addWidget(self.lbl2)
        self.table.setWindowTitle(text)
        self.table.setAlternatingRowColors(True)
        self.table.show()
        self.addwid.addWidget(self.table)

    def select_table_ddos(self):

        actions = str("Нажата кнопка выбора таблицы")
        write_logs.write_row(actions)

        text = self.combo.currentText()
        list_db = control_db.select_db(text)
        df = list_db[0]
        text2 = list_db[1]

        #Удаление таблицы и label
        for i in range(self.addwid.count())[4:]:
            self.addwid.itemAt(i).widget().deleteLater() 

        #Отрисовка label
        self.lbl = QLabel(text2, self)
        self.lbl.setFont(QFont('Serif', 16))
        self.addwid.addWidget(self.lbl)

        #Отрисовка таблицы
        model = PdTable(df)
        self.table = QTableView()
        self.table.setModel(model)
        self.table.resize(410, 250)
        self.table.setWindowTitle(text)
        self.table.setAlternatingRowColors(True)
        self.table.show()
        self.addwid.addWidget(self.table)

    def btn_anomalyies_on_wifi(self):
        
        text = "Выберите таблицу"
        text2 = "Выявленные аномилии в беспроводной сети"

        actions = str(f"Перешли на страницу {text2}")
        write_logs.write_row(actions)
        
        #Удаление всех виджетов 
        for i in range(self.addwid.count()):
            self.addwid.itemAt(i).widget().deleteLater()

        self.lbl2 = QLabel(text2, self)
        self.lbl2.setFont(QFont('Serif', 16))
        self.addwid.addWidget(self.lbl2)
        self.lbl = QLabel(text, self)
        self.lbl.setFont(QFont('Serif', 14))
        self.addwid.addWidget(self.lbl)

        self.combo = QComboBox(self)
        list_table_names = []
        tupple_names = control_db.db_names()
        for i in tupple_names:
            list_table_names.append(str(i)[2:-3])
        list_table_names.remove("logs")


        list_table_names.remove("info_for_tables")
        list_table_names.remove("info_for_tables_view")
        self.combo.addItems(list_table_names)
        self.addwid.addWidget(self.combo)
        self.btn_select_data = QPushButton("Выбрать данные", self)
        self.addwid.addWidget(self.btn_select_data)
        self.btn_select_data.clicked.connect(self.select_table_anomalyies)

        list_result = control_db.select_db()
        df = list_result[0]
        model = PdTable(df)
        self.table = QTableView()
        self.table.setModel(model)
        self.table.resize(410, 250)
        self.lbl2 = QLabel("Пример получаемой таблицы")
        self.lbl2.setFont(QFont('Serif', 12))
        self.addwid.addWidget(self.lbl2)
        self.table.setWindowTitle(text)
        self.table.setAlternatingRowColors(True)
        self.table.show()
        self.addwid.addWidget(self.table)

    def select_table_anomalyies(self):

        actions = str("Нажата кнопка выбора таблицы")
        write_logs.write_row(actions)

        text = self.combo.currentText()
        list_db = control_db.select_db(text)
        df = list_db[0]
        text2 = list_db[1]

        #Удаление таблицы и label
        for i in range(self.addwid.count())[4:]:
            self.addwid.itemAt(i).widget().deleteLater() 

        #Отрисовка label
        self.lbl = QLabel(text2, self)
        self.lbl.setFont(QFont('Serif', 16))
        self.addwid.addWidget(self.lbl)

        #Отрисовка таблицы
        model = PdTable(df)
        self.table = QTableView()
        self.table.setModel(model)
        self.table.resize(410, 250)
        self.table.setWindowTitle(text)
        self.table.setAlternatingRowColors(True)
        self.table.show()
        self.addwid.addWidget(self.table)

    def create_body(self):
        form_frame = QFrame()
        form_frame.setFrameShape(QFrame.StyledPanel)
        form_frame.setMinimumWidth(300)
        form_frame.setMaximumWidth(300)

        p_push = QPushButton('Общее состояние сети')
        p_push.setContentsMargins(10, 20, 10, 10)
        p_push1 = QPushButton('Возвраты')
        p_push1.setContentsMargins(10, 40, 10, 30)
        p_push2 = QPushButton('DDOS')
        p_push2.setContentsMargins(10, 60, 10, 50)
        p_push3 = QPushButton('Подозрительная активность')
        p_push3.setContentsMargins(10, 80, 10, 70)

        form_lay = QFormLayout()
        form_lay.addRow(p_push)
        form_lay.addRow(p_push1)
        form_lay.addRow(p_push2)
        form_lay.addRow(p_push3)
        form_frame.setLayout(form_lay)

        ver_frame = QFrame()
        ver_frame.setFrameShape(QFrame.StyledPanel)
        self.plb = QLabel("Управление анализом трафика")
        self.plb.setFont(QFont('Serif', 16))

        self.addwid = QVBoxLayout()
        self.addwid.setContentsMargins(25, 20, 25, 25)        
        self.addwid.addWidget(self.plb)
        ver_frame.setLayout(self.addwid)

        splitter = QSplitter(Qt.Horizontal)
        splitter.addWidget(form_frame)
        splitter.addWidget(ver_frame)

        self.vbox = QVBoxLayout()
        self.vbox.addWidget(splitter)
        self.setCentralWidget(splitter)

        p_push.clicked.connect(self.btn_status_wifi)
        p_push1.clicked.connect(self.btn_retry)
        p_push2.clicked.connect(self.btn_ddos)
        p_push3.clicked.connect(self.btn_anomalyies_on_wifi)

class develop_widgets_window(QMainWindow):
    
    def __init__(self):
        super().__init__()

        self.create_body()

    def btn_bar_(self):
        actions = str("Нажата кнопка Столбчатая диаграмма")
        write_logs.write_row(actions)

        #Удаление всех виджетов 
        for i in range(self.addwid.count()):
            self.addwid.itemAt(i).widget().deleteLater()

        self.lbl = QLabel("Построение столбчатой диаграммы")
        self.lbl.setFont(QFont('Serif', 16))
        self.addwid.addWidget(self.lbl)

        self.lbl2 = QLabel("Выберите таблицу")
        self.lbl2.setFont(QFont('Serif', 14))
        self.addwid.addWidget(self.lbl2)
        self.combo = QComboBox(self)
        self.list_table_names = []
        tupple_names = control_db.db_names()
        for i in tupple_names:
            self.list_table_names.append(str(i)[2:-3])
        self.list_table_names.remove("logs")
        self.list_table_names.remove("info_for_tables")
        self.list_table_names.remove("info_for_tables_view")
        self.combo.addItems(self.list_table_names)
        self.combo.setFixedWidth(400)
        self.addwid.addWidget(self.combo)

        self.button2 = QPushButton('Выбрать таблицу', self)
        self.button2.setFixedWidth(400)
        self.button2.clicked.connect(self.btn2_activated)
        self.addwid.addWidget(self.button2)        


        self.button1 = QPushButton('Вернуться назад', self)
        self.button1.setFixedWidth(400)
        self.button1.clicked.connect(self.create_body)
        self.addwid.addWidget(self.button1)

    def btn2_activated(self):

        try:
            actions = str("Выбрали таблицу для Столбчатой диаграммы")
            write_logs.write_row(actions)
            self.table_name = self.combo.currentText()
        except:
            actions = str("Редактирование Столбчатой диаграммы")
            write_logs.write_row(actions)
            self.table_name = self.table_name2

        #Удаление всех виджетов 
        for i in range(self.addwid.count())[1:]:
            self.addwid.itemAt(i).widget().deleteLater()

        self.lbl2 = QLabel(f"Выбрана таблица - {self.table_name}")
        self.lbl2.setFont(QFont('Serif', 14))
        self.addwid.addWidget(self.lbl2)

        self.lbl3 = QLabel("Выберите поле для группировки")
        self.lbl3.setFont(QFont('Serif', 14))
        self.addwid.addWidget(self.lbl3)
        self.select_unique_columns = control_db.select_unique_columns(\
            self.table_name)
        self.select_unique_columns_float = \
        control_db.select_unique_columns_float(self.table_name)

        self.combo1 = QComboBox(self)
        self.combo1.addItems(self.select_unique_columns)
        self.combo1.setFixedWidth(400)
        self.addwid.addWidget(self.combo1)

        self.lbl5 = QLabel("Выберите поле для метрики")
        self.lbl5.setFont(QFont('Serif', 14))
        self.addwid.addWidget(self.lbl5)
        self.combo3 = QComboBox(self)
        self.combo3.addItems(self.select_unique_columns_float)
        self.combo3.setFixedWidth(400)
        self.addwid.addWidget(self.combo3)        

        self.lbl4 = QLabel("Выберите агрегатную функцию")
        self.lbl4.setFont(QFont('Serif', 14))
        self.addwid.addWidget(self.lbl4)
        self.list_aggr_func = ['nunique','count','sum','mean','median','min','max','std']
        self.combo2 = QComboBox(self)
        self.combo2.addItems(self.list_aggr_func)
        self.combo2.setFixedWidth(400)
        self.addwid.addWidget(self.combo2)

        self.button2 = QPushButton('Построить граф', self)
        self.button2.setFixedWidth(400)
        self.button2.clicked.connect(self.btn_build_graph)
        self.addwid.addWidget(self.button2)        

        self.button1 = QPushButton('Вернуться  к выбору таблицы', self)
        self.button1.setFixedWidth(400)
        self.button1.clicked.connect(self.btn_bar_)
        self.addwid.addWidget(self.button1)

        self.button2 = QPushButton('Вернуться в главное меню дашбордов', self)
        self.button2.setFixedWidth(400)
        self.button2.clicked.connect(self.create_body)
        self.addwid.addWidget(self.button2)

    def btn_build_graph(self):

        actions = str("Построили Столбчатую диаграмму")
        write_logs.write_row(actions)
        
        agg_value = self.combo1.currentText()
        choise_func = self.combo2.currentText()
        choise_metrics = self.combo3.currentText()
        
        table_name = self.table_name

        #Удаление всех виджетов 
        for i in range(self.addwid.count()):
            self.addwid.itemAt(i).widget().deleteLater()

        self.table_name2 = table_name

        df = control_db.select_db(table_name)[0]

        self.lbl = QLabel("Столбчатая диаграмма")
        self.lbl.setFont(QFont('Serif', 16))
        self.addwid.addWidget(self.lbl)

        grouped = df.groupby(agg_value, as_index=False).\
        agg({choise_metrics:choise_func})
        grouped = grouped.sort_values(agg_value, ascending=False)
        
        try:
            fig = px.bar(x = grouped[agg_value], \
                y = grouped[choise_metrics], \
                title=str(f"Диаграмма по распределени {choise_func}:{choise_metrics}"))
        except:
            fig = px.bar( x = srez['Флаг'], y = srez['Количество'],\
                title='2')
        
        self.browser = QtWebEngineWidgets.QWebEngineView(self)
        self.browser.setFixedSize(650,450)
        fig.update_traces()#quartilemethod="inclusive")
        self.browser.setHtml(fig.to_html(include_plotlyjs='cdn'))
        self.browser.show()
        self.addwid.addWidget(self.browser)

        self.button1 = QPushButton('Изменить параметры диаграммы', self)
        self.button1.setFixedWidth(400)
        self.button1.clicked.connect(self.btn2_activated)
        self.addwid.addWidget(self.button1)

        self.button2 = QPushButton('Построить новую столбчатую диаграмму', self)
        self.button2.setFixedWidth(400)
        self.button2.clicked.connect(self.btn_bar_)
        self.addwid.addWidget(self.button2)

        self.button4 = QPushButton('Вернуться в главное меню дашбордов', self)
        self.button4.setFixedWidth(400)
        self.button4.clicked.connect(self.create_body)
        self.addwid.addWidget(self.button4)

    def btn_table(self):

        actions = str("Нажата кнопка Таблица")
        write_logs.write_row(actions)

        actions = str("btn_table")
        write_logs.write_row(actions)

        #Удаление всех виджетов 
        for i in range(self.addwid.count()):
            self.addwid.itemAt(i).widget().deleteLater()

        self.lbl = QLabel("Построение Таблицы")
        self.lbl.setFont(QFont('Serif', 16))
        self.addwid.addWidget(self.lbl)

        self.lbl2 = QLabel("Выберите таблицу")
        self.lbl2.setFont(QFont('Serif', 14))
        self.addwid.addWidget(self.lbl2)
        self.combo = QComboBox(self)
        self.list_table_names = []
        tupple_names = control_db.db_names()
        for i in tupple_names:
            self.list_table_names.append(str(i)[2:-3])
        self.list_table_names.remove("logs")
        self.list_table_names.remove("info_for_tables")
        self.list_table_names.remove("info_for_tables_view")
        self.combo.addItems(self.list_table_names)
        self.combo.setFixedWidth(400)
        self.addwid.addWidget(self.combo)

        self.button2 = QPushButton('Выбрать таблицу', self)
        self.button2.setFixedWidth(400)
        self.button2.clicked.connect(self.btn2_activated_table)
        self.addwid.addWidget(self.button2)        

        self.button1 = QPushButton('Вернуться назад', self)
        self.button1.setFixedWidth(400)
        self.button1.clicked.connect(self.create_body)
        self.addwid.addWidget(self.button1)

    def btn2_activated_table(self):

        actions = str("Выбрана таблица для Таблицы")
        write_logs.write_row(actions)

        try:
            self.table_name = self.combo.currentText()
        except:
            self.table_name = self.table_name2

        #Удаление всех виджетов 
        for i in range(self.addwid.count())[1:]:
            self.addwid.itemAt(i).widget().deleteLater()

        self.lbl2 = QLabel(f"Выбрана таблица - {self.table_name}")
        self.lbl2.setFont(QFont('Serif', 14))
        self.addwid.addWidget(self.lbl2)

        self.lbl3 = QLabel("Выберите поле для группировки")
        self.lbl3.setFont(QFont('Serif', 14))
        self.addwid.addWidget(self.lbl3)
        self.select_unique_columns = control_db.select_unique_columns(\
            self.table_name)
        self.select_unique_columns_float = \
        control_db.select_unique_columns_float(self.table_name)

        self.combo1 = QComboBox(self)
        self.combo1.addItems(self.select_unique_columns)
        self.combo1.setFixedWidth(400)
        self.addwid.addWidget(self.combo1)

        self.lbl5 = QLabel("Выберите поле для метрики")
        self.lbl5.setFont(QFont('Serif', 14))
        self.addwid.addWidget(self.lbl5)
        self.combo3 = QComboBox(self)
        self.combo3.addItems(self.select_unique_columns_float)
        self.combo3.setFixedWidth(400)
        self.addwid.addWidget(self.combo3)        

        self.lbl4 = QLabel("Выберите агрегатную функцию")
        self.lbl4.setFont(QFont('Serif', 14))
        self.addwid.addWidget(self.lbl4)
        self.list_aggr_func = ['nunique','count','sum','mean','median','min','max','std']
        self.combo2 = QComboBox(self)
        self.combo2.addItems(self.list_aggr_func)
        self.combo2.setFixedWidth(400)
        self.addwid.addWidget(self.combo2)

        self.button2 = QPushButton('Построить таблицу', self)
        self.button2.setFixedWidth(400)
        #self.button2.clicked.connect(self.btn_build_graph)
        self.addwid.addWidget(self.button2)        

        self.button1 = QPushButton('Вернуться  к выбору таблицы', self)
        self.button1.setFixedWidth(400)
        self.button1.clicked.connect(self.btn_table)
        self.addwid.addWidget(self.button1)

        self.button2 = QPushButton('Вернуться в главное меню дашбордов', self)
        self.button2.setFixedWidth(400)
        self.button2.clicked.connect(self.create_body)
        self.addwid.addWidget(self.button2)

    def btn_pie_chart(self):
        actions = str("Нажата кнопка Круговая диаграмма")
        write_logs.write_row(actions)

        #Удаление всех виджетов 
        for i in range(self.addwid.count()):
            self.addwid.itemAt(i).widget().deleteLater()

        self.lbl = QLabel("Построение круговой диаграммы")
        self.lbl.setFont(QFont('Serif', 16))
        self.addwid.addWidget(self.lbl)

        self.lbl2 = QLabel("Выберите таблицу")
        self.lbl2.setFont(QFont('Serif', 14))
        self.addwid.addWidget(self.lbl2)
        self.combo = QComboBox(self)
        self.list_table_names = []
        tupple_names = control_db.db_names()
        for i in tupple_names:
            self.list_table_names.append(str(i)[2:-3])
        self.list_table_names.remove("logs")
        self.list_table_names.remove("info_for_tables")
        self.list_table_names.remove("info_for_tables_view")
        self.combo.addItems(self.list_table_names)
        self.combo.setFixedWidth(400)
        self.addwid.addWidget(self.combo)

        self.button2 = QPushButton('Выбрать таблицу', self)
        self.button2.setFixedWidth(400)
        self.button2.clicked.connect(self.btn2_activated_pie)
        self.addwid.addWidget(self.button2)        

        self.button1 = QPushButton('Вернуться назад', self)
        self.button1.setFixedWidth(400)
        self.button1.clicked.connect(self.create_body)
        self.addwid.addWidget(self.button1)

    def btn2_activated_pie(self):

        try:
            actions = str("Выбрана таблица для Круговой диаграммы")
            write_logs.write_row(actions)
            self.table_name = self.combo.currentText()
        except:
            actions = str("Редактирование круговой диаграммы")
            write_logs.write_row(actions)
            self.table_name = self.table_name2

        #Удаление всех виджетов 
        for i in range(self.addwid.count())[1:]:
            self.addwid.itemAt(i).widget().deleteLater()

        self.lbl2 = QLabel(f"Выбрана таблица - {self.table_name}")
        self.lbl2.setFont(QFont('Serif', 14))
        self.addwid.addWidget(self.lbl2)

        self.lbl3 = QLabel("Выберите поле для группировки")
        self.lbl3.setFont(QFont('Serif', 14))
        self.addwid.addWidget(self.lbl3)
        self.select_unique_columns = control_db.select_unique_columns(\
            self.table_name)
        self.select_unique_columns_float = \
        control_db.select_unique_columns_float(self.table_name)

        self.combo1 = QComboBox(self)
        self.combo1.addItems(self.select_unique_columns)
        self.combo1.setFixedWidth(400)
        self.addwid.addWidget(self.combo1)

        self.lbl5 = QLabel("Выберите поле для метрики")
        self.lbl5.setFont(QFont('Serif', 14))
        self.addwid.addWidget(self.lbl5)
        self.combo3 = QComboBox(self)
        self.combo3.addItems(self.select_unique_columns_float)
        self.combo3.setFixedWidth(400)
        self.addwid.addWidget(self.combo3)        

        self.lbl4 = QLabel("Выберите агрегатную функцию")
        self.lbl4.setFont(QFont('Serif', 14))
        self.addwid.addWidget(self.lbl4)
        self.list_aggr_func = ['nunique','count','sum','mean','median','min','max','std']
        self.combo2 = QComboBox(self)
        self.combo2.addItems(self.list_aggr_func)
        self.combo2.setFixedWidth(400)
        self.addwid.addWidget(self.combo2)

        self.button2 = QPushButton('Построить граф', self)
        self.button2.setFixedWidth(400)
        self.button2.clicked.connect(self.btn_build_pie)
        self.addwid.addWidget(self.button2)        

        self.button1 = QPushButton('Вернуться  к выбору таблицы', self)
        self.button1.setFixedWidth(400)
        self.button1.clicked.connect(self.btn_bar_)
        self.addwid.addWidget(self.button1)

        self.button2 = QPushButton('Вернуться в главное меню дашбордов', self)
        self.button2.setFixedWidth(400)
        self.button2.clicked.connect(self.create_body)
        self.addwid.addWidget(self.button2)

    def btn_build_pie(self):
        
        actions = str("Построили Круговую диаграмму")
        write_logs.write_row(actions)

        agg_value = self.combo1.currentText()
        choise_func = self.combo2.currentText()
        choise_metrics = self.combo3.currentText()
        
        table_name = self.table_name

        #Удаление всех виджетов 
        for i in range(self.addwid.count()):
            self.addwid.itemAt(i).widget().deleteLater()

        self.table_name2 = table_name

        df = control_db.select_db(table_name)[0]

        self.lbl = QLabel("Круговая диаграмма")
        self.lbl.setFont(QFont('Serif', 16))
        self.addwid.addWidget(self.lbl)

        grouped = df.groupby(agg_value, as_index=False).\
        agg({choise_metrics:choise_func})
        grouped = grouped.sort_values(agg_value, ascending=False)
        
        try:
            fig = go.Figure()
            fig.add_trace(go.Pie(values=grouped[choise_metrics], \
                labels=grouped[agg_value],\
                hole=0.9))
            fig.update_layout(
                title = (f"Диаграмма по распределени {choise_func}:{choise_metrics}"),
                )
        except:
            df = px.data.gapminder().query("year == 2007").\
            query("continent == 'Europe'")
            srez = df.sort_values('pop', ascending=False).head(10).copy().\
            reset_index(drop=True)
            abs_sum_pop = round(df['pop'].sum()/10**6,2)
            choise_sum_pop = round(srez['pop'].sum()/10**6,2)
            text = str(f"    Всего : {abs_sum_pop} млн.<br>\
            Выбрано: {choise_sum_pop} млн.")
            del df

            fig = go.Figure()
            fig.add_trace(go.Pie(values=srez['pop'], labels=srez['country'],\
                hole=0.9))
            fig.update_layout(
                title = "Пример круговой диаграммы",
                annotations=[dict(text=text,x=0.5, y=0.5, \
                    showarrow=False)])
        
        self.browser = QtWebEngineWidgets.QWebEngineView(self)
        self.browser.setFixedSize(650,450)
        fig.update_traces()#quartilemethod="inclusive")
        self.browser.setHtml(fig.to_html(include_plotlyjs='cdn'))
        self.browser.show()
        self.addwid.addWidget(self.browser)

        self.button1 = QPushButton('Изменить параметры диаграммы', self)
        self.button1.setFixedWidth(400)
        self.button1.clicked.connect(self.btn2_activated_pie)
        self.addwid.addWidget(self.button1)

        self.button2 = QPushButton('Построить новую круговую диаграмму', self)
        self.button2.setFixedWidth(400)
        self.button2.clicked.connect(self.btn_pie_chart)
        self.addwid.addWidget(self.button2)

        self.button4 = QPushButton('Вернуться в главное меню дашбордов', self)
        self.button4.setFixedWidth(400)
        self.button4.clicked.connect(self.create_body)
        self.addwid.addWidget(self.button4)

    def btn_hist(self):
        actions = str("Нажата кнопка Гистограмма")
        write_logs.write_row(actions)

        #Удаление всех виджетов 
        for i in range(self.addwid.count()):
            self.addwid.itemAt(i).widget().deleteLater()

        self.lbl = QLabel("Построение гистограммы")
        self.lbl.setFont(QFont('Serif', 16))
        self.addwid.addWidget(self.lbl)

        self.lbl2 = QLabel("Выберите таблицу")
        self.lbl2.setFont(QFont('Serif', 14))
        self.addwid.addWidget(self.lbl2)
        self.combo = QComboBox(self)
        self.list_table_names = []
        tupple_names = control_db.db_names()
        for i in tupple_names:
            self.list_table_names.append(str(i)[2:-3])
        self.list_table_names.remove("logs")
        self.list_table_names.remove("info_for_tables")
        self.list_table_names.remove("info_for_tables_view")
        self.combo.addItems(self.list_table_names)
        self.combo.setFixedWidth(400)
        self.addwid.addWidget(self.combo)

        self.button2 = QPushButton('Выбрать таблицу', self)
        self.button2.setFixedWidth(400)
        self.button2.clicked.connect(self.btn2_activated_hist)
        self.addwid.addWidget(self.button2)        

        self.button1 = QPushButton('Вернуться назад', self)
        self.button1.setFixedWidth(400)
        self.button1.clicked.connect(self.create_body)
        self.addwid.addWidget(self.button1)

    def btn2_activated_hist(self):
        try:
            actions = str("Выбрана таблица для Гистограммы")
            write_logs.write_row(actions)
            self.table_name = self.combo.currentText()
        except:
            actions = str("Редактирование Гистограммы")
            write_logs.write_row(actions)
            self.table_name = self.table_name2

        #Удаление всех виджетов 
        for i in range(self.addwid.count()):
            self.addwid.itemAt(i).widget().deleteLater()

        self.lbl2 = QLabel(f"Выбрана таблица - {self.table_name}")
        self.lbl2.setFont(QFont('Serif', 14))
        self.addwid.addWidget(self.lbl2)

        self.lbl3 = QLabel("Выберите поле для группировки")
        self.lbl3.setFont(QFont('Serif', 14))
        self.addwid.addWidget(self.lbl3)
        self.select_unique_columns = control_db.select_unique_columns(\
            self.table_name)
        self.select_unique_columns_float = \
        control_db.select_unique_columns_float(self.table_name)

        self.combo1 = QComboBox(self)
        self.combo1.addItems(self.select_unique_columns)
        self.combo1.setFixedWidth(400)
        self.addwid.addWidget(self.combo1)

        self.button2 = QPushButton('Построить граф', self)
        self.button2.setFixedWidth(400)
        self.button2.clicked.connect(self.btn_build_hist)
        self.addwid.addWidget(self.button2)        

        self.button1 = QPushButton('Вернуться  к выбору таблицы', self)
        self.button1.setFixedWidth(400)
        self.button1.clicked.connect(self.btn2_activated_hist)
        self.addwid.addWidget(self.button1)

        self.button2 = QPushButton('Вернуться в главное меню дашбордов', self)
        self.button2.setFixedWidth(400)
        self.button2.clicked.connect(self.create_body)
        self.addwid.addWidget(self.button2)

    def btn_build_hist(self):

        actions = str("Построили Гистограмму")
        write_logs.write_row(actions)
        
        agg_value = self.combo1.currentText()
        
        table_name = self.table_name

        #Удаление всех виджетов 
        for i in range(self.addwid.count()):
            self.addwid.itemAt(i).widget().deleteLater()

        self.table_name2 = table_name

        df = control_db.select_db(table_name)[0]

        self.lbl = QLabel("Гистограмма")
        self.lbl.setFont(QFont('Serif', 16))
        self.addwid.addWidget(self.lbl)

        try:
            grouped = df[agg_value].to_frame().copy()
            del df
        except:
            grouped = pd.DataFrame()
            grouped[agg_value] = [0,0]
            del df

        try:
            fig = go.Figure(data=[go.Histogram(x=grouped[agg_value])])
            fig.update_layout(
                title = f"Гистограммы по полю {agg_value}")
        except:
            dices = pd.DataFrame(np.random.randint(low=1, high=7, size=(100,2)),\
                columns=('1','2'))
            dices['сумма'] = dices['1'] + dices['2']
            fig = go.Figure(data=[go.Histogram(x=dices['сумма'])])
            fig.update_layout(
                title = "Пример гистограммы")
        
        self.browser = QtWebEngineWidgets.QWebEngineView(self)
        self.browser.setFixedSize(650,450)
        fig.update_traces()#quartilemethod="inclusive")
        self.browser.setHtml(fig.to_html(include_plotlyjs='cdn'))
        self.browser.show()
        self.addwid.addWidget(self.browser)

        self.button1 = QPushButton('Изменить параметры диаграммы', self)
        self.button1.setFixedWidth(400)
        self.button1.clicked.connect(self.btn2_activated_hist)
        self.addwid.addWidget(self.button1)

        self.button2 = QPushButton('Построить новую гистограмму', self)
        self.button2.setFixedWidth(400)
        self.button2.clicked.connect(self.btn_hist)
        self.addwid.addWidget(self.button2)

        self.button4 = QPushButton('Вернуться в главное меню дашбордов', self)
        self.button4.setFixedWidth(400)
        self.button4.clicked.connect(self.create_body)
        self.addwid.addWidget(self.button4)

    def btn_scatter(self):
        actions = str("Нажата кнопка Линейный график")
        write_logs.write_row(actions)

        #Удаление всех виджетов 
        for i in range(self.addwid.count()):
            self.addwid.itemAt(i).widget().deleteLater()

        self.lbl = QLabel("Построение линейного графика")
        self.lbl.setFont(QFont('Serif', 16))
        self.addwid.addWidget(self.lbl)

        self.lbl2 = QLabel("Выберите таблицу")
        self.lbl2.setFont(QFont('Serif', 14))
        self.addwid.addWidget(self.lbl2)
        self.combo = QComboBox(self)
        self.list_table_names = []
        tupple_names = control_db.db_names()
        for i in tupple_names:
            self.list_table_names.append(str(i)[2:-3])
        self.list_table_names.remove("logs")
        self.list_table_names.remove("info_for_tables")
        self.list_table_names.remove("info_for_tables_view")
        self.combo.addItems(self.list_table_names)
        self.combo.setFixedWidth(400)
        self.addwid.addWidget(self.combo)

        self.button2 = QPushButton('Выбрать таблицу', self)
        self.button2.setFixedWidth(400)
        self.button2.clicked.connect(self.btn2_activated_scatter)
        self.addwid.addWidget(self.button2)        

        self.button1 = QPushButton('Вернуться назад', self)
        self.button1.setFixedWidth(400)
        self.button1.clicked.connect(self.create_body)
        self.addwid.addWidget(self.button1)

    def btn2_activated_scatter(self):
        try:
            actions = str("Выбрана таблица для Линейного графика")
            write_logs.write_row(actions)
            self.table_name = self.combo.currentText()
        except:
            actions = str("Редактирование Линейного графика")
            write_logs.write_row(actions)
            self.table_name = self.table_name2

        #Удаление всех виджетов 
        for i in range(self.addwid.count())[1:]:
            self.addwid.itemAt(i).widget().deleteLater()

        self.lbl2 = QLabel(f"Выбрана таблица - {self.table_name}")
        self.lbl2.setFont(QFont('Serif', 14))
        self.addwid.addWidget(self.lbl2)

        self.lbl3 = QLabel("Выберите поле для группировки")
        self.lbl3.setFont(QFont('Serif', 14))
        self.addwid.addWidget(self.lbl3)
        self.select_unique_columns = control_db.select_unique_columns(\
            self.table_name)
        self.select_unique_columns_float = \
        control_db.select_unique_columns_float(self.table_name)

        self.combo1 = QComboBox(self)
        self.combo1.addItems(self.select_unique_columns)
        self.combo1.setFixedWidth(400)
        self.addwid.addWidget(self.combo1)

        self.lbl5 = QLabel("Выберите поле для метрики")
        self.lbl5.setFont(QFont('Serif', 14))
        self.addwid.addWidget(self.lbl5)
        self.combo3 = QComboBox(self)
        self.combo3.addItems(self.select_unique_columns_float)
        self.combo3.setFixedWidth(400)
        self.addwid.addWidget(self.combo3)        

        self.lbl4 = QLabel("Выберите агрегатную функцию")
        self.lbl4.setFont(QFont('Serif', 14))
        self.addwid.addWidget(self.lbl4)
        self.list_aggr_func = ['nunique','count','sum','mean','median','min','max','std']
        self.combo2 = QComboBox(self)
        self.combo2.addItems(self.list_aggr_func)
        self.combo2.setFixedWidth(400)
        self.addwid.addWidget(self.combo2)

        self.button2 = QPushButton('Построить граф', self)
        self.button2.setFixedWidth(400)
        self.button2.clicked.connect(self.btn_build_scatter)
        self.addwid.addWidget(self.button2)        

        self.button1 = QPushButton('Вернуться  к выбору таблицы', self)
        self.button1.setFixedWidth(400)
        self.button1.clicked.connect(self.btn_scatter)
        self.addwid.addWidget(self.button1)

        self.button2 = QPushButton('Вернуться в главное меню дашбордов', self)
        self.button2.setFixedWidth(400)
        self.button2.clicked.connect(self.create_body)
        self.addwid.addWidget(self.button2)

    def btn_build_scatter(self):

        actions = str("Построили Линейный график")
        write_logs.write_row(actions)
        
        agg_value = self.combo1.currentText()
        choise_func = self.combo2.currentText()
        choise_metrics = self.combo3.currentText()
        
        table_name = self.table_name

        #Удаление всех виджетов 
        for i in range(self.addwid.count()):
            self.addwid.itemAt(i).widget().deleteLater()

        self.table_name2 = table_name

        df = control_db.select_db(table_name)[0]

        self.lbl = QLabel("Столбчатая диаграмма")
        self.lbl.setFont(QFont('Serif', 16))
        self.addwid.addWidget(self.lbl)

        grouped = df.groupby(agg_value, as_index=False).\
        agg({choise_metrics:choise_func})
        grouped = grouped.sort_values(agg_value, ascending=False)
        
        try:
            fig = px.scatter(x=grouped[agg_value],\
             y=grouped[choise_metrics], title='Линейный график')
        except:
            x = np.arange(0,5,0.1)
            def f(x):
                return x**2
            fig = px.scatter(x=x, y=f(x), title='Test Scatter chart')
        
        self.browser = QtWebEngineWidgets.QWebEngineView(self)
        self.browser.setFixedSize(650,450)
        fig.update_traces()#quartilemethod="inclusive")
        self.browser.setHtml(fig.to_html(include_plotlyjs='cdn'))
        self.browser.show()
        self.addwid.addWidget(self.browser)

        self.button1 = QPushButton('Изменить параметры диаграммы', self)
        self.button1.setFixedWidth(400)
        self.button1.clicked.connect(self.btn2_activated_scatter)
        self.addwid.addWidget(self.button1)

        self.button2 = QPushButton('Построить новую столбчатую диаграмму', self)
        self.button2.setFixedWidth(400)
        self.button2.clicked.connect(self.btn_scatter)
        self.addwid.addWidget(self.button2)

        self.button4 = QPushButton('Вернуться в главное меню дашбордов', self)
        self.button4.setFixedWidth(400)
        self.button4.clicked.connect(self.create_body)
        self.addwid.addWidget(self.button4)

    def btn_box(self):
        actions = str("Нажата кнопка Свечи")
        write_logs.write_row(actions)

        #Удаление всех виджетов 
        for i in range(self.addwid.count()):
            self.addwid.itemAt(i).widget().deleteLater()

        self.lbl = QLabel("Построение диаграммы свечи")
        self.lbl.setFont(QFont('Serif', 16))
        self.addwid.addWidget(self.lbl)

        self.lbl2 = QLabel("Выберите таблицу")
        self.lbl2.setFont(QFont('Serif', 14))
        self.addwid.addWidget(self.lbl2)
        self.combo = QComboBox(self)
        self.list_table_names = []
        tupple_names = control_db.db_names()
        for i in tupple_names:
            self.list_table_names.append(str(i)[2:-3])
        self.list_table_names.remove("logs")
        self.list_table_names.remove("info_for_tables")
        self.list_table_names.remove("info_for_tables_view")
        self.combo.addItems(self.list_table_names)
        self.combo.setFixedWidth(400)
        self.addwid.addWidget(self.combo)

        self.button2 = QPushButton('Выбрать таблицу', self)
        self.button2.setFixedWidth(400)
        self.button2.clicked.connect(self.btn2_activated_box)
        self.addwid.addWidget(self.button2)        

        self.button1 = QPushButton('Вернуться назад', self)
        self.button1.setFixedWidth(400)
        self.button1.clicked.connect(self.create_body)
        self.addwid.addWidget(self.button1)

    def btn2_activated_box(self):
        try:
            actions = str("Выбрана таблциа для Свечей")
            write_logs.write_row(actions)
            self.table_name = self.combo.currentText()
        except:
            actions = str("Редактирование свечей")
            write_logs.write_row(actions)
            self.table_name = self.table_name2

        #Удаление всех виджетов 
        for i in range(self.addwid.count())[1:]:
            self.addwid.itemAt(i).widget().deleteLater()

        self.lbl2 = QLabel(f"Выбрана таблица - {self.table_name}")
        self.lbl2.setFont(QFont('Serif', 14))
        self.addwid.addWidget(self.lbl2)

        self.lbl3 = QLabel("Выберите поле для группировки")
        self.lbl3.setFont(QFont('Serif', 14))
        self.addwid.addWidget(self.lbl3)
        self.select_unique_columns = control_db.select_unique_columns(\
            self.table_name)
        self.select_unique_columns_float = \
        control_db.select_unique_columns_float(self.table_name)

        self.combo1 = QComboBox(self)
        self.combo1.addItems(self.select_unique_columns)
        self.combo1.setFixedWidth(400)
        self.addwid.addWidget(self.combo1)

        self.lbl5 = QLabel("Выберите поле для метрики")
        self.lbl5.setFont(QFont('Serif', 14))
        self.addwid.addWidget(self.lbl5)
        self.combo3 = QComboBox(self)
        self.combo3.addItems(self.select_unique_columns_float)
        self.combo3.setFixedWidth(400)
        self.addwid.addWidget(self.combo3)        

        self.lbl4 = QLabel("Выберите агрегатную функцию")
        self.lbl4.setFont(QFont('Serif', 14))
        self.addwid.addWidget(self.lbl4)
        self.list_aggr_func = ['nunique','count','sum','mean','median','min','max','std']
        self.combo2 = QComboBox(self)
        self.combo2.addItems(self.list_aggr_func)
        self.combo2.setFixedWidth(400)
        self.addwid.addWidget(self.combo2)

        self.button2 = QPushButton('Построить граф', self)
        self.button2.setFixedWidth(400)
        self.button2.clicked.connect(self.btn_build_box)
        self.addwid.addWidget(self.button2)        

        self.button1 = QPushButton('Вернуться  к выбору таблицы', self)
        self.button1.setFixedWidth(400)
        self.button1.clicked.connect(self.btn_box)
        self.addwid.addWidget(self.button1)

        self.button2 = QPushButton('Вернуться в главное меню дашбордов', self)
        self.button2.setFixedWidth(400)
        self.button2.clicked.connect(self.create_body)
        self.addwid.addWidget(self.button2)

    def btn_build_box(self):

        actions = str("Построили Свечи")
        write_logs.write_row(actions)
        
        agg_value = self.combo1.currentText()
        choise_func = self.combo2.currentText()
        choise_metrics = self.combo3.currentText()
        
        table_name = self.table_name

        #Удаление всех виджетов 
        for i in range(self.addwid.count()):
            self.addwid.itemAt(i).widget().deleteLater()

        self.table_name2 = table_name

        df = control_db.select_db(table_name)[0]

        self.lbl = QLabel("Диаграмма Свеча")
        self.lbl.setFont(QFont('Serif', 16))
        self.addwid.addWidget(self.lbl)

        grouped = df.groupby(agg_value, as_index=False).\
        agg({choise_metrics:choise_func})
        grouped = grouped.sort_values(agg_value, ascending=False)
        
        try:
            fig = px.box(grouped, y="agg_value", \
                color={choise_metrics:choise_func}, \
                title='Test Box chart')
        except:
            df = px.data.tips()
            fig = px.box(df, y="total_bill", color="smoker", \
                title='Test Box chart')
        
        self.browser = QtWebEngineWidgets.QWebEngineView(self)
        self.browser.setFixedSize(650,450)
        fig.update_traces()#quartilemethod="inclusive")
        self.browser.setHtml(fig.to_html(include_plotlyjs='cdn'))
        self.browser.show()
        self.addwid.addWidget(self.browser)

        self.button1 = QPushButton('Изменить параметры диаграммы', self)
        self.button1.setFixedWidth(400)
        self.button1.clicked.connect(self.btn2_activated_box)
        self.addwid.addWidget(self.button1)

        self.button2 = QPushButton('Построить новые Свечи', self)
        self.button2.setFixedWidth(400)
        self.button2.clicked.connect(self.btn_box)
        self.addwid.addWidget(self.button2)

        self.button4 = QPushButton('Вернуться в главное меню дашбордов', self)
        self.button4.setFixedWidth(400)
        self.button4.clicked.connect(self.create_body)
        self.addwid.addWidget(self.button4)

    def pie_graph(self):

        actions = str("Выбрана Круговая диаграмма для примера")
        write_logs.write_row(actions)

        #Круговая диаграмма     
        df = px.data.gapminder().query("year == 2007").\
        query("continent == 'Europe'")
        srez = df.sort_values('pop', ascending=False).head(10).copy().\
        reset_index(drop=True)
        abs_sum_pop = round(df['pop'].sum()/10**6,2)
        choise_sum_pop = round(srez['pop'].sum()/10**6,2)
        text = str(f"    Всего : {abs_sum_pop} млн.<br>\
            Выбрано: {choise_sum_pop} млн.")
        del df
        
        fig = go.Figure()
        fig.add_trace(go.Pie(values=srez['pop'], labels=srez['country'],\
            hole=0.9))
        fig.update_layout(
            title = "Пример круговой диаграммы",
            annotations=[dict(text=text,x=0.5, y=0.5, showarrow=False)])

        return fig

    def bar_graph(self):

        actions = str("Выбрана Столбчатая диаграмма для примера")
        write_logs.write_row(actions)

        #Столбчатая диаграмма
        fig = px.bar(x=["a","b","c","d"], y=[1,2.3,3,3.5],\
            title='Test bar chart')
        return fig

    def table_graph(self):

        actions = str("Выбрана Таблица для примера")
        write_logs.write_row(actions)

        #Сводная таблица
        print(10)

    def scatter_graph(self):

        actions = str("Выбран Линейный график для примера")
        write_logs.write_row(actions)

        #Линейный график
        x = np.arange(0,5,0.1)
        def f(x):
            return x**2
        fig = px.scatter(x=x, y=f(x), title='Test Scatter chart')
        return fig

    def hist_graph(self):

        actions = str("Выбрана Гистограмма для примера")
        write_logs.write_row(actions)

        #Гистограмма
        dices = pd.DataFrame(np.random.randint(low=1, high=7, size=(100,2)),\
            columns=('1','2'))
        dices['сумма'] = dices['1'] + dices['2']
        fig = go.Figure(data=[go.Histogram(x=dices['сумма'])])
        fig.update_layout(
            title = "Пример гистограммы")
        return fig

    def box_graph(self):

        actions = str("Выбрана диаграмма Свеча для примера")
        write_logs.write_row(actions)

        #Свечи
        df = px.data.tips()
        fig = px.box(df, y="total_bill", color="smoker", \
            title='Test Box chart')
        return fig

    def show_graph(self):

        choise = self.combo.currentText()

        actions = str(f"На стартовой странице дашбордов выбрали - {choise}")
        write_logs.write_row(actions)

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
        self.browser.show()

    def create_body(self):
        form_frame = QFrame()
        form_frame.setFrameShape(QFrame.StyledPanel)
        form_frame.setMinimumWidth(300)
        form_frame.setMaximumWidth(300)
        
        p_push = QPushButton('Столбчатая диаграмма')
        p_push.setContentsMargins(10, 20, 10, 10)
        p_push1 = QPushButton('Круговая диаграмма')
        p_push1.setContentsMargins(10, 40, 10, 30)
        p_push2 = QPushButton('Гистограмма')
        p_push2.setContentsMargins(10, 60, 10, 50)
        p_push3 = QPushButton('Таблица')
        p_push3.setContentsMargins(10, 80, 10, 70)
        p_push4 = QPushButton('Линейный график')
        p_push4.setContentsMargins(10, 100, 10, 90)
        p_push5 = QPushButton('Диаграмма Свеча')
        p_push5.setContentsMargins(10, 120, 10, 110)

        form_lay = QFormLayout()
        form_lay.addRow(p_push)
        form_lay.addRow(p_push1)
        form_lay.addRow(p_push2)
        form_lay.addRow(p_push3)
        form_lay.addRow(p_push4)
        form_lay.addRow(p_push5)
        form_frame.setLayout(form_lay)

        ver_frame = QFrame()
        ver_frame.setFrameShape(QFrame.StyledPanel)


        self.addwid = QVBoxLayout()
        self.addwid.setContentsMargins(25, 20, 25, 25)        
        
        self.lbl = QLabel("Построить дашборд")
        self.lbl.setFont(QFont('Serif', 16))
        self.addwid.addWidget(self.lbl)

        self.lbl1 = QLabel("Пример построения различных виджетов")
        self.lbl1.setFont(QFont('Serif', 14))
        self.addwid.addWidget(self.lbl1)

        self.lbl2 = QLabel("Выберите виджет")
        self.lbl2.setFont(QFont('Serif', 14))
        self.addwid.addWidget(self.lbl2)

        self.combo = QComboBox(self)
        self.list_graph = ['Круговая диаграмма', 'Столбчатая диаграмма','Линейный график', 'Гистограмма', 'Свечи']
        self.combo.addItems(self.list_graph)
        self.combo.setFixedWidth(400)

        self.button = QPushButton('Построить график', self)
        self.button.setFixedWidth(400)

        self.browser = QtWebEngineWidgets.QWebEngineView(self)
        self.browser.setFixedSize(650,450)

        self.addwid.addWidget(self.combo)  
        self.addwid.addWidget(self.button)
        
        fig = self.pie_graph()
        fig.update_traces()#quartilemethod="inclusive")
        self.browser.setHtml(fig.to_html(include_plotlyjs='cdn'))
        self.browser.show()

        self.addwid.addWidget(self.browser)

        self.button.clicked.connect(self.show_graph)

        ver_frame.setLayout(self.addwid)

        #Создание разделителя
        splitter = QSplitter(Qt.Horizontal)
        splitter.addWidget(form_frame)
        splitter.addWidget(ver_frame)

        self.vbox = QVBoxLayout()
        self.vbox.addWidget(splitter)
        self.setCentralWidget(splitter)

        p_push.clicked.connect(self.btn_bar_)
        p_push1.clicked.connect(self.btn_pie_chart)
        p_push2.clicked.connect(self.btn_hist)
        p_push3.clicked.connect(self.btn_table)
        p_push4.clicked.connect(self.btn_scatter)
        p_push5.clicked.connect(self.btn_box)

class Button(QtWidgets.QPushButton):
    pass

class menu_toolbar_window(QMainWindow):

    def __init__(self):
        super().__init__()

        self.create_menu_bar()

    def create_menu_bar(self):
        self.menu_bar = self.menuBar()

        self.file_menu = self.menu_bar.addMenu("Файл")
        self.file_menu.addAction('Новый')
        self.file_menu.addAction('Открыть')
        self.file_menu.addAction('Сохранить')
        self.file_menu.addAction('Сохранить как')

        self.exit_menu = QAction('&Выйти', self)
        self.exit_menu.setShortcut('Ctrl+Q')
        self.exit_menu.triggered.connect(self.close)
        self.file_menu.addAction(self.exit_menu)         

        self.view_menu = self.menu_bar.addMenu("Вид")
        self.view_menu.addAction('set Full Screen')
        self.view_menu.addAction('show Status Bar') 

        self.edit_menu = self.menu_bar.addMenu("Изменение")
        self.edit_menu.addAction('Вырезать')
        self.edit_menu.addAction('Копировать')
        self.edit_menu.addAction('Вставить')
        self.edit_menu.addAction('Поиск')
        self.edit_menu.addAction('Замена') 

        self.help_menu = self.menu_bar.addMenu("Помощь")
        self.help_menu.addAction('Помощь')
        self.help_menu.addAction('Об')

    def contextMenuEvent(self, event):
        men = QMenu()
        men.addAction('New')
        men.addAction('Open')
        quit = men.addAction('Quit')
        action = men.exec_(self.mapToGlobal(event.pos()))
        if action is quit:
           self.close()

class MainWindow(QtWidgets.QWidget):

    def __init__(self):
        super().__init__()
        self.myclose = False
        self.write_logs

        actions = "Запустили программу"
        write_logs.write_row(actions)

        page1 = main_window()
        page2 = capture_trafic_window()
        page3 = control_db_window()
        page4 = analyse_trafic_window()
        page5 = develop_widgets_window()
        
        options = ["Главная страница","Захват трафика", "Управление БД", 
            "Анализ трафика", "Построение графиков"]
        stackedwidget = QtWidgets.QStackedWidget()

        hlay = QtWidgets.QHBoxLayout()
        group = QtWidgets.QButtonGroup(self)
        group.buttonClicked[int].connect(self.write_logs)
        group.buttonClicked[int].connect(stackedwidget.setCurrentIndex)

        for i, (option, widget) in enumerate(
                zip(
                    options, 
                    (page1, page2, page3, page4, page5)
                )
            ):
            button = Button(text=option, checkable=True)
            ix = stackedwidget.addWidget(widget)
            group.addButton(button, ix)
            hlay.addWidget(button)
            if i == 0:
                button.setChecked(True)
                actions = str(f"Открылась вкладка {option}")
                write_logs.write_row(actions)
        
        vbox = QtWidgets.QVBoxLayout(self)
        vbox.addWidget(stackedwidget)
        vbox.addLayout(hlay)

    def write_logs(self, option):
        if option == 0:
            text = "Главная страница"
            actions = str(f"Открылась вкладка {text}")
            write_logs.write_row(actions)
        elif option == 1:
            text = "Захват трафика"
            actions = str(f"Открылась вкладка {text}")
            write_logs.write_row(actions)
        elif option == 2:
            text = "Управление БД"
            actions = str(f"Открылась вкладка {text}")
            write_logs.write_row(actions)
        elif option == 3:
            text = "Анализ трафика"
            actions = str(f"Открылась вкладка {text}")
            write_logs.write_row(actions)
        elif option == 4:
            text = "Построение графиков"
            actions = str(f"Открылась вкладка {text}")
            write_logs.write_row(actions)

    def closeEvent(self, event):
        actions = "Закрыли программу"
        write_logs.write_row(actions)
          
if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    app.setStyle("fusion")
    app.setStyleSheet(style.QSS)
    win = MainWindow()
    win.setWindowTitle('Программа для анализа трафика')
    win.setWindowIcon(QIcon("icon.png")) 
    win.resize(1000, 800)

    win.show()
    sys.exit(app.exec_())