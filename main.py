import sys
import sqlite3
from addEditCoffeeForm import Ui_Form
from ui_main import Ui_MainWindow

from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QHeaderView,\
    QTableWidget, QTableWidgetItem


def except_hook(cls, exception, traceback):
    sys.__excepthook__(cls, exception, traceback)


class CoffeeTable(QMainWindow, Ui_MainWindow):
    """Главное окно с таблицей"""

    def __init__(self):
        super(CoffeeTable, self).__init__()
        self.setupUi(self)
        self.form = None

        self.connection = sqlite3.connect('data/coffee.db')
        self.cursor = self.connection.cursor()

        self.edit_btn.clicked.connect(self.open_edit_form)
        self.add_btn.clicked.connect(self.open_add_form)

        header = self.tableWidget.horizontalHeader()
        for i in range(1, self.tableWidget.columnCount()):
            header.setSectionResizeMode(i, QHeaderView.Stretch)

        self.update_table()

    def update_table(self):
        """Заполнение таблицы"""

        sorts = self.get_all_sorts()
        self.tableWidget.setRowCount(len(sorts))
        for i, row in enumerate(sorts):
            for j, elem in enumerate(row):
                if j == 3:
                    elem = 'Молотый' if elem else 'Зерновой'
                self.tableWidget.setItem(i, j, QTableWidgetItem(str(elem)))
        self.tableWidget: QTableWidget
        self.tableWidget.resizeRowsToContents()

    def open_edit_form(self):
        """Открытие формы редактирования"""

        self.statusBar().showMessage('')
        self.statusBar().setStyleSheet('')

        self.tableWidget: QTableWidget
        selected_cell = self.tableWidget.selectedItems()  # Выбранные ячейки

        if not selected_cell:
            self.statusBar().showMessage('Не выбрана ячейка')
            self.statusBar().setStyleSheet('background-color: red; color: white; font-size: 12pt')
            return

        # получение всей информации о выбранном сорте
        information = [self.tableWidget.item(selected_cell[0].row(), i).text()
                       for i in range(self.tableWidget.columnCount())]

        self.form = EditAddForm(regime=0, info=information, parent=self)
        self.form.show()

    def open_add_form(self):
        """Открытие формы добавления"""

        self.form = EditAddForm(regime=1, info=[], parent=self)
        self.form.show()

    def get_all_sorts(self):
        """Получение всех сортов кофе с инфой о них"""

        return self.cursor.execute('''SELECT sorts.id, sorts.name, degrees.name,
                                   sorts.ground_or_grain, sorts.taste, sorts.price,
                                   sorts.volume FROM sorts, degrees
                                   WHERE sorts.degree = degrees.id''').fetchall()

    def edit_coffee(self, input_data, sort_id):
        """Редактирование сорта кофе"""

        self.cursor.execute('''UPDATE sorts SET name = ?, degree =
                                (SELECT id FROM degrees WHERE name = ?),
                                ground_or_grain = ?, taste = ?, price = ?, volume = ?
                                WHERE id = ?''', (*input_data, sort_id))
        self.connection.commit()

        self.update_table()  # обновление таблицы

    def add_coffee(self, input_data):
        """Добавление сорта кофе"""

        self.cursor.execute('''INSERT INTO sorts (name, degree,
        ground_or_grain, taste, price, volume) VALUES
        (?, (SELECT id FROM degrees WHERE name = ?), ?, ?, ?, ?)''', input_data)

        self.connection.commit()

        self.update_table()  # обновление таблицы

    def get_degrees(self):
        """Получение всех видов обжарки"""

        return self.cursor.execute('''SELECT name FROM degrees''').fetchall()


class EditAddForm(QWidget, Ui_Form):
    """Форма редактирования / добавления"""

    def __init__(self, regime, info, parent: CoffeeTable):
        super(EditAddForm, self).__init__()
        self.setupUi(self)

        self.parent = parent  # окно родитель

        self.mode = regime  # режим (редактирование или добавление)
        self.info = info  # вся информация о выбранном кофе, если есть

        self.fill_in_fields()  # Заполнение формы данными если имеются

        self.setWindowTitle('Добавить кофе' if regime else 'Редактировать кофе')
        self.pushButton.setText('Добавить' if regime else 'Редактировать')
        self.pushButton.clicked.connect(self.slot_function)

    def get_input_data(self):
        """Получение данных с формы, заполненной пользователем"""

        self.error_label.setText('')

        sort = self.sort_line.text()
        degree = self.degree_box.currentText()
        taste = self.taste_edit.toPlainText()
        price = self.price_spin.value()
        volume = self.volume_spin.value()
        ground_or_grain = self.rbtn2.isChecked()
        return [sort, degree, ground_or_grain, taste, price, volume]

    def slot_function(self):
        """Функция обработчик добавления или редактирования кофе по кнопке"""

        input_data = self.get_input_data()

        if not all(input_data[:2] + input_data[3:]):
            self.error_label.setText('Имеются пустые поля')
            return

        if self.mode == 0:
            self.parent.edit_coffee(input_data, self.info[0])
        else:
            self.parent.add_coffee(input_data)
        self.close()

    def fill_in_fields(self):
        """Заполнение формы данными о кофе"""

        degrees = [d[0] for d in self.parent.get_degrees()]
        self.degree_box.addItems(degrees)
        if self.info:
            sort, degree, ground_or_grain, taste, price, volume = self.info[1:]
            self.sort_line.setText(sort)
            self.degree_box.setCurrentIndex(degrees.index(degree))
            self.taste_edit.setPlainText(taste)
            self.price_spin.setValue(float(price))
            self.volume_spin.setValue(float(volume))
            if ground_or_grain == 'Молотый':
                self.rbtn2.toggle()
            else:
                self.rbtn1.toggle()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = CoffeeTable()
    window.show()
    sys.excepthook = except_hook
    sys.exit(app.exec_())