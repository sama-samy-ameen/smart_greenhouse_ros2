import rclpy
from rclpy.node import Node
from greenhouse_interfaces import GreenhouseCommand,  GreenhouseSafety, GreenhouseSensors

class SerialBridge(Node):
    def __init__(self):
        super().__init__('serial_bridge')
        