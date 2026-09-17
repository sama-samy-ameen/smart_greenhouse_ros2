import math
import rclpy
from rclpy.node import Node
from greenhouse_interfaces.msg import GreenhouseSensors, GreenhouseCommand, GreenhouseSafety


class SafetyMonitor(Node):

    PUMP_TIMEOUT = 7.0
    SENSOR_TIMEOUT = 30.0

    def __init__(self):
        super().__init__('safety_monitor')

        # Time when the last sensor message was received
        self.last_sensor_time = self.get_clock().now()

        # Pump state and start time
        self.pump_on = False
        self.pump_start_time = None

        # Store the latest sensor safety message
        self.current_safety_message = 'Safety OK'

        # Subscribe to sensor data
        self.sensor_subscription = self.create_subscription(GreenhouseSensors, '/greenhouse/sensors', self.sensor_callback, 10)

        # Subscribe to actuator commands
        self.command_subscription = self.create_subscription(GreenhouseCommand, '/greenhouse/commands', self.command_callback, 10)

        # Publish safety information
        self.safety_publisher = self.create_publisher(GreenhouseSafety, '/greenhouse/safety', 10)

        # Check system safety every second
        self.timer = self.create_timer(1.0, self.check_safety)

        self.get_logger().info('Safety Monitor started')

    def sensor_callback(self, msg):

        # Update the time of the latest sensor message
        self.last_sensor_time = self.get_clock().now()

        # Check if sensor values are valid
        if not self.valid_sensor_data(msg):

            self.current_safety_message = 'Invalid sensor data'

            self.publish_safety(True, self.current_safety_message)
            return
        # Check for sensor warnings
        self.check_current_sensors(msg)


    def command_callback(self, msg):
        if msg.pump==self.pump_on:
            return

        # Pump changed from OFF to ON
        if msg.pump and not self.pump_on:

            self.pump_on = True
            self.pump_start_time = self.get_clock().now()

            self.get_logger().info('Pump turned ON')

        # Pump changed from ON to OFF
        elif not msg.pump and self.pump_on:

            self.pump_on = False
            self.pump_start_time = None

            self.get_logger().info('Pump turned OFF')

    def valid_sensor_data(self, msg):

        # Check that all sensor values are valid numbers
        if not math.isfinite(msg.temperature):
            return False
        if not math.isfinite(msg.humidity):
            return False
        if not math.isfinite(msg.light):
            return False
        if not math.isfinite(msg.soil_moisture):
            return False
        # Humidity should be between 0% and 100%
        if msg.humidity < 0 or msg.humidity > 100:
            return False
        # Soil moisture should be between 0% and 1023
        if msg.soil_moisture < 0 or msg.soil_moisture > 1023:
            return False
        # temperatue should be between 0 and 80
        if msg.temperature < 0 or msg.temperature >80:
            return False
        
        # Light cannot be negative
        if msg.light < 0 :
            return False
        return True

    def check_current_sensors(self, msg):

        # High temperature
        if msg.temperature > 23:

            self.current_safety_message = ('High temperature: fan should be open')
        # Very high humidity
        elif msg.humidity > 85:

            self.current_safety_message = ('High humidity: increase ventilation')
        # Very low humidity
        elif msg.humidity < 30:

            self.current_safety_message = ('Low humidity: plants may lose water quickly')
        # Very wet soil
        elif msg.soil_moisture < 920:

            self.current_safety_message = ('Soil moisture is too high: avoid overwatering')
        # Very dry soil
        elif msg.soil_moisture > 400:

            self.current_safety_message = ('Soil moisture is very low: irrigation may be needed')
        # Very low light
        elif msg.light < 200:

            self.current_safety_message = ('Low light: plants may need more light')

        elif msg.light > 1023:
            self.current_safety_message = ('High light: plants may exposed to exessive light')
            
        
        else:

            self.current_safety_message = 'Safety OK'

    def check_safety(self):

        now = self.get_clock().now()

        # Calculate time since the last sensor message
        sensor_elapsed = (now - self.last_sensor_time).nanoseconds / 1e9

        # Critical: no sensor data for too long
        if sensor_elapsed > self.SENSOR_TIMEOUT:
            self.get_logger().error('CRITICAL: No sensor data recieved for 5 seconds!')
            self.publish_safety(True, 'No sensor data received for 5 seconds')
            return
        
        # Critical: pump running for too long
        if self.pump_on and self.pump_start_time is not None:

            pump_elapsed = (now - self.pump_start_time).nanoseconds / 1e9

            if pump_elapsed > self.PUMP_TIMEOUT:

                self.publish_safety(True, 'Pump running too long')
                return

        # No critical problem
        # Publish the latest sensor safety status
        self.publish_safety(False, self.current_safety_message)

    def publish_safety(self, emergency, message):

        msg = GreenhouseSafety()

        msg.emergency = emergency
        msg.message = message

        self.safety_publisher.publish(msg)


def main(args=None):

    rclpy.init(args=args)

    node = SafetyMonitor()

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()

