from PyQt5.QtWidgets import (QApplication, QMainWindow, QMessageBox, QCheckBox)
from src.py_files.mathStab import Ui_MainWindow
from src.py_files.class_Settings import Settings
from src.py_files.class_Report import Report
import sys
import sympy as sp


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.second_window = None
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.settings = Settings()
        self.ui.pushButton.clicked.connect(self.open_report)
        self.ui.action.triggered.connect(self.settings.show)

    def open_report(self):
        app_data = {}
        required_fields = ['a', 'b', 'c', 'd', 'y', 'y_diff']
        if self.ui.solution_in_point.isChecked():
            required_fields.append('point_t')

        if not all(getattr(self.ui, field).text() for field in required_fields):
            self.show_warning("Ошибка", "Введите все значения")
            return
        try:
            float(self.ui.point_t.text())
        except ValueError:
            self.show_warning("Ошибка", "Некорректное значение точки")
            return
        try:
            app_data['y'] = float(self.ui.y.text())
            app_data['y_diff'] = float(self.ui.y_diff.text())
        except ValueError:
            self.show_warning("Ошибка", "Некорректные начальные условия")
            return

        try:
            for field in required_fields:
                app_data[field] = getattr(self.ui, field).text()
                sp.sympify(app_data[field])
        except ValueError:
            self.show_warning("Ошибка", "Введены некорректные данные")
            return
        point = float(self.ui.point_t.text()) if self.ui.solution_in_point.isChecked() else None
        self.second_window = Report(app_data, self.settings, point)
        self.second_window.show()

    def show_warning(self, title, message):
        msg_box = QMessageBox(self)
        msg_box.setIcon(QMessageBox.Warning)
        msg_box.setWindowTitle(title)
        msg_box.setText(message)
        msg_box.setStandardButtons(QMessageBox.Ok)
        msg_box.exec()


app = QApplication(sys.argv)
application = MainWindow()
application.show()

sys.exit(app.exec())
