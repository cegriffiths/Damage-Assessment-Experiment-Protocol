#include <Arduino.h>
#include <BluetoothSerial.h>

// Pin definitions
#define SIGNAL_OUT 12
#define DIRECTION_OUT 13
#define ENABLE_OUT 14
#define LIMIT_SWITCH_IN 15

const int pwmChannel = 0;
BluetoothSerial SerialBT;
volatile bool limitSwitchTriggered = false;

// Function definitions
void moveStage(int, int, bool);
void parseCommand(String command);
void IRAM_ATTR onLimitSwitchPress();

// Initiate pins and serials
void setup() {
  pinMode(SIGNAL_OUT, OUTPUT);            //Signal to the motor
  pinMode(DIRECTION_OUT, OUTPUT);         //true (1) is towards end with motor, false (0) is towards end without motor
  pinMode(ENABLE_OUT, OUTPUT);            //Low is enabled, High is disabled
  pinMode(LIMIT_SWITCH_IN, INPUT_PULLUP); //Regularly high, low when pressed

  attachInterrupt(digitalPinToInterrupt(LIMIT_SWITCH_IN), onLimitSwitchPress, FALLING);

  SerialBT.begin("ESP32StepperControl");

  Serial.begin(921600);
  Serial.print("Setup Finished");
}

// Listening over serialBT for commands
void loop() {
  // Check if there is a message
  if (SerialBT.available()){
    String command = SerialBT.readStringUntil('\n');
    Serial.printf("Command recieved: %s\n", command.c_str());

    parseCommand(command);
  }

  // Check if the limit switch is triggered
  if (limitSwitchTriggered){
    // Send signals
    SerialBT.println("LIMIT_SWITCH_TRIGGERED");
    Serial.println("Limit switch triggered.");
    limitSwitchTriggered = false;
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
    // Calculate the half period in microseconds
  int halfPeriod = 500000 / frequency;

  // Enable the motor
  digitalWrite(ENABLE_OUT, LOW);
  delay(10);

  // Write the direction to the motor
  digitalWrite(DIRECTION_OUT, direction);

  // Send pulses to the motor (one pulse per step)
  for (int i = 0; i < steps; i++){
    // If the limit switch is trigger, exit the loop to stop the motor
    if (limitSwitchTriggered){
      break;
    }
    digitalWrite(SIGNAL_OUT, HIGH);
    delayMicroseconds(halfPeriod);
    digitalWrite(SIGNAL_OUT, LOW);
    delayMicroseconds(halfPeriod);
  }

  // Disable the motor
  digitalWrite(ENABLE_OUT, HIGH);
}

// ISR on the limit switch
void IRAM_ATTR onLimitSwitchPress(){
  // Turn off motor immediately
  digitalWrite(ENABLE_OUT, HIGH);
  // Flag for void loop
  limitSwitchTriggered = true;
}