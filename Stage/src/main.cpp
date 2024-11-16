#include <Arduino.h>
#include <BluetoothSerial.h>

#define SIGNAL_OUT 12
#define DIRECTION_OUT 13
#define ENABLE_OUT 14

const int pwmChannel = 0;
BluetoothSerial SerialBT;
// bool dir = true;

void moveStage(int, int, bool);
void parseCommand(String command);

void setup() {
  // pinMode(SIGNAL_OUT, OUTPUT);
  pinMode(DIRECTION_OUT, OUTPUT);
  pinMode(ENABLE_OUT, OUTPUT);

  ledcSetup(pwmChannel, 0, 8);
  ledcAttachPin(SIGNAL_OUT, pwmChannel);

  SerialBT.begin("ESP32StepperControl");

  Serial.begin(921600);
  Serial.print("Setup Finished");
}

void loop() {
  // Check if there is a message
  if (SerialBT.available()){
    String command = SerialBT.readStringUntil('\n');
    Serial.printf("Command recieved: %s\n", command.c_str());

    parseCommand(command);
  }

  delay(100);
}

// Take inputs over bluetooth
// Currently assumes a string of the form "frequency,steps,direction"
void parseCommand(String command){
  // Find indices of commas
  int firstcomma = command.indexOf(',');
  int secondcomma = command.indexOf(',', firstcomma + 1);

  // Split command string into expected variables
  int frequency = command.substring(0, firstcomma).toInt();
  int steps = command.substring(firstcomma + 1, secondcomma).toInt();
  bool direction = command.substring(secondcomma + 1).toInt() == 1;

  Serial.printf("Frequency: %d, Steps: %d, Direction: %d\n", frequency, steps, direction);

  moveStage(frequency, steps, direction);
}

// Moves linear stage
// Takes input a frequency, number of steps, and a direction
// Outputs a square wave to a specified pin with the given frequency and a number of periods equaling the number of steps
// Outputs a direction boolean to another specified pin
// Toggles an enable pin at the beginning and end of the function
void moveStage(int frequency, int steps, bool direction){
  // Calculate total time to do the specified number of steps for the specified frequency in milliseconds
  int period = 1000 / (frequency);
  int duration = period * steps;

  // Enable Motor (Assuming high is enabled, low is disabled)
  digitalWrite(ENABLE_OUT, LOW);
  delay(10);
  // Give direction 
  digitalWrite(DIRECTION_OUT, direction);
  // Turn on PWM Signal
  ledcWriteTone(pwmChannel, frequency);
  // Wait duration
  delay(duration);
  // Turn off PWM Signal
  ledcWriteTone(pwmChannel, 0);
  // Turn off motor
  digitalWrite(ENABLE_OUT, HIGH);
}