import datetime
import os
import sqlite3
import sys
from json import loads, dumps

from PIL import Image
from PyQt5 import uic
from PyQt5.QtCore import QSize, QDate
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QMainWindow, QApplication, QPushButton, QListWidgetItem, QFileDialog

connect = sqlite3.connect('db/ship_tool.db')
cursor = connect.cursor()


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi('templates/main.ui', self)
        self.initUI()

    def initUI(self):
        # self.pushButton_2.clicked.connect(self.open_report)
        self.pushButton.clicked.connect(self.open_peiring)
        self.pushButton_3.clicked.connect(self.open_human)
        # self.pushButton_6.clicked.connect(self.open_stories)

    def open_peiring(self):
        self.peirings = PeiringsWindow()
        self.peirings.show()

    def open_human(self):
        self.humans = HumansWindow()
        self.humans.show()


class HumansWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi('templates/humans.ui', self)
        self.initUI()

    def initUI(self):
        self.tabWidget.setVisible(False)
        self.pushButton_4.setVisible(False)
        self.pushButton_5.setVisible(False)
        self.pushButton.clicked.connect(self.add_human)
        self.select_button = None
        self.dict_but = {}
        self.dict_peirings_but = {}
        self.new_human_mode = False
        self.photo = None
        self.pushButton_5.clicked.connect(self.delete_photo)
        self.lineEdit_2.textChanged.connect(self.check_window)
        self.textEdit.textChanged.connect(self.check_window)
        self.textEdit_2.textChanged.connect(self.check_window)
        self.lineEdit.textChanged.connect(self.find_human)
        self.dateEdit.dateChanged.connect(self.check_window)
        self.pushButton_3.clicked.connect(self.delete)
        self.pushButton_4.clicked.connect(self.save_data)
        self.pushButton_2.clicked.connect(self.new_icon)
        self.load_window()

    def find_human(self):
        global cursor
        humans = cursor.execute(f'SELECT * from humans').fetchall()
        if humans:
            self.listWidget.clear()
            list_buttons = list(map(lambda x: self.make_buttons(x, find_mode=True), humans))
            for i in list_buttons:
                if i:
                    list_widget_item = QListWidgetItem()
                    list_widget_item.setSizeHint(QSize(25, 50))
                    if self.dict_but[i][4]:
                        list_widget_item.setIcon(QIcon(self.dict_but[i][4]))
                    self.listWidget.addItem(list_widget_item)
                    self.listWidget.setItemWidget(list_widget_item, i)

    def delete_photo(self):
        global cursor
        global connect
        os.remove(self.dict_but[self.select_button][4])
        cursor.execute(f'UPDATE humans SET photo = ? WHERE id = {self.dict_but[self.select_button][0]}', (None,))
        connect.commit()
        self.pushButton_2.setIcon(QIcon('app_image/no_photo.png'))
        self.load_window()
        self.pushButton_5.setVisible(False)
        self.label_4.setVisible(True)

    def save_data(self):
        global cursor
        global connect
        if len(self.lineEdit_2.text().split()) == 2:
            name, surname = self.lineEdit_2.text().split()
            patronymic = None
        elif len(self.lineEdit_2.text().split()) == 3:
            name, surname, patronymic = self.lineEdit_2.text().split()
        elif len(self.lineEdit_2.text().split()) == 1:
            name, surname, patronymic = self.lineEdit_2.text().strip(), None, None
        else:
            name, surname, patronymic = None, None, None
        cursor.execute(f'UPDATE humans SET name = ?, surname = ?, patronymic = ?, photo = ?,'
                       f' dating_history = ?, general_info = ?, date_of_birth = ?, edit_date = ?'
                       f' WHERE id = {str(self.dict_but[self.select_button][0])}', (
                           name if name else None, surname if surname else None,
                           patronymic if patronymic else None,
                           self.photo if self.photo else None, self.textEdit_2.toPlainText(),
                           self.textEdit.toPlainText(), str(self.dateEdit.date().toString('yyyy-M-d')),
                           str(datetime.date.today())))
        connect.commit()
        self.pushButton.setVisible(True)
        self.pushButton_4.setVisible(False)
        self.load_window()

    def new_icon(self):
        try:
            fname = QFileDialog.getOpenFileName(self, 'Выбрать картинку', '/home', "Изображение (*.png *.xpm *.jpg)")[0]
            im = Image.open(fname)
            im.save(f'data/humans/{str(self.dict_but[self.select_button][0])}.png')
            self.photo = f'data/humans/{str(self.dict_but[self.select_button][0])}.png'
            self.pushButton_2.setIcon(QIcon(f'data/humans/{str(self.dict_but[self.select_button][0])}.png'))
            cursor.execute(f'UPDATE humans SET photo'
                           f' = \'{f"data/humans/{str(self.dict_but[self.select_button][0])}.png"}\''
                           f' WHERE id = {str(self.dict_but[self.select_button][0])}')
            connect.commit()
            self.load_window()
        except AttributeError:
            pass

    def delete(self):
        global cursor
        global connect
        self.new_human_mode = True
        self.pushButton_2.setIcon(QIcon('app_image/no_photo.png'))
        self.tabWidget.setVisible(False)
        self.lineEdit_2.setText('')
        self.textEdit_2.setText('')
        self.textEdit.setText('')
        self.listWidget_3.clear()
        self.dateEdit.setDate(datetime.date.today())
        self.label_7.setText('')
        file = cursor.execute(f'SELECT photo from humans'
                              f' WHERE id = {str(self.dict_but[self.select_button][0])}').fetchall()[0][0]
        if file:
            os.remove(file)
        cursor.execute(f'DELETE from humans WHERE id = {str(self.dict_but[self.select_button][0])}')
        connect.commit()
        self.new_human_mode = False
        self.pushButton.setVisible(True)
        self.pushButton_4.setVisible(False)
        self.load_window()

    def add_human(self):
        self.new_human_mode = True
        global cursor
        global connect
        self.pushButton_2.setIcon(QIcon('app_image/no_photo.png'))
        self.lineEdit_2.setText('Новый человек')
        self.textEdit_2.setText('')
        self.textEdit.setText('')
        self.listWidget_3.clear()
        self.dateEdit.setDate(datetime.date.today())
        self.label_7.setText('')
        cursor.execute(f'INSERT INTO humans(name, surname, patronymic, photo, dating_history,'
                       f' general_info, date_of_birth, create_date, edit_date)'
                       f' VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?)',
                       ('Новый', 'человек', None, None, None, None, None, str(datetime.date.today()),
                        str(datetime.date.today())))
        self.new_id = max(list(map(lambda x: x[0], cursor.execute('SELECT id from humans').fetchall())))
        self.pushButton.setVisible(False)
        self.pushButton_4.setVisible(True)
        list_widget_item = QListWidgetItem()
        list_widget_item.setSizeHint(QSize(25, 50))
        self.listWidget.addItem(list_widget_item)
        button = QPushButton('Новый человек')
        self.dict_but[button] = [self.new_id, 'Новый', 'человек', None, None, None, None, None]
        self.listWidget.setItemWidget(list_widget_item, button)
        self.open_human()
        self.new_human_mode = False
        button.clicked.connect(self.open_human)
        self.select_button = button

    def check_window(self):
        if not self.new_human_mode:
            if len(self.lineEdit_2.text().split()) == 2:
                name, surname = self.lineEdit_2.text().split()
                patronymic = None
            elif len(self.lineEdit_2.text().split()) == 3:
                name, surname, patronymic = self.lineEdit_2.text().split()
            elif len(self.lineEdit_2.text().split()) == 1:
                name, surname, patronymic = self.lineEdit_2.text().strip(), None, None
            else:
                name, surname, patronymic = None, None, None
            if name != self.dict_but[self.select_button][1] or surname != self.dict_but[self.select_button][2] \
                    or patronymic != self.dict_but[self.select_button][3] \
                    or self.photo != self.dict_but[self.select_button][4] \
                    or self.textEdit_2.toPlainText() != self.dict_but[self.select_button][5] \
                    or self.textEdit.toPlainText() != self.dict_but[self.select_button][6] \
                    or str(self.dateEdit.date().toString('yyyy-M-d')) != self.dict_but[self.select_button][7]:
                self.pushButton.setVisible(False)
                self.pushButton_4.setVisible(True)
            else:
                self.pushButton.setVisible(True)
                self.pushButton_4.setVisible(False)

    def load_window(self):
        global cursor
        humans = cursor.execute(f'SELECT * from humans').fetchall()
        if humans:
            self.listWidget.clear()
            list_buttons = list(map(lambda x: self.make_buttons(x), humans))
            for i in list_buttons:
                list_widget_item = QListWidgetItem()
                list_widget_item.setSizeHint(QSize(25, 50))
                if self.dict_but[i][4]:
                    list_widget_item.setIcon(QIcon(self.dict_but[i][4]))
                self.listWidget.addItem(list_widget_item)
                self.listWidget.setItemWidget(list_widget_item, i)

    def make_buttons(self, list_info, find_mode=False):
        if not find_mode:
            button = QPushButton(f'{list_info[1]} {list_info[2]}')
            self.dict_but[button] = list_info
            button.clicked.connect(self.open_human)
            return button
        else:
            find_text = self.lineEdit.text().lower().strip()
            if find_text in ''.join(list(map(lambda x: x.lower().strip() if type(x) == str else '', list_info))):
                button = QPushButton(f'{list_info[1]} {list_info[2]}')
                self.dict_but[button] = list_info
                button.clicked.connect(self.open_human)
                return button

    def check_selection_data(self, list_info, not_checked_peirings):
        if list_info[0] in loads(not_checked_peirings[2]):
            return not_checked_peirings

    def make_peirings_buttons(self, list_info):
        button = QPushButton(f'{list_info[1]}')
        self.dict_peirings_but[button] = list_info
        button.clicked.connect(self.open_peirings)
        list_widget_item = QListWidgetItem()
        list_widget_item.setSizeHint(QSize(25, 50))
        if list_info[3]:
            list_widget_item.setIcon(QIcon(list_info[3]))
        self.listWidget_3.addItem(list_widget_item)
        self.listWidget_3.setItemWidget(list_widget_item, button)

    def open_peirings(self):
        peiring_list = self.dict_peirings_but[self.sender()]
        self.peiring_window = PeiringsWindow()
        self.peiring_window.new_peiring_mode = True
        self.peiring_window.open_peiring(manage_mode=peiring_list)
        self.peiring_window.new_peiring_mode = False
        self.peiring_window.show()

    def open_human(self, manage_mode=False):
        if self.select_button != self.sender():
            self.pushButton_5.setVisible(False)
            self.label_4.setVisible(True)
            self.photo = None
            self.listWidget_3.clear()
            if manage_mode:
                list_info = manage_mode
            else:
                if self.new_human_mode:
                    list_info = [self.new_id, 'Новый', 'человек', None, None, None, None, None]
                    self.select_button = self.sender()
                else:
                    self.pushButton.setVisible(True)
                    self.pushButton_4.setVisible(False)
                    self.select_button = self.sender()
                    list_info = self.dict_but[self.select_button]
            if list_info[4]:
                self.pushButton_2.setIcon(QIcon(list_info[4]))
                self.photo = list_info[4]
                self.pushButton_5.setVisible(True)
                self.label_4.setVisible(False)
            else:
                self.pushButton_5.setVisible(False)
                self.label_4.setVisible(True)
                self.pushButton_2.setIcon(QIcon('app_image/no_photo.png'))
            peirings = cursor.execute(f'SELECT * from peirings').fetchall()
            if peirings:
                list_peirings = list(filter(None, map(lambda x: self.check_selection_data(list_info, x), peirings)))
                if list_peirings:
                    list(map(lambda x: self.make_peirings_buttons(x), list_peirings))
            self.tabWidget.setVisible(True)
            self.lineEdit_2.setText(f'{list_info[1] if list_info[1] else ""}'
                                    f' {list_info[2] if list_info[2] else ""}'
                                    f' {list_info[3] if list_info[3] else ""}')
            self.textEdit_2.setText(f'{list_info[5] if list_info[5] else ""}')
            self.textEdit.setText(f'{list_info[6] if list_info[6] else ""}')
            if list_info[7]:
                self.dateEdit.setDate(QDate(*map(int, list_info[7].split('-'))))
            else:
                self.dateEdit.setDate(QDate(datetime.date.today()))
            self.label_7.setText(str(list_info[0]))
        else:
            self.tabWidget.setVisible(False)
            self.new_human_mode = True
            self.lineEdit_2.setText('')
            self.textEdit_2.setText('')
            self.textEdit.setText('')
            self.listWidget_3.clear()
            self.dateEdit.setDate(datetime.date.today())
            self.label_7.setText('')
            self.new_human_mode = False
            if self.lineEdit.text() and self.lineEdit.text() != 'Поиск':
                self.find_human()
            else:
                self.load_window()


class PeiringsWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi('templates/peirings.ui', self)
        self.initUI()

    def initUI(self):
        self.tabWidget.setVisible(False)
        self.pushButton_8.setVisible(False)
        self.pushButton_7.setVisible(False)
        self.select_button = None
        self.dict_but = {}
        self.mini_dict_but = {}
        self.new_peiring_mode = False
        self.photo = None
        self.status = None
        self.humans = []
        self.lineEdit.textChanged.connect(self.find_data)
        self.lineEdit_2.textChanged.connect(self.check_window)
        self.textEdit.textChanged.connect(self.check_window)
        self.comboBox.currentIndexChanged.connect(self.check_status)
        self.checkBox.stateChanged.connect(self.check_status)
        self.lineEdit_3.textChanged.connect(self.check_status)
        self.dateEdit.dateChanged.connect(self.check_window)
        self.dateEdit_2.dateChanged.connect(self.check_window)
        self.pushButton_8.clicked.connect(self.save_data)
        self.pushButton_5.clicked.connect(self.window_add_remove_human)
        self.pushButton_4.clicked.connect(self.window_add_remove_human)
        self.pushButton.clicked.connect(self.add_peiring)
        self.pushButton_2.clicked.connect(self.new_icon)
        self.pushButton_7.clicked.connect(self.delete_photo)
        self.pushButton_3.clicked.connect(self.delete)
        self.status_dict = {'Вместе': 0, 'Не вместе': 1, 'Расстались': 2, 'В соре': 3, 'Нет информации': 4,
                            'Больше не пейринг': 5, 0: 'Вместе', 1: 'Не вместе', 2: 'Расстались', 3: 'В соре',
                            4: 'Нет информации', 5: 'Больше не пейринг'}
        self.load_window()

    def delete_photo(self):
        global cursor
        global connect
        os.remove(self.dict_but[self.select_button][3])
        cursor.execute(f'UPDATE peirings SET photo = ? WHERE id = {self.dict_but[self.select_button][0]}', (None,))
        connect.commit()
        self.pushButton_2.setIcon(QIcon('app_image/no_photo.png'))
        self.pushButton_7.setVisible(False)
        self.label_4.setVisible(True)

    def clear_window(self):
        self.pushButton_2.setIcon(QIcon('app_image/no_photo.png'))
        self.lineEdit_2.setText('')
        self.textEdit.setText('')
        self.dateEdit.setDate(datetime.date.today())
        self.dateEdit_2.setDate(datetime.date.today())
        self.listWidget_2.clear()
        self.label_13.setText('')
        self.photo = None
        self.status = None
        self.humans = []
        self.lineEdit_3.setText('')
        self.checkBox.setChecked(False)
        self.comboBox.setCurrentIndex(0)
        self.listWidget_4.clear()
        self.listWidget_6.clear()
        self.pushButton_7.setVisible(False)
        self.label_4.setVisible(True)
        self.pushButton.setVisible(True)
        self.pushButton_8.setVisible(False)
        self.label_7.setText('')

    def delete(self):
        global cursor
        global connect
        self.new_human_mode = True
        self.clear_window()
        file = cursor.execute(f'SELECT photo from peirings'
                              f' WHERE id = {str(self.dict_but[self.select_button][0])}').fetchall()[0][0]
        if file:
            os.remove(file)
        cursor.execute(f'DELETE from peirings WHERE id = {str(self.dict_but[self.select_button][0])}')
        connect.commit()
        self.clear_window()
        self.tabWidget.setVisible(False)
        self.new_peiring_mode = False
        self.load_window()

    def new_icon(self):
        try:
            fname = QFileDialog.getOpenFileName(self, 'Выбрать картинку', '/home', "Изображение (*.png *.xpm *.jpg)")[0]
            im = Image.open(fname)
            im.save(f'data/peirings/{str(self.dict_but[self.select_button][0])}.png')
            self.photo = f'data/peirings/{str(self.dict_but[self.select_button][0])}.png'
            self.pushButton_2.setIcon(QIcon(f'data/peirings/{str(self.dict_but[self.select_button][0])}.png'))
            cursor.execute(f'UPDATE peirings SET photo'
                           f' = \'{f"data/peirings/{str(self.dict_but[self.select_button][0])}.png"}\''
                           f' WHERE id = {str(self.dict_but[self.select_button][0])}')
            connect.commit()
            self.pushButton_7.setVisible(True)
            self.label_4.setVisible(False)
            self.load_window()
        except AttributeError:
            pass

    def add_peiring(self):
        self.new_peiring_mode = True
        global cursor
        global connect
        self.clear_window()
        self.pushButton.setVisible(False)
        self.pushButton_8.setVisible(True)
        self.lineEdit_2.setText('Новый пейринг')
        cursor.execute(f'INSERT INTO peirings(name, humans, photo, status, general_info,'
                       f' start_date, end_date, create_date, edit_date, your_status)'
                       f' VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?)',
                       ('Новый пейринг', '[]', None, None, None, None, None, str(datetime.date.today()),
                        str(datetime.date.today()), False))
        self.new_id = max(list(map(lambda x: x[0], cursor.execute('SELECT id from peirings').fetchall())))
        list_widget_item = QListWidgetItem()
        list_widget_item.setSizeHint(QSize(25, 50))
        self.listWidget.addItem(list_widget_item)
        button = QPushButton('Новый пейринг')
        self.dict_but[button] = [self.new_id, 'Новый пейринг', None, None, 'Вместе', None, None, None, None, None, 0]
        self.listWidget.setItemWidget(list_widget_item, button)
        self.open_peiring()
        self.new_peiring_mode = False
        button.clicked.connect(self.open_peiring)
        self.select_button = button
        self.save_data()

    def open_human(self):
        human_list = self.mini_dict_but[self.sender()]
        self.human_window = HumansWindow()
        self.human_window.new_human_mode = True
        self.human_window.open_human(manage_mode=human_list)
        self.human_window.new_human_mode = False
        self.human_window.show()

    def window_add_remove_human(self):
        if self.sender() == self.pushButton_5:
            self.add_human = ManageHumans(self)
            self.add_human.show()
        elif self.sender() == self.pushButton_4:
            self.remove_human = ManageHumans(self, 'remove')
            self.remove_human.show()

    def find_data(self):
        global cursor
        humans = cursor.execute(f'SELECT * from peirings').fetchall()
        if humans:
            self.listWidget.clear()
            list_buttons = list(map(lambda x: self.make_buttons(x, find_mode=True), humans))
            for i in list_buttons:
                if i:
                    list_widget_item = QListWidgetItem()
                    list_widget_item.setSizeHint(QSize(25, 50))
                    if self.dict_but[i][3]:
                        list_widget_item.setIcon(QIcon(self.dict_but[i][3]))
                    self.listWidget.addItem(list_widget_item)
                    self.listWidget.setItemWidget(list_widget_item, i)

    def save_data(self):
        global cursor
        global connect
        if self.checkBox.isChecked():
            self.lineEdit_3.setVisible(True)
            if self.status != self.lineEdit_3.text():
                self.status = self.lineEdit_3.text()
        else:
            self.lineEdit_3.setVisible(False)
            if self.status != self.comboBox.currentText():
                self.status = self.comboBox.currentText()
        cursor.execute(f'UPDATE peirings SET name = ?, humans = ?, photo = ?, status = ?,'
                       f' general_info = ?, start_date = ?, end_date = ?, edit_date = ?, your_status = ? WHERE'
                       f' id = {str(self.dict_but[self.select_button][0])}',
                       (self.lineEdit_2.text().strip(), dumps(self.humans) if self.humans else '[]',
                        self.photo if self.photo else None,
                        self.status if self.status else None, self.textEdit.toPlainText(),
                        str(self.dateEdit.date().toString('yyyy-M-d')),
                        str(self.dateEdit_2.date().toString('yyyy-M-d')), datetime.date.today(),
                        self.checkBox.isChecked()))
        connect.commit()
        self.open_peiring(manage_mode=cursor.execute(
            f'SELECT * from peirings'
            f' WHERE id = {str(self.dict_but[self.select_button][0])}').fetchall()[0])
        self.pushButton.setVisible(True)
        self.pushButton_8.setVisible(False)

    def check_window(self):
        if not self.new_peiring_mode:
            if self.lineEdit_2.text().strip() != self.dict_but[self.select_button][1] or self.textEdit.toPlainText() != \
                    self.dict_but[self.select_button][5] \
                    or str(self.dateEdit.date().toString('yyyy-M-d')) != self.dict_but[self.select_button][6] \
                    or str(self.dateEdit_2.date().toString('yyyy-M-d')) != self.dict_but[self.select_button][7]:
                self.pushButton.setVisible(False)
                self.pushButton_8.setVisible(True)
            else:
                self.pushButton.setVisible(True)
                self.pushButton_8.setVisible(False)

    def load_window(self):
        global cursor
        humans = cursor.execute(f'SELECT * from peirings').fetchall()
        if humans:
            self.listWidget.clear()
            list(map(lambda x: self.make_buttons(x), humans))

    def make_buttons(self, list_info, find_mode=False):
        if not find_mode:
            button = QPushButton(f'{list_info[1] if list_info[1] else ""}')
            self.dict_but[button] = list_info
            button.clicked.connect(self.open_peiring)
            list_widget_item = QListWidgetItem()
            list_widget_item.setSizeHint(QSize(25, 50))
            if list_info[3]:
                list_widget_item.setIcon(QIcon(list_info[3]))
            self.listWidget.addItem(list_widget_item)
            self.listWidget.setItemWidget(list_widget_item, button)
        else:
            find_text = self.lineEdit.text().lower().strip()
            if find_text in ''.join(list(map(lambda x: x.lower().strip() if type(x) == str else '', list_info))):
                button = QPushButton(f'{list_info[1]}')
                self.dict_but[button] = list_info
                button.clicked.connect(self.open_peiring)
                list_widget_item = QListWidgetItem()
                list_widget_item.setSizeHint(QSize(25, 50))
                if list_info[3]:
                    list_widget_item.setIcon(QIcon(list_info[3]))
                self.listWidget.addItem(list_widget_item)
                self.listWidget.setItemWidget(list_widget_item, button)

    def make_mini_buttons(self, list_info):
        button = QPushButton(f'{list_info[1] if list_info[1] else ""} {list_info[2] if list_info[2] else ""}')
        self.mini_dict_but[button] = list_info
        button.clicked.connect(self.open_human)
        list_widget_item = QListWidgetItem()
        list_widget_item.setSizeHint(QSize(25, 50))
        if list_info[4]:
            list_widget_item.setIcon(QIcon(list_info[4]))
        self.listWidget_2.addItem(list_widget_item)
        self.listWidget_2.setItemWidget(list_widget_item, button)
        return list_info[0]

    def check_status(self):
        if not self.new_peiring_mode:
            if self.checkBox.isChecked():
                self.lineEdit_3.setVisible(True)
                if self.status != self.lineEdit_3.text():
                    self.pushButton.setVisible(False)
                    self.pushButton_8.setVisible(True)
                else:
                    self.pushButton.setVisible(True)
                    self.pushButton_8.setVisible(False)
            else:
                self.lineEdit_3.setVisible(False)
                self.lineEdit_3.setText('')
                if self.status != self.comboBox.currentText():
                    self.pushButton.setVisible(False)
                    self.pushButton_8.setVisible(True)
                else:
                    self.pushButton.setVisible(True)
                    self.pushButton_8.setVisible(False)

    def open_peiring(self, manage_mode=False):
        if self.select_button != self.sender():
            if manage_mode:
                list_info = manage_mode
            else:
                if self.new_peiring_mode:
                    list_info = [self.new_id, 'Новый пейринг', [], None, 'Вместе', None, None, None, None, None, 0]
                    self.select_button = self.sender()
                else:
                    self.pushButton.setVisible(True)
                    self.pushButton_8.setVisible(False)
                    self.select_button = self.sender()
                    list_info = self.dict_but[self.select_button]
            self.clear_window()
            if list_info[3]:
                self.pushButton_2.setIcon(QIcon(list_info[3]))
                self.photo = list_info[3]
                self.pushButton_7.setVisible(True)
                self.label_4.setVisible(False)
            else:
                self.pushButton_7.setVisible(False)
                self.label_4.setVisible(True)
                self.pushButton_2.setIcon(QIcon('app_image/no_photo.png'))
            self.tabWidget.setVisible(True)
            self.lineEdit_2.setText(list_info[1] if list_info[1] else '')
            self.label_13.setText(list_info[4] if list_info[4] else '')
            self.textEdit.setText(list_info[5] if list_info[5] else '')
            self.label_7.setText(str(list_info[0]))
            if not list_info[10]:
                self.checkBox.setChecked(False)
                self.lineEdit_3.setVisible(False)
                self.comboBox.setCurrentIndex(int(self.status_dict[list_info[4]]))
                self.status = list_info[4]
            else:
                self.checkBox.setChecked(True)
                self.lineEdit_3.setVisible(True)
                self.lineEdit_3.setText(list_info[4])
                self.status = list_info[4]
            if list_info[6]:
                self.dateEdit.setDate(QDate(*map(int, list_info[6].split('-'))))
            else:
                self.dateEdit.setDate(datetime.date.today())
            if list_info[7]:
                self.dateEdit_2.setDate(QDate(*map(int, list_info[7].split('-'))))
            else:
                self.dateEdit_2.setDate(datetime.date.today())
            if list_info[2]:
                self.humans = list(map(lambda x: self.make_mini_buttons(x[0]) if x else None,
                                       map(lambda x: cursor.execute(f'SELECT * from humans WHERE id = {x}').fetchall(),
                                           loads(list_info[2]))))
        else:
            self.tabWidget.setVisible(False)
            self.new_peiring_mode = True
            self.clear_window()
            self.new_peiring_mode = False
            if self.lineEdit.text() and self.lineEdit.text() != 'Поиск':
                self.find_data()
            else:
                self.load_window()


class ManageHumans(QMainWindow):
    def __init__(self, parent, type_manage='add'):
        super().__init__()
        self.parent = parent
        self.type_manage = type_manage
        uic.loadUi('templates/manage_human.ui', self)
        self.lineEdit.textChanged.connect(self.find_data)
        self.dict_but = {}
        self.load_window()

    def find_data(self):
        self.listWidget.clear()
        if self.type_manage == 'add':
            list(
                map(lambda x: self.make_buttons(x, find_mode=True), cursor.execute(f'SELECT * from humans').fetchall()))
        else:
            list(map(lambda x: self.make_buttons(x, find_mode=True),
                     map(lambda x: cursor.execute(f'SELECT * from humans WHERE id = {str(x)}').fetchall()[0],
                         self.parent.humans)))

    def manege_human(self):
        if self.type_manage == 'add':
            self.parent.humans.append(self.dict_but[self.sender()][0])
            self.parent.save_data()
            self.parent.open_peiring(manage_mode=cursor.execute(
                f'SELECT * from peirings'
                f' WHERE id = {str(self.parent.dict_but[self.parent.select_button][0])}').fetchall()[0])
            self.load_window()
        elif self.type_manage == 'remove':
            self.parent.humans.pop(self.parent.humans.index(self.dict_but[self.sender()][0]))
            self.parent.save_data()
            self.parent.open_peiring(manage_mode=cursor.execute(
                f'SELECT * from peirings'
                f' WHERE id = {str(self.parent.dict_but[self.parent.select_button][0])}').fetchall()[0])
            self.load_window()

    def make_buttons(self, list_info, find_mode=False):
        if self.type_manage == 'add' and list_info[0] not in self.parent.humans and (
                not find_mode or self.lineEdit.text().lower().strip()
                in ''.join(list(map(lambda x: x.lower().strip() if type(x) == str else '', list_info)))):
            button = QPushButton(f'{list_info[1] if list_info[1] else ""} {list_info[2] if list_info[2] else ""}')
            self.dict_but[button] = list_info
            button.clicked.connect(self.manege_human)
            list_widget_item = QListWidgetItem()
            list_widget_item.setSizeHint(QSize(25, 50))
            if list_info[4]:
                list_widget_item.setIcon(QIcon(list_info[4]))
            self.listWidget.addItem(list_widget_item)
            self.listWidget.setItemWidget(list_widget_item, button)
        elif self.type_manage == 'remove' and (
                not find_mode or self.lineEdit.text().lower().strip() in ''.join(
            list(map(lambda x: x.lower().strip() if type(x) == str else '', list_info)))):
            button = QPushButton(f'{list_info[1] if list_info[1] else ""} {list_info[2] if list_info[2] else ""}')
            self.dict_but[button] = list_info
            button.clicked.connect(self.manege_human)
            list_widget_item = QListWidgetItem()
            list_widget_item.setSizeHint(QSize(25, 50))
            if list_info[4]:
                list_widget_item.setIcon(QIcon(list_info[4]))
            self.listWidget.addItem(list_widget_item)
            self.listWidget.setItemWidget(list_widget_item, button)

    def load_window(self):
        self.listWidget.clear()
        if self.type_manage == 'add':
            list(map(lambda x: self.make_buttons(x), cursor.execute(f'SELECT * from humans').fetchall()))
        else:
            try:
                list(map(lambda x: self.make_buttons(x),
                         map(lambda x: cursor.execute(f'SELECT * from humans WHERE id = {str(x)}').fetchall()[0],
                             self.parent.humans)))
            except TypeError:
                pass


def except_hook(cls, exception, traceback):
    sys.__excepthook__(cls, exception, traceback)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ship_tool_app = MainWindow()
    ship_tool_app.show()
    sys.excepthook = except_hook
    sys.exit(app.exec())
