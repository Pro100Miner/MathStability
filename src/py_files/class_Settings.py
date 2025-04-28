from src.py_files.settings import Ui_Settings
from PyQt5.QtWidgets import QWidget
from PyQt5.QtCore import QSettings


class Settings(QWidget):
    def __init__(self):
        super().__init__()
        self.ui = Ui_Settings()
        self.ui.setupUi(self)
        self.settings_mapping = {
            "t_min": self.ui.spinBox_3,
            "t_max": self.ui.spinBox_4,
            "y_min": self.ui.spinBox_5,
            "y_max": self.ui.spinBox_6,
            "y'_min": self.ui.spinBox_9,
            "y'_max": self.ui.spinBox_10,
            "y_min_f": self.ui.spinBox_11,
            "y_max_f": self.ui.spinBox_12,
        }
        self.default_settings = {
            "t_min": 0,
            "t_max": 10,
            "y_min": 0,
            "y_max": 10,
            "y'_min": 0,
            "y'_max": 10,
            "y_min_f": 0,
            "y_max_f": 10,
        }

        self.change_values(1, 4, self.ui.checkBox, "График решения")
        self.change_values(5, 8, self.ui.checkBox_2, "Фазовый портрет")
        self.ui.checkBox.stateChanged.connect(lambda: self.change_values(1, 4, self.ui.checkBox, "График решения"))
        self.ui.checkBox_2.stateChanged.connect(lambda: self.change_values(5, 8, self.ui.checkBox_2, "Фазовый портрет"))
        self.load_settings()  # Установить значения
        self.ui.pushButton_2.clicked.connect(self.close_window)  # Закрытие окна
        self.ui.pushButton.clicked.connect(self.save_settings)  # Сохранение настроек
        self.ui.pushButton_3.clicked.connect(self.reset_settings)  # Сбросить настройки до заводских

    def save_settings(self):
        settings = QSettings("Math", "MathStab")
        settings.beginGroup("PlotSettings")
        for key, widget in self.settings_mapping.items():
            settings.setValue(key, widget.value())
        settings.endGroup()

        self.ui.label.setText("Данные сохранены")
        self.ui.label.setStyleSheet("color: green;")

    def load_settings(self):
        settings = QSettings("Math", "MathStab")
        settings.beginGroup("PlotSettings")
        for key, widget in self.settings_mapping.items():
            widget.setValue(settings.value(key, defaultValue=self.default_settings[key], type=int))
        settings.endGroup()

    def reset_settings(self):
        # Сброс значений спинбоксов
        for key, widget in self.settings_mapping.items():
            widget.setValue(self.default_settings[key])
        # Сброс значений в реестре
        settings = QSettings("Math", "MathStab")
        settings.beginGroup("PlotSettings")
        for key, _ in self.settings_mapping.items():
            settings.setValue(key, self.default_settings[key])
        settings.endGroup()

        self.ui.label.setStyleSheet("color: red;")
        self.ui.label.setText("Настройки сброшены на значения по умолчанию")

    def change_values(self, start, end, check_box, text):
        name_spin_boxes = [key for key, _ in self.settings_mapping.items()][start-1:end]
        widgets = [self.settings_mapping[i] for i in name_spin_boxes]
        for widget in widgets:
            widget.setEnabled(True if check_box.isChecked() else False)
        check_box.setText(text if check_box.isChecked() else text + " (Auto)")

    def close_window(self):
        self.close()
        self.ui.label.setText("")

