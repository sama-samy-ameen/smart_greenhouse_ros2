import time
import rclpy
from rclpy.node import Node

from greenhouse_interfaces.msg import (GreenhouseSensors,GreenhouseCommand,GreenhouseSafety,GreenhouseGUI)


class LoggerNode(Node):

    def __init__(self):
        super().__init__('logger_node')

       
        # Variables for sensor data
        self.temperature = 0.0
        self.humidity = 0.0
        self.light = 0.0
        self.soil_moisture = 0.0

        # Variables for commands
        self.pump_state = False
        self.servo_angle = 0.0
        self.fan_state = False

        # Safety information
        self.emergency = False
        self.safety_message = "No safety message"

        # Irrigation statistics
        self.irrigation_cycles = 0
        self.pump_start_time = None
        self.total_pump_runtime = 0.0

        # Pump flow rate (Replace this value after calibrating the real pump) > mL/min
        self.pump_flow_rate_ml_per_min = 100.0

        # Temperature / Humidity statistics
        self.temperature_sum = 0.0
        self.humidity_sum = 0.0
        self.sensor_readings_count = 0

        self.sensor_subscription = self.create_subscription(GreenhouseSensors,'/greenhouse/sensors',self.sensor_callback,10)
        self.command_subscription = self.create_subscription(GreenhouseCommand,'/greenhouse/commands',self.command_callback,10)
        self.safety_subscription = self.create_subscription(GreenhouseSafety,'/greenhouse/safety',self.safety_callback,10)

        #publisher for gui
        self.gui_publisher = self.create_publisher(GreenhouseGUI,'/greenhouse/gui',10)

        self.timer = self.create_timer(0.5,self.display_status)
        self.gui_timer = self.create_timer(0.5,self.publish_gui_data)

        self.get_logger().info('Logger node started and waiting for messages...')

    
    # Sensor callback
    def sensor_callback(self, msg):

        # Save latest sensor values
        self.temperature = msg.temperature
        self.humidity = msg.humidity
        self.light = msg.light
        self.soil_moisture = msg.soil_moisture

        # Update statistics
        self.temperature_sum += self.temperature
        self.humidity_sum += self.humidity
        self.sensor_readings_count += 1

    # Command callback
    def command_callback(self, msg):

        new_pump_state = msg.pump

        # Detect OFF -> ON transition
        if new_pump_state and not self.pump_state:

            # New irrigation cycle
            self.irrigation_cycles += 1

            # Save pump start time
            self.pump_start_time = time.monotonic()
            self.get_logger().info('Action: Pump ON')

        # Detect ON -> OFF transition
        elif not new_pump_state and self.pump_state:

            if self.pump_start_time is not None:

                runtime = (time.monotonic()- self.pump_start_time)

                self.total_pump_runtime += runtime

                self.pump_start_time = None

            self.get_logger().info('Action: Pump OFF')



        # Save latest command
        self.pump_state = new_pump_state
        self.servo_angle = msg.servo_angle
        self.fan_state = msg.fan

       
    # Safety callback
    def safety_callback(self, msg):

        self.emergency = msg.emergency
        self.safety_message = msg.message

  
    # Calculate average temperature
    def get_average_temperature(self):

        if self.sensor_readings_count == 0:
            return 0.0

        return (self.temperature_sum/ self.sensor_readings_count)

   
    # Calculate average humidity
    def get_average_humidity(self):

        if self.sensor_readings_count == 0:
            return 0.0

        return (self.humidity_sum/ self.sensor_readings_count)

    
    # Calculate current pump runtime
    def get_current_pump_runtime(self):

        runtime = self.total_pump_runtime

        # If pump is currently ON,
        # include the current running time.
        if self.pump_state and self.pump_start_time is not None:

            runtime += (time.monotonic()- self.pump_start_time)
        return runtime

    
    # Calculate estimated water usage
    def get_estimated_water(self):

        runtime_seconds = self.get_current_pump_runtime()

        runtime_minutes = runtime_seconds / 60.0

        water_ml = (runtime_minutes* self.pump_flow_rate_ml_per_min)
        return water_ml

    def publish_gui_data(self):

        msg = GreenhouseGUI()

        msg.temperature = self.temperature
        msg.humidity = self.humidity
        msg.light = self.light
        msg.soil_moisture = self.soil_moisture

        msg.pump = self.pump_state
        msg.fan = self.fan_state
        msg.servo_angle = self.servo_angle
        
        msg.emergency = self.emergency
        msg.safety_message = self.safety_message

        msg.irrigation_cycles = self.irrigation_cycles
        msg.average_temperature = self.get_average_temperature()
        msg.average_humidity = self.get_average_humidity()
        msg.pump_runtime = self.get_current_pump_runtime()
        msg.estimated_water = self.get_estimated_water()

        

        self.gui_publisher.publish(msg)

   
    # Display current status
    def display_status(self):

        average_temperature = self.get_average_temperature()
        average_humidity = self.get_average_humidity()

        water_usage = self.get_estimated_water()

        pump_text = "ON" if self.pump_state else "OFF"
        fan_state= "ON" if self.fan_state else "OFF"

        if self.emergency:
            safety_text = "EMERGENCY"
        else:
            safety_text = "OK"

        self.get_logger().info(
            '\n\n'
            '       SMART GREENHOUSE STATUS\n'
            '\n'
            f'Temperature: {self.temperature:.1f} C\n'
            f'Humidity: {self.humidity:.1f} \n'
            f'Light: {self.light:.1f}\n'
            f'Soil Moisture: {self.soil_moisture:.1f} \n\n'
            f'Pump Command: {pump_text}\n'
            f'Shade Servo: {self.servo_angle:.1f} deg\n\n'
            f'Fan Command: {fan_state}\n'
            f'Safety: {safety_text}\n'
            f'Safety Message: {self.safety_message}\n\n'
            f'Irrigation Cycles: {self.irrigation_cycles}\n'
            f'Average Temperature: {average_temperature:.1f} C\n'
            f'Average Humidity: {average_humidity:.1f} \n'
            f'Pump Runtime: {self.get_current_pump_runtime():.1f} s\n'
            f'Estimated Water: {water_usage:.1f} mL\n'
            '========================================'
        )

def main(args=None):
    rclpy.init(args=args)
    node = LoggerNode()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()