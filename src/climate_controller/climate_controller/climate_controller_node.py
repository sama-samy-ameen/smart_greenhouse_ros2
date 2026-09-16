import rclpy
from rclpy.node import Node
from greenhouse_interfaces.msg import GreenhouseSensors, GreenhouseCommand

class ClimateControl(Node):
    def __init__(self):
        super().__init__('climate_controller')
        #all these values are susceptible to change basedon the arduino sensor sensitivity later on
        self.soil_on_threshold=900.0
        self.soil_off_threshold=500.0
        self.light_high_threshold=1015.0
        self.light_low_threshold=400.0
        self.temperature=27.0
        self.current_pump_state= False

        self.sensor_subscriber=self.create_subscription(
            GreenhouseSensors,
            '/greenhouse/sensors',
            self.sensor_callback,
            10
        )

        self.publisher_=self.create_publisher(
            GreenhouseCommand,
            '/greenhouse/commands',
            10
        )
        self.get_logger().info("Climate controller node initialized and listening!")

    def sensor_callback(self, msg):
        command=GreenhouseCommand()
        if msg.soil_moisture>self.soil_on_threshold:
            self.current_pump_state=True
        if msg.soil_moisture<self.soil_off_threshold:
            self.current_pump_state=False

        command.pump=self.current_pump_state

        if msg.temperature> self.temperature:
            command.fan=True
        else:
            command.fan=False

        if msg.light> self.light_high_threshold:
            command.servo_angle= 120.0
        elif msg.light< self.light_low_threshold:
            command.servo_angle=0.0
        else:
            command.servo_angle=0.0

        self.publisher_.publish(command)

def main(args=None):
    rclpy.init(args=args)
    node=ClimateControl()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()