import sys
from PyQt5 import uic
from PyQt5.QtWidgets import QApplication, QDialog, QMainWindow
from pathlib import Path



class SafetyPage(QDialog):
     def __init__(self, home_page):
          super().__init__() 
          uic.loadUi(str(Path(__file__).with_name('safety.ui')), self)
          self.home_page = home_page 
          self.safety_back_button.clicked.connect(self.go_back)

     def go_back(self):
         self.hide()
         self.home_page.show()
 
     #function to update data recieved from ros onto the page
     def update_safety( self, pump_state, fan_state, servo_state, emergency_state, safety_message ):
         self.pump_state_label.setText( f"Pump: {pump_state}" )
         self.fan_state_label.setText( f"Fan: {fan_state}" ) 
         self.servo_state_label.setText( f"Servo: {servo_state}" )
         self.emergency_label.setText( f"Emergency: {emergency_state}" )
         self.safety_message_label.setText( f"{safety_message}" )


# Testing
if __name__ == "__main__": 
    app = QApplication(sys.argv)
    home_page = QMainWindow()
    home_page.setWindowTitle("Home")
    home_page.resize(800, 600)
    safety_page = SafetyPage(home_page)
     # Test values 
    safety_page.update_safety( "ON",  "OFF", "90°",  "Normal", "All systems operating normally" ) 
    safety_page.show()
    sys.exit(app.exec_())