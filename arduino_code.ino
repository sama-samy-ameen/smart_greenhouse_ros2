#include <Servo.h>
#include <DHT.h>

#define DHT_PIN 2
#define DHT_TYPE DHT11

#define FAN_RELAY_PIN 3
#define PUMP_RELAY_PIN 4
#define SERVO_PIN 9
#define SOIL_MOIST_PIN A1
#define LDR_PIN A2
#define LED 13

//define that relay is an active-low component
#define RELAY_ON LOW
#define RELAY_OFF HIGH

DHT dht(DHT_PIN, DHT_TYPE);
Servo shade;

byte command;

int light;
float temperature;
float humidity;
int soil_moisture;



void setup()
{
  pinMode(PUMP_RELAY_PIN, OUTPUT);
  pinMode(FAN_RELAY_PIN, OUTPUT);
  pinMode(SOIL_MOIST_PIN, INPUT);
  pinMode(LDR_PIN, INPUT);
  pinMode(LED,OUTPUT);

  Serial.begin(9600);

  dht.begin();
  shade.attach(SERVO_PIN);

  // Start with everything off
  digitalWrite(PUMP_RELAY_PIN, RELAY_OFF);
  digitalWrite(FAN_RELAY_PIN, RELAY_OFF);
  digitalWrite(LED,LOW);
  shade.write(0);

  command = 0;
}

void loop()
{
  //reading command from ros nodes
  if (Serial.available() > 0)
  {command = Serial.read();}

//reading sensor data
  light = analogRead(LDR_PIN);
  temperature = dht.readTemperature();
  humidity = dht.readHumidity();
  soil_moisture = analogRead(SOIL_MOIST_PIN);
  
  

// sending data to ros nodes
  Serial.print(light);
  Serial.print(",");

  Serial.print(temperature);
  Serial.print(",");

  Serial.print(humidity);
  Serial.print(",");

  Serial.println(soil_moisture);

// checking for water pump command 'bit 0'
  if (command & (1 << 0))
  {digitalWrite(PUMP_RELAY_PIN, RELAY_ON);}
  else
  {digitalWrite(PUMP_RELAY_PIN, RELAY_OFF);}
  
// checking for shade command 'bit 1'
  if (command & (1 << 1))
  {shade.write(0);}
  else
  {shade.write(90);}

  // checking for fan command 'bit 3'
  if (command & (1 << 3))
  {digitalWrite(FAN_RELAY_PIN, RELAY_ON);}
  else
  {digitalWrite(FAN_RELAY_PIN, RELAY_OFF);}

  
// emergency action  'bit 2'
  //put everything off
  if (command & (1 << 2))
  { digitalWrite(PUMP_RELAY_PIN, RELAY_OFF);
    digitalWrite(FAN_RELAY_PIN, RELAY_OFF);
    shade.write(0);
   //and turn the emergency led on
   for(int i=0;i<4;i++){
    digitalWrite(LED,HIGH);
    delay(10);
    digitalWrite(LED,LOW);
    delay(10);
    }
  }

  delay(25);
}
