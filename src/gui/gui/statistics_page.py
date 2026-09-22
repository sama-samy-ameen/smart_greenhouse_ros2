import os
from PyQt5 import uic
from PyQt5.QtWidgets import QMainWindow


class StatisticsPage(QMainWindow):

    def __init__(self, home_page):
        super().__init__()

        # Load statistics.ui
        ui_path = os.path.join(
            os.path.dirname(os.path.dirname(__file__)),"ui","statistics.ui")
        uic.loadUi(ui_path, self)

        # Home page
        self.home_page = home_page

        # Back button
        self.statistics_back_button.clicked.connect(self.go_back)

    def go_back(self):
        self.hide()
        self.home_page.show()

    def update_statistics(self,irrigation_cycles,avg_temperature,avg_humidity,pump_runtime,estimated_water):
        self.irrigation_cycles_label.setText(str(irrigation_cycles))
        self.avg_temperature_label.setText(f"{avg_temperature:.1f} °C")
        self.avg_humidity_label.setText(f"{avg_humidity:.1f} %")
        self.pump_runtime_label.setText(f"{pump_runtime:.1f} s")
        self.estimated_water_label.setText(f"{estimated_water:.1f} mL")