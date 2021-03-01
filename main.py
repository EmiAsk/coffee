import sys
import sqlite3
from PyQt5.uic import loadUi

from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QHeaderView, QTableWidgetItem


class CoffeeTable(QMainWindow):
    def __init__(self):
        super(CoffeeTable, self).__init__()
        loadUi('main.ui', self)

        self.connection = sqlite3.connect('coffee.db')
        self.cursor = self.connection.cursor()

        header = self.tableWidget.horizontalHeader()
        for i in range(1, self.tableWidget.columnCount()):
            header.setSectionResizeMode(i, QHeaderView.Stretch)

        self.upload_table()

    def get_all_sorts(self):
        """Получение всех сортов кофе с инфой о них"""

        return self.cursor.execute('''SELECT sorts.id, sorts.name, degrees.name,
                                   sorts.ground_or_grain, sorts.taste, sorts.price, sorts.volume
                                   FROM sorts, degrees WHERE sorts.degree = degrees.id''').fetchall()

    def upload_table(self):
        """Заполнение таблицы"""

        sorts = self.get_all_sorts()
        self.tableWidget.setRowCount(len(sorts))
        for i, row in enumerate(sorts):
            for j, elem in enumerate(row):
                if j == 3:
                    elem = 'Молотый' if elem else 'Зерновой'
                self.tableWidget.setItem(i, j, QTableWidgetItem(str(elem)))
        self.tableWidget.resizeRowsToContents()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = CoffeeTable()
    window.show()
    sys.exit(app.exec_())