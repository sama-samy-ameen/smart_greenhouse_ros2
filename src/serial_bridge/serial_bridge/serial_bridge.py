import rclpy
from rclpy.node import Node
from greenhouse_interfaces.msg import GreenhouseCommand,  GreenhouseSafety, GreenhouseSensors
import random
import serial
import time

Baud_rate=9600


class SerialBridge(Node):
    def __init__(self):
        super().__init__('serial_bridge')

        #connecting to arduino
        self.arduino=serial.Serial('/dev/ttyACM0', Baud_rate,timeout=1)
        time.sleep(2)
        self.get_logger().info("Connected successfully to arduino")


        #publisher of sensor data
        self.publisher=self.create_publisher(GreenhouseSensors,'/greenhouse/sensors',10)
        #data publish rate
        self.timer=self.create_timer(1,self.sensor_data)

        #subsciber of climate controller node
        self.contol_subscriber=self.create_subscription(GreenhouseCommand,'/greenhouse/commands',self.safe_action,10)

        #subscriber of safety node
        self.safety_subscriber=self.create_subscription(GreenhouseSafety,'/greenhouse/safety',self.urgent_action,10)

        #for bitwise 'the 0 bit for water pump , bit 1 for servo , bit 2 for safety check
        self.command=0  #all commands



    def sensor_data(self):
        

        #reading from arduino
        try:
            data=self.arduino.readline().decode().strip()
            light,temperature,humidity,soil_moisture=data.split(',')
        except:
            self.get_logger().info('Error recieved from arduino!')



        #publishing sensor data  'add float'
        msg=GreenhouseSensors()
        msg.temperature=float(temperature)
        msg.humidity=float(humidity)
        msg.light=float(light)   
        msg.soil_moisture=float(soil_moisture)
        self.publisher.publish(msg)

    def safe_action(self,msg):
        #control pump
        if msg.pump:
            self.command |= (1<<0)
        else:
            self.command &= ~(1 << 0)
             

        #controll servo
        if msg.servo_angle:  #any non zero value , which is True
           self.command |= (1<<1)
        else :
            self.command &= ~(1<<1)

        if msg.fan:
            self.command |=(1<<3)
        else:
            self.command &= ~(1<<3)


            



    def urgent_action(self,msg):
        
        if msg.emergency :
           self.command |= (1<<2)
        else:
            self.command &= ~(1<<2)

            

        #send the command to arduino
        self.arduino.write(bytes([self.command]))

 


def main(args=None):
    rclpy.init(args=args)
    node=SerialBridge()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()


