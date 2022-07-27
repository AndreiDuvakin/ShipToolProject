import sys

from PyQt5 import uic
from PyQt5.QtCore import QSize
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QMainWindow, QApplication, QPushButton, QListWidgetItem
import sqlite3

connect = sqlite3.connect('db/ship_tool.db')
cursor = connect.cursor()
STYLE_OF_TEXT_EDIT = '<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.0//EN" "http://www.w3.org/TR/REC-html40/strict.dtd">' \
                     '<html><head><meta name="qrichtext" content="1" /><style type="text/css">' \
                     'p, li { white-space: pre-wrap; }' \
                     '</style></head><body style=" font-family:Arial' \
                     '; font-size:12pt; font-weight:400; font-style:normal;margin-top:0px;' \
                     ' margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0;' \
                     ' text-indent:0px;" align="justify"></body></html>'


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
        self.pushButton.clicked.connect(self.add_human)
        self.dict_but = {}
        self.load_window()

    def add_human(self):
        pass

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

    def make_buttons(self, list_info):
        button = QPushButton(f'{list_info[1]} {list_info[2]}')
        self.dict_but[button] = list_info
        button.clicked.connect(self.open_human)
        return button

    def open_human(self):
        sender = self.sender()
        list_info = self.dict_but[sender]
        self.tabWidget.setVisible(True)
        self.lineEdit_2.setText(f'{list_info[1] if list_info[1] else ""}'
                                f' {list_info[2] if list_info[2] else ""}'
                                f' {list_info[3] if list_info[3] else ""}')
        self.textEdit_2.setText(f'{list_info[5] if list_info[5] else ""}')
        if list_info[4]:
            self.pushButton_2.setIcon(QIcon(list_info[4]))


def except_hook(cls, exception, traceback):
    sys.__excepthook__(cls, exception, traceback)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ship_tool_app = MainWindow()
    ship_tool_app.show()
    sys.excepthook = except_hook
    sys.exit(app.exec())
