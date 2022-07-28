import datetime
import os
import sqlite3
import sys

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
        # self.pushButton.clicked.connect(self.open_peiring)
        self.pushButton_3.clicked.connect(self.open_human)
        # self.pushButton_6.clicked.connect(self.open_stories)

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
        self.select_button = button
        self.dict_but[button] = [self.new_id, 'Новый', 'человек', None, None, None, None, None]
        self.listWidget.setItemWidget(list_widget_item, button)
        self.open_human()
        self.new_human_mode = False
        button.clicked.connect(self.open_human)

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

    def open_human(self):
        if self.select_button != self.sender():
            self.pushButton_5.setVisible(False)
            self.label_4.setVisible(True)
            self.photo = None
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
                self.pushButton_2.setIcon(QIcon('app_image/no_photo.png'))
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
            self.dateEdit.setDate(datetime.date.today())
            self.label_7.setText('')
            self.new_human_mode = False
            self.load_window()


def except_hook(cls, exception, traceback):
    sys.__excepthook__(cls, exception, traceback)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ship_tool_app = MainWindow()
    ship_tool_app.show()
    sys.excepthook = except_hook
    sys.exit(app.exec())
