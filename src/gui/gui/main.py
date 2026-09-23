#pyqt imports
import sys
import threading
from pathlib import Path
from PyQt5 import uic
from PyQt5 import QtWidgets, QtCore
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QDialog
from PyQt5.QtCore import pyqtSignal, QObject
#ros imports
import rclpy
from rclpy.node import Node
from greenhouse_interfaces.msg import GreenhouseGUI


# signal  'connecting ros with the gui'
class ROSSignalBridge(QObject):
    data_signal = pyqtSignal(float, float, float, float)
    safety_signal = pyqtSignal(bool, bool, float, bool, str)
    statistics_signal = pyqtSignal(int, float, float, float, float)


# GreenhouseGUI subscriber ' has everything the logger is displaying'
class ROSsubscriber(Node):
    def __init__(self,bridge):
        super().__init__('logger_subscriber')


        self.bridge=bridge

        self.gui_subsriber=self.create_subscription(GreenhouseGUI,'/greenhouse/gui',self.gui_callback,10)

    def gui_callback(self,msg):

        self.temperature =msg.temperature
        self.humidity=msg.humidity 
        self.light=msg.light 
        self.soil_moisture=msg.soil_moisture 
        
        self.pump_state=msg.pump 
        self.fan_state=msg.fan 
        self.servo_angle=msg.servo_angle 
                
        self.emergency=msg.emergency 
        self.safety_message=msg.safety_message 
        
        self.irrigation_cycles=msg.irrigation_cycles 
        self.avg_temp=msg.average_temperature 
        self.avg_hum=msg.average_humidity 
        self.pump_runtime=msg.pump_runtime 
        self.estimated_water=msg.estimated_water 

        #all data signals
        self.bridge.data_signal.emit(self.temperature,self.humidity,self.light,self.soil_moisture)

        self.bridge.safety_signal.emit(self.pump_state,self.fan_state,self.servo_angle,self.emergency,self.safety_message)

        self.bridge.statistics_signal.emit(self.irrigation_cycles,self.avg_temp,self.avg_hum,self.pump_runtime,self.estimated_water)   

       


# pyqt part and pages connections
class home(QMainWindow):
    def __init__(self):
        super(home, self).__init__()
        uic.loadUi(str(Path(__file__).with_name('home.ui')), self)

        # pages widget
        self.sensor_page=DataPage()
        self.status_page=SafetyPage()
        self.statistics_page=StatisticsPage()

        self.data_button.clicked.connect(self.data)
        self.safety_button.clicked.connect(self.status)
        self.statistics_button.clicked.connect(self.statistics)


#   displaying sensor data 
    def data(self):
        
        print('sensor_page')   
        widget.setCurrentWidget(self.sensor_page)

    def status(self):
        
        print('status_page')
        widget.setCurrentWidget(self.status_page)

    def statistics(self):
        
        print('statistics_page')
        widget.setCurrentWidget(self.statistics_page)





class DataPage(QDialog):
    def __init__(self):
        super().__init__()
        #loading data.ui file
        uic.loadUi(str(Path(__file__).with_name('data.ui')), self)
        #creating back to home page button
        self.data_back_button.clicked.connect(self.go_back)


    def go_back(self):
        widget.setCurrentIndex(0)
        print('back to main page')
        
    #function to update data recieved from ros onto the page
    def update_data(self, temperature, humidity, light, soil_moisture):
        self.temperature_label.setText(f"Temperature: {temperature:.1f} C")
        self.humidity_label.setText(f"Humidity: {humidity:.1f}")
        self.light_label.setText(f"Light: {light:.1f}")
        self.soil_moisture_label.setText(f"Soil Moisture: {soil_moisture:.1f}")



class SafetyPage(QDialog):
    def __init__(self):
        super().__init__()
        uic.loadUi(str(Path(__file__).with_name('safety.ui')), self)
        self.safety_back_button.clicked.connect(self.go_back)

    def go_back(self):
        widget.setCurrentIndex(0)
        print('back to main page')

    # function to update data recieved from ros onto the page
    def update_safety(self, pump_state, fan_state, servo_state, emergency_state, safety_message):
        self.pump_state_label.setText(f"Pump: {pump_state}")
        self.fan_state_label.setText(f"Fan: {fan_state}")
        self.servo_state_label.setText(f"Servo: {servo_state}")
        self.emergency_label.setText(f"Emergency: {emergency_state}")
        self.safety_message_label.setText(f"{safety_message}")


class StatisticsPage(QMainWindow):

    def __init__(self):
        super().__init__()
        # Load statistics.ui
        uic.loadUi(str(Path(__file__).with_name('statistics.ui')), self)
        # Back button
        self.statistics_back_button.clicked.connect(self.go_back)

    def go_back(self):
        widget.setCurrentIndex(0)
        print('back to main page')

    def update_statistics(self,irrigation_cycles,avg_temperature,avg_humidity,pump_runtime,estimated_water):
        self.irrigation_cycles_label.setText(str(irrigation_cycles))
        self.avg_temperature_label.setText(f"{avg_temperature:.1f} °C")
        self.avg_humidity_label.setText(f"{avg_humidity:.1f} %")
        self.pump_runtime_label.setText(f"{pump_runtime:.1f} s")
        self.estimated_water_label.setText(f"{estimated_water:.1f} mL")

# showing up everything
def main(args=None):
        
        rclpy.init(args=args)

        app = QApplication(sys.argv)


        global widget
        widget = QtWidgets.QStackedWidget()
        widget.setFixedWidth(460)
        widget.setFixedHeight(620)
        main_window = home()
        widget.addWidget(main_window)
        widget.addWidget(main_window.sensor_page)
        widget.addWidget(main_window.status_page)   
        widget.addWidget(main_window.statistics_page)

        bridge = ROSSignalBridge()
        bridge.data_signal.connect(main_window.sensor_page.update_data)
        bridge.safety_signal.connect(main_window.status_page.update_safety)
        bridge.statistics_signal.connect(main_window.statistics_page.update_statistics)

        ros_node = ROSsubscriber(bridge)
        ros_thread = threading.Thread(
            target=rclpy.spin,
            args=(ros_node,),
            daemon=True)
        ros_thread.start()
        
        
        widget.show()

        sys.exit(app.exec_())



if __name__ == '__main__':
        main()




