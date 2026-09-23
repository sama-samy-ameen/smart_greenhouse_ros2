# Smart Greenhouse System

## ROS 2, Arduino, and PyQt5-Based Greenhouse Monitoring and Control System

---

## 1. Introduction

The Smart Greenhouse is an automated greenhouse monitoring and control system developed using **ROS 2, Arduino, sensors, actuators, and a PyQt5 graphical user interface**.

The main purpose of the system is to monitor environmental conditions inside a greenhouse and control the greenhouse actuators according to the detected conditions. The system monitors:

* Temperature
* Humidity
* Light intensity
* Soil moisture

Based on these measurements, the system can control:

* Water pump
* Cooling fan
* Shade servo

A separate safety system continuously monitors the greenhouse and can detect abnormal sensor readings, communication problems, and emergency conditions.

The system was designed using a modular ROS 2 architecture so that each major function is handled by a separate node. This makes the system easier to test, debug, and extend.

---
────────────┘

# 3. Hardware Components

The Arduino is responsible for reading the physical sensors and controlling the actuators.

| Component            | Arduino Pin | Function                  |
| -------------------- | ----------: | ------------------------- |
| DHT11                |          D2 | Temperature and humidity  |
| Fan Relay            |          D3 | Fan control               |
| Pump Relay           |          D4 | Water pump control        |
| Servo                |          D9 | Shade control             |
| Soil Moisture Sensor |          A1 | Soil moisture measurement |
| LDR                  |          A2 | Light measurement         |

Serial communication between the Arduino and ROS 2 is configured at:

**9600 baud**

---

# 4. Arduino Layer

The Arduino continuously reads the greenhouse sensors and sends their measurements to the ROS 2 system through serial communication.

The sensor data contains:

```text
light, temperature, humidity, soil_moisture
```

The Arduino also receives commands from ROS 2 to control the actuators.

The command information is encoded into a byte so that different bits can represent different actuator commands.

The control bits are:

* Bit 0 → Pump
* Bit 1 → Shade servo
* Bit 2 → Emergency
* Bit 3 → Fan

When an emergency condition is detected, a red led would turn on as an indication of emergency state

---

# 5. ROS 2 Packages and Nodes

The ROS 2 system is divided into several packages.

### 5.1 `greenhouse_interfaces`

This package contains the custom ROS 2 message definitions used for communication between the nodes.

The main messages include:

### `GreenhouseSensors`

```text
float32 temperature
float32 humidity
float32 light
float32 soil_moisture
```

### `GreenhouseCommand`

```text
bool pump
bool fan
float32 servo_angle
bool emergency
```

### `GreenhouseSafety`

```text
bool emergency
string message
```

### `GreenhouseGUI`

This message combines the information required by the graphical interface, including:

```text
temperature
humidity
light
soil_moisture

pump
fan
servo_angle
emergency

irrigation_cycles
average_temperature
average_humidity
pump_runtime
estimated_water

safety_message
```

This allows the GUI to receive the information it needs without implementing the greenhouse decision-making logic itself.

---
# Main Nodes:
# 5.2 Serial Bridge

The `serial_bridge` node is responsible for communication between the Arduino and ROS 2.

Its main responsibilities are:

1. Receiving sensor measurements from the Arduino.
2. Converting the received serial data into ROS 2 messages.
3. Publishing the sensor information on:

```text
/greenhouse/sensors
```

4. Receiving actuator commands from ROS 2.
5. Converting those commands into the appropriate serial command.
6. Sending the commands back to the Arduino.

The Serial Bridge therefore acts as the connection between the physical hardware and the ROS 2 system.

---

# 5.3. Climate Controller

The climate controller processes the sensor information and determines the required actuator states.

For example, soil moisture is used to determine whether irrigation is required, while environmental measurements are used to control the greenhouse climate.

The controller publishes actuator commands through:

```text
/greenhouse/commands
```

The controller is responsible for normal greenhouse operation, while emergency handling is kept separate in the safety system.

---

# 5.4 Safety Monitor

The `safety_monitor` node is independent from the normal climate-control logic.

Its purpose is to monitor the system for unsafe conditions, including:

* Invalid sensor values
* Missing sensor updates
* Communication timeout
* Emergency conditions
* Other abnormal system states

The node publishes safety information through:

```text
/greenhouse/safety
```

The safety monitor can therefore identify problems even when the normal climate controller is operating.

This separation is important because safety handling should not depend entirely on the normal control logic.

---

# 5.5. Logger and Statistics

The `logger_display` node collects the information produced by the greenhouse system and maintains the statistics required for monitoring.

The recorded information includes:

* Current sensor values
* Pump state
* Fan state
* Servo angle
* Emergency state
* Irrigation cycles
* Average temperature
* Average humidity
* Pump runtime
* Estimated water consumption
* Safety message

The estimated water consumption is calculated using the configured pump flow rate of:

**100 mL/min**

The logger publishes the combined GUI information through:

```text
/greenhouse/gui
```

This topic is used by the graphical interface.

---

# 5.6. Graphical User Interface

A PyQt5 graphical interface was developed to provide a simple way to monitor the greenhouse system.

The GUI does not perform the greenhouse control calculations itself.

Instead, it receives already-processed information from ROS 2 and displays it to the user.

This keeps the GUI separate from the system's control and safety logic.

The interface contains four main pages.

---

##  Home Page

The Home page is the main navigation page.

It provides access to:

* Data
* Safety
* Statistics

The pages are managed using a `QStackedWidget`, allowing the user to switch between them without opening multiple independent windows.

---

##  Data Page

The Data page displays the current environmental measurements:

* Temperature
* Humidity
* Light
* Soil moisture

The values are updated when new ROS 2 messages are received.

---

##  Safety Page

The Safety page displays the current system and safety state.

It shows:

* Pump state
* Fan state
* Servo angle
* Emergency state
* Safety message

This allows the user to see both the actuator states and any safety information generated by the ROS 2 system.

---

##  Statistics Page

The Statistics page displays the information collected by the logger.

It includes:

* Number of irrigation cycles
* Average temperature
* Average humidity
* Pump runtime
* Estimated water consumption

The GUI only displays these values. The calculations are performed by the ROS 2 logging/statistics system.

---

# 6. ROS 2–GUI Communication

The GUI subscribes to:

```text
/greenhouse/gui
```

The `GreenhouseGUI` message contains the sensor, actuator, safety, and statistical information needed by the interface.

The GUI uses Qt signals to safely transfer received ROS data to the PyQt5 interface.

---

# 7. Testing With Simulated Sensor Data

Before relying completely on the physical sensors, simulated sensor values were used to test the ROS 2 communication and GUI integration.

The test data is generated using random values.

For example:

```python
soil_moisture = random.randint(0, 1023)
light = random.randint(0, 1023)
temperature = random.uniform(20.0, 35.0)
humidity = random.uniform(0.0, 100.0)
```

The generated values are placed into a `GreenhouseSensors` message:

```python
msg = GreenhouseSensors()

msg.temperature = float(temperature)
msg.humidity = float(humidity)
msg.light = float(light)
msg.soil_moisture = float(soil_moisture)

self.publisher.publish(msg)
```

Using simulated data makes it possible to test the complete ROS 2 communication pipeline even when the physical sensors are not connected.

It also makes it easier to verify that the GUI updates correctly whenever new sensor messages are received.

---

# 8. Demonstration Video

A demonstration video was recorded to show the operation of the integrated system.


The following video demonstrates the complete Smart Greenhouse system, including launching the ROS 2 system, displaying simulated  fake-sensor data, navigating through the GUI pages, and viewing safety and statistics information.

[▶️ Watch the Smart Greenhouse Demo](docs/greenhouse_demo.webm)




# 9. Challenges

Several challenges were encountered during development.

### 9.1 ROS 2 communication

Connecting the different nodes through custom messages and topics required careful coordination between the publishers and subscribers.

### 9.2 Sensor data integration

One of the main challenges was ensuring that the sensor values received from the Arduino matched the expected data format and ranges used by the ROS 2 system.

### 9.3 Hardware wiring

Connecting the sensors, relays, servo, and Arduino through the breadboard required careful wiring and testing.

### 9.4 Safety integration

Safety logic needed to remain independent from normal climate control so that abnormal conditions could be detected even when the normal control system was operating.

### 9.5 GUI integration

Another challenge was connecting a Qt-based graphical application with ROS 2 while keeping the interface responsive.

The final solution separates the ROS subscriber from the PyQt5 widgets and uses Qt signals to transfer the received information safely to the GUI.

### 9.6 Organizing the GUI

The GUI was divided into separate pages for sensor data, safety, and statistics. A `QStackedWidget` was used to manage navigation between these pages.


---






This architecture allows sensing, control, safety, logging, and visualization to operate as separate but connected components.

---
