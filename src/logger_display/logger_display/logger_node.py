import rclpy
from rclpy.node import Node

from greenhouse_interfaces.msg import (
    GreenhouseSensors,
    GreenhouseCommand,
    GreenhouseSafety)


class LoggerNode(Node):

    def __init__(self):
        super().__init__('logger_node')

        # Subscribe to greenhouse sensors
        self.sensor_subscription = self.create_subscription(
            GreenhouseSensors,
            '/greenhouse/sensors',
            self.sensor_callback,
            10
        )

        # Subscribe to greenhouse commands
        self.command_subscription = self.create_subscription(
            GreenhouseCommand,
            '/greenhouse/commands',
            self.command_callback,
            10
        )

        # Subscribe to greenhouse safety
        self.safety_subscription = self.create_subscription(
            GreenhouseSafety,
            '/greenhouse/safety',
            self.safety_callback,
            10
        )
        self.get_logger().info('Logger node started and waiting for messages...')

    def sensor_callback(self, msg):
        self.get_logger().info(
            f'Sensors | '
            f'Temperature: {msg.temperature} | '
            f'Humidity: {msg.humidity} | '
            f'Light: {msg.light} | '
            f'Soil Moisture: {msg.soil_moisture}'
        )

    def command_callback(self, msg):
        self.get_logger().info(
            f'Command | '
            f'Pump: {msg.pump} | '
            f'Servo Angle: {msg.servo_angle}'
        )

    def safety_callback(self, msg):
        self.get_logger().info(
            f'Safety | '
            f'Emergency: {msg.emergency} | '
            f'Message: {msg.messages}'
        )

def main():
    rclpy.init()
    node = LoggerNode()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__== '__main__':
    main()