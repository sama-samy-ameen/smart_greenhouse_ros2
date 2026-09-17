

# Smart Greenhouse Monitoring and Control System

## 1. Project Overview

The Smart Greenhouse is a ROS 2-based monitoring and control system combining Arduino hardware with ROS 2 software. Arduino handles sensor reading and actuator control, while ROS 2 handles decision-making, safety monitoring, communication, and data logging.

The system monitors temperature, humidity, light intensity, and soil moisture, then controls the irrigation pump, greenhouse shade, and ventilation fan accordingly.

## 2. Problem Statement

Traditional greenhouse systems often require continuous manual monitoring and control. This project provides an automated system that can:

- Monitor greenhouse conditions
- Automatically control irrigation
- Automatically control the shade based on light and temperature
- Detect unsafe or abnormal conditions
- Monitor and record system activity

The system separates hardware interaction (Arduino) from decision-making (ROS 2).

## 3. Project Objectives

- Monitor environmental conditions in real time
- Automatically control soil irrigation
- Automatically control the greenhouse shade
- Monitor system safety
- Record and display greenhouse data
- Establish communication between Arduino and ROS 2
- Build a modular system that's easy to test and extend

## 4. Team Members and Responsibilities

- **Member 1** – Serial Bridge
- **Member 2** – Climate Controller
- **Member 3** – Safety Monitor
- **Member 4** – Logger Display
- **All Members** – Arduino hardware and system integration

## 5. ROS 2 Nodes

### 5.1 Serial Bridge

**Function:** Handles communication between Arduino and ROS 2.

**Responsibilities:**
- Receive sensor readings from Arduino via USB Serial
- Parse temperature, humidity, light, and soil moisture values
- Publish sensor data to ROS 2
- Receive actuator commands from ROS 2
- Send actuator commands to Arduino
- Handle invalid serial data without crashing

**Publishes:** `/greenhouse/sensors`
**Subscribes:** `/greenhouse/commands`

### 5.2 Climate Controller

**Function:** Makes automatic control decisions based on sensor readings.

**Irrigation Rules:**
- Soil moisture < 40% → Pump ON
- Soil moisture 40–60% → Keep current pump state
- Soil moisture > 60% → Pump OFF

**Shade Rules:**
- Light > 700 → Close shade (~120° servo angle)
- Light < 400 → Open shade (~0° servo angle)
- Temperature > 35°C → Open shade (heat-safety action)

**Publishes:** `/greenhouse/commands`
**Subscribes:** `/greenhouse/sensors`

### 5.3 Safety Monitor

**Function:** Detects abnormal and unsafe system conditions.

**Responsibilities:**
- Detect invalid sensor values
- Detect missing sensor data
- Detect communication problems
- Monitor sensor timeout
- Monitor excessive continuous pump operation
- Publish emergency states and safety messages

**Safety Conditions (examples):**
- No sensor data for ~5 seconds
- Pump running continuously beyond safety timeout (e.g., 10 seconds)
- Invalid or abnormal sensor readings
- Communication/operating abnormalities

**Publishes:** `/greenhouse/safety`
**Subscribes:** `/greenhouse/sensors`

### 5.4 Logger Display

**Function:** Monitors overall system status and records statistics.

**Responsibilities:**
- Display current temperature, humidity, light level, soil moisture
- Display latest requested pump state
- Display latest servo angle
- Display current safety state and message
- Count irrigation cycles
- Calculate average temperature and humidity for the session
- Estimate water consumption from pump runtime and calibrated flow rate

**Subscribes:** `/greenhouse/sensors`, `/greenhouse/commands`, `/greenhouse/safety`

## 6. ROS 2 Topics

- `/greenhouse/sensors` (GreenhouseSensors) – published by Serial Bridge; subscribed by Climate Controller, Safety Monitor, Logger
- `/greenhouse/commands` (GreenhouseCommand) – published by Climate Controller; subscribed by Serial Bridge, Logger
- `/greenhouse/safety` (GreenhouseSafety) – published by Safety Monitor; subscribed by Logger

## 7. Custom Interfaces

**GreenhouseSensors.msg**
```
float32 temperature
float32 humidity
float32 light
float32 soil_moisture
```

**GreenhouseCommand.msg**
```
bool pump
float32 servo_angle
```

**GreenhouseSafety.msg**
```
bool emergency
string messages
```

## 8. Hardware Components

**Arduino Uno R3** – Main microcontroller for direct sensor/actuator interaction.

**DHT11** – Measures air temperature and humidity. Chosen for being simple, inexpensive, and suitable for an educational prototype.

**GL5528 5mm LDR (Photoresistor)** – Measures light intensity via a voltage divider (with a 10 kΩ resistor). Used to control the shade.

**Soil Moisture Sensor (resistive, analog)** – Measures soil moisture. Analog output is used since the project needs different thresholds for irrigation control. Requires calibration since raw readings don't map directly to percentage.

**5V Submersible Water Pump** – ~100–300 L/h flow rate, ~1 m max head. Controlled via relay since it needs more current than an Arduino GPIO pin can safely provide.

**2-Channel 5V Low-Level Relay Module** – Mechanical relay, 5V trigger, up to 10A/30V DC contact rating. Channel 1: water pump. Channel 2: ventilation fan.

**SG90 Servo Motor** – Controls the greenhouse shade via PWM directly from Arduino. 0° = shade open, 120° = shade closed.

**F130 5V DC Motor** – Used as a small ventilation fan (stall current ~0.8–1.2A), controlled via the second relay channel.

**12V Battery** – Main power source for external loads, stepped down to 5V via the LM2596S buck converter.

**LM2596S Buck Converter** – Input ~3–40V, adjustable output ~1.5–35V. Steps battery voltage down to ~5V. Chosen over a 7805 linear regulator because a switching regulator has lower power loss and less heat at higher currents.

## 9. Control Logic

**Irrigation Control** uses two thresholds for hysteresis:
- Below 40% → Pump ON
- 40–60% → Keep previous pump state
- Above 60% → Pump OFF

This avoids rapid ON/OFF switching from small sensor fluctuations.

**Shade Control:**
- Light above 700 → Close shade
- Light below 400 → Open shade
- Temperature above 35°C → Open shade (heat safety)

## 10. Problems Faced and Solutions

**10.1 Voltage Regulator Selection**
- Problem: Need a stable 5V supply while the battery voltage is higher.
- Solution: Used an LM2596S adjustable buck converter to step down to 5V.

**10.2 7805 vs LM2596**
A 7805 linear regulator dissipates the voltage difference as heat (Power Loss = (Vin − Vout) × Current), which becomes significant at higher currents. The LM2596S switching regulator is more suitable for powering multiple loads.

**10.3 Relay Selection**
- Problem: A 5V Solid State Relay was initially considered, but the available SSR was intended for AC loads, while the pump and fan are DC loads.
- Solution: Used a 5V mechanical relay module that supports DC switching.

**10.4 Pump Current**
- Problem: The pump requires more current than an Arduino GPIO pin can provide.
- Solution: Arduino only controls the relay; the pump gets its power from the external 5V supply.

**10.5 Soil Moisture Calibration**
- Problem: Raw analog readings don't directly represent an accurate moisture percentage.
- Solution: Calibrate the sensor using dry and wet soil conditions before applying the 40%/60% thresholds.

**10.6 Pump Switching**
- Problem: Small changes in soil moisture can cause rapid pump ON/OFF switching.
- Solution: Use two different thresholds (hysteresis) to prevent unnecessary rapid switching.

## 11. Communication

Arduino communicates with ROS 2 through USB Serial. Sensor data is sent in this format:

```
TEMP:27.5,HUM:61.0,LIGHT:730,SOIL:35
```

The Serial Bridge parses this data and publishes it as a `GreenhouseSensors` message. The Climate Controller processes it and publishes a `GreenhouseCommand` message. The Serial Bridge receives the command and sends it to Arduino to control the actuators. The Safety Monitor independently monitors sensor data and publishes safety information. The Logger Display subscribes to all topics to display current status and statistics.

## 12. Example Logger Output

```
========================================
SMART GREENHOUSE STATUS
========================================
Temperature: 32.0 C
Humidity: 60.0 %
Light: 800
Soil Moisture: 30.0 %
Pump Command: ON
Shade Servo: 120 deg
Safety: OK
Irrigation Cycles: 3
Estimated Water: 200 mL
========================================
```

## 13. Conclusion

The Smart Greenhouse project demonstrates the integration of Arduino hardware with ROS 2 for environmental monitoring and automatic control. Arduino handles direct hardware interaction, while ROS 2 handles decision-making, safety monitoring, communication, and logging. The modular design allows each part of the system to be developed and tested independently while working together as one complete system.


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
