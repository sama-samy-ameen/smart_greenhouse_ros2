# Smart Greenhouse System

# System Overview

Our project is a smart greenhouse system that combines Arduino and ROS 2 to monitor and control the greenhouse environment.
The Arduino is responsible for interacting directly with the hardware. It collects data from sensors such as the temperature and humidity sensor, light sensor, and soil moisture sensor, and controls the physical actuators, including the water pump, fan, and shade servo motor.

The collected sensor data is transferred from the Arduino to ROS 2 through a serial communication bridge. Within ROS 2, the system is divided into several independent nodes, with each node having a specific responsibility. The climate controller processes the sensor data and makes the normal control decisions for irrigation, ventilation, and shading. A separate safety monitor continuously checks the system for abnormal or unsafe conditions,then the command is sent through bitwise operatio . Finally, a logger/display node provides real-time system information and statistics.


# Challenges Faced :

1- ROS 2 Communication

We did not face any significant problems with the ROS 2 system itself. However, connecting the different nodes and making sure that they could communicate correctly through the appropriate topics and message types took some time during development. We had to test the communication between the nodes and verify that the correct data was being published and received. After establishing the communication structure, the ROS 2 nodes worked together successfully.

2- Sensor Data Integration

One of our biggest challenges was integrating the sensor data correctly with ROS 2. We had to ensure that the data collected by the Arduino was transferred correctly through the serial connection, parsed properly by the serial bridge, and assigned to the correct ROS 2 message fields.

Another challenge was dealing with the different data ranges and formats produced by the sensors. Incorrect sensor values could cause the ROS 2 system to make inappropriate decisions or trigger safety warnings. Therefore, validating the incoming data was an important part of the system.


Another major challenge was ensuring that the system could make the correct control decision at the correct time based on changing sensor readings.For instance, the soil moisture level determines when irrigation should start or stop, while temperature and light levels affect the fan and shade. We had to carefully determine appropriate thresholds and control conditions so that the system would respond correctly to changes in the greenhouse environment without unnecessary or repeated actuator switching.

3- Safety Monitoring

Implementing the safety system also required careful testing because it operates independently from the normal climate-control logic. We had to ensure that the safety monitor could distinguish between valid sensor readings and abnormal data and correctly report emergency conditions.

Testing different sensor values was particularly important because the system needed to respond correctly to invalid readings while continuing normal operation when the data was within the expected ranges.

4- Arduino
Connecting the components correctly on the breadboard and interfacing them with the Arduino required a significant amount of time and effort. However, once the connections were understood, the implementation itself was straightforward.
