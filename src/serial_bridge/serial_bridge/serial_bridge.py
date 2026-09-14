import rclpy
from rclpy.node import Node
from greenhouse_interfaces.msg import GreenhouseCommand,  GreenhouseSafety, GreenhouseSensors
import random
import serial
import time

#port=
Baud_rate=9600


class SerialBridge(Node):
    def __init__(self):
        super().__init__('serial_bridge')

        #connecting to arduino
        #self.arduino=serial.Serial('/dev/ttyACM0',Baud_rate,timeout=1)
        #time.sleep(2)
        self.get_logger().info("Connected successfully to arduino")


        #publisher of sensor data
        self.publisher=self.create_publisher(GreenhouseSensors,'/greenhouse/sensors',10)
        #data publish rate
        self.timer=self.create_timer(1,self.sensor_data)

        #subsciber of climate controller node
        self.contol_subscriber=self.create_subscription(GreenhouseCommand,'/greenhouse/commands',self.safe_action,10)

        #subscriber of safety node
        self.saftey_subscriber=self.create_subscription(GreenhouseSafety,'/greenhouse/safety',self.urgent_action,10)

        #for bitwise 'the 0 bit for water pump , bit 1 for servo , bit 2 for safety check
        self.command=0  #all commands


    def sensor_data(self):
        
        #reading from arduino
        #data=self.arduino.readline().decode().strip()
        #light,temperature,humidity,soil_moisture=data.split('\n')


            #for testing
            temperature=random.uniform(20.0,55.0)
            humidity=random.uniform(40.0,80.0)
            light=random.uniform(10.0,100.0)
            soil_moisture=random.uniform(10.0,100.0)


            #publishing sensor data  'add float'
            msg=GreenhouseSensors()
            msg.temperature=temperature
            msg.humidity=humidity
            msg.light=light     
            msg.soil_moisture=soil_moisture
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
            



    def urgent_action(self,msg):
        
        if msg.emergency :
           self.command |= (1<<2)
        else:
            self.command &= ~(1<<2)

            

        #send the command to arduino
        #self.arduino.write(bytes([self.command]))



    
        

            









def main(args=None):
    rclpy.init(args=args)
    node=SerialBridge()
    rclpy.spin(node)
    rclpy.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()


