import sys
from PyQt5 import uic
from PyQt5.QtWidgets import QDialog, QApplication, QMainWindow
from PyQt5.QtCore import pyqtSignal
from pathlib import Path

class DataPage(QDialog):
    def __init__(self, home_page):
        super().__init__()
        #loading data.ui file
        uic.loadUi(str(Path(__file__).with_name('data.ui')), self)
        #creating back to home page button
        self.home_page= home_page
        self.data_back_button.clicked.connect(self.go_back)

    def go_back(self):
        self.hide()
        self.home_page.show()

    #function to update data recieved from ros onto the page
    def update_data(self, temperature, humidity, light, soil_moisture):
        self.temperature_label.setText(f"Temperature: {temperature:.1f} C")
        self.humidity_label.setText(f"Humidity: {humidity:.1f}")
        self.light_label.setText(f"Light: {light:.1f}")
        self.soil_moisture_label.setText(f"Soil Moisture: {soil_moisture:.1f}")



#testing...
if __name__ == "__main__":

    app = QApplication(sys.argv)

    home_page = QMainWindow()
    home_page.setWindowTitle("Home")
    home_page.resize(800, 600)

    data_page = DataPage(home_page)

    data_page.update_data(
        24.5,   # temperature
        56.0,   # humidity
        430.0,  # light
        720.0   # soil moisture
    )

    data_page.show()

    sys.exit(app.exec_())
