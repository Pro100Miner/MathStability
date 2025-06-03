from PyQt5.QtCore import QSettings
from PyQt5.QtWidgets import (QApplication, QMainWindow, QMessageBox, QCheckBox)
from src.py_files.mathStab import Ui_MainWindow
from src.py_files.class_Settings import Settings
from src.py_files.class_Report import Report
from src.py_files.message_error import show_warning
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

        try:
            settings = QSettings("Math", "MathStab")
            settings.beginGroup("PlotSettings")
            settings_mapping_sol = {}
            settings_mapping_phase = {}
            keys = list(self.settings.settings_mapping.keys())
            for key, widget in self.settings.settings_mapping.items():
                if self.settings.ui.checkBox.isChecked() and key in keys[0:4]:
                    settings_mapping_sol[key] = widget.value()
                elif self.settings.ui.checkBox_2.isChecked() and key in keys[4:8]:
                    settings_mapping_phase[key] = widget.value()
        except ValueError as e:
            show_warning("Ошибка", str(e))
            return
        app_data['settings_sol'] = settings_mapping_sol
        app_data['settings_phase'] = settings_mapping_phase
        app_data['path_to_tex'] = self.settings.ui.lineEdit.text()

        if not all(getattr(self.ui, field).text() for field in required_fields):
            show_warning("Ошибка", "Введите все значения")
            return
        try:
            float(self.ui.point_t.text())
        except ValueError:
            show_warning("Ошибка", "Некорректное значение точки")
            return
        try:
            app_data['y'] = float(self.ui.y.text())
            app_data['y_diff'] = float(self.ui.y_diff.text())
        except ValueError:
            show_warning("Ошибка", "Некорректные начальные условия")
            return

        try:
            for field in required_fields:
                app_data[field] = getattr(self.ui, field).text()
                sp.sympify(app_data[field])
        except ValueError:
            show_warning("Ошибка", "Введены некорректные данные")
            return
        point = float(self.ui.point_t.text()) if self.ui.solution_in_point.isChecked() else None
        self.second_window = Report(app_data, self.settings, point)
        if self.second_window.run():
            self.second_window.show()





app = QApplication(sys.argv)
application = MainWindow()
application.show()

sys.exit(app.exec())
