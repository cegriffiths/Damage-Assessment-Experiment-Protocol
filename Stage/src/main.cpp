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
void moveStage(int, int, int, bool);
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
  Serial.print("Setup Finished!");
  // digitalWrite(ENABLE_OUT, LOW);

}

// Listening over serialBT for commands
void loop() {
  // Check if there is a message
  if (SerialBT.available()){
    Serial.println("BT Command Recieved");
    String command = SerialBT.readStringUntil('\n');
    Serial.printf("Command recieved: %s\n", command.c_str());

    parseCommand(command);
  }

  // // Check if the limit switch is triggered
  // if (limitSwitchTriggered){
  //   // Send signals
  //   SerialBT.println("LIMIT_SWITCH_TRIGGERED");
  //   Serial.println("Limit switch triggered.");
  //   limitSwitchTriggered = false;
  // }

  delay(10);
  // Serial.println("looping");
}

// Take inputs over bluetooth
// Currently assumes a string of the form "frequency,steps,direction"
void parseCommand(String command){
  // Find indices of commas
  int firstcomma = command.indexOf(',');
  int secondcomma = command.indexOf(',', firstcomma + 1);
  int thirdcomma = command.indexOf(',', secondcomma + 1);

  // Split command string into expected variables
  int steps = command.substring(0, firstcomma).toInt();
  int frequency = command.substring(firstcomma, secondcomma).toInt();
  int delta = command.substring(secondcomma, thirdcomma).toInt();
  bool direction = command.substring(thirdcomma + 1).toInt() == 1;

  Serial.printf("Steps: %d, Frequency: %d, Delta: %d, Direction: %d\n", steps, frequency, delta, direction);

  // int frequency = command.substring(0, firstcomma).toInt();
  // int steps = command.substring(firstcomma + 1, secondcomma).toInt();
  // bool direction = command.substring(secondcomma + 1).toInt() == 1;

  // Serial.printf("Frequency: %d, Steps: %d, Direction: %d\n", frequency, steps, direction);

  moveStage(steps, frequency, delta, direction);
}

// Moves linear stage
// Takes input a frequency, number of steps, and a direction
// Outputs a square wave to a specified pin with the given frequency and a number of periods equaling the number of steps
// Outputs a direction boolean to another specified pin
// Toggles an enable pin at the beginning and end of the function
void moveStage(int steps, int frequency, int delta, bool direction){
  // If going towards home and already home, to not move motor
  if (direction == 0 && digitalRead(LIMIT_SWITCH_IN) == LOW){
    // Send signals
    SerialBT.println("LIMIT_STOP");
    Serial.println("Already home: Limit stop");
  }
  else{
    // Set half period at full velocity
    int halfPeriod = 500000 / frequency;

    int halfPeriodDelta = 500000 / delta;
    int accelHalfPeriod = 500000 / delta;

    // Number of steps to complete acceleration
    int Na = frequency / delta;
    // Number of steps at constant velocity
    int Nv = steps - 2*Na;

    // Enable the motor
    digitalWrite(ENABLE_OUT, LOW);
    delay(10);

    // Write the direction to the motor
    digitalWrite(DIRECTION_OUT, direction);

    // Send pulses to the motor (one pulse per step) for acceleration
    for (int i = 0; i < Na; i++){
      // If we are going towards home and limit switch is triggered, 
      // turn off motor and say the limit switch is triggered
      if ((limitSwitchTriggered && direction == 0)){
        // Turn off motor immediately
        digitalWrite(ENABLE_OUT, HIGH);
        // Send signals
        SerialBT.println("LIMIT_STOP");
        Serial.println("Limit stop");
        // Flip Flag
        limitSwitchTriggered = false;
        return;
      }
      // If we are going away from home and are out of the range of the limit switch and the limit switch is triggered,
      // turn off motor and say we manually stopped
      else if (limitSwitchTriggered && direction == 1 &&  i > 15){
        // Turn off motor immediately
        digitalWrite(ENABLE_OUT, HIGH);
        // Send signals
        SerialBT.println("MANUAL_STOP");
        Serial.println("Manual stop");
        // Flip Flag
        limitSwitchTriggered = false;
        return;
      }
      // If we are going away from home and are in range of the limit switch and it is triggered (unpressing bounce),
      // re-enable the motor and keep going
      else if (limitSwitchTriggered && direction == 1){
        digitalWrite(ENABLE_OUT, LOW);
        limitSwitchTriggered = false;
      }
      // Do one full cycle
      digitalWrite(SIGNAL_OUT, HIGH);
      delayMicroseconds(halfPeriodDelta*(i + 1));
      digitalWrite(SIGNAL_OUT, LOW);
      delayMicroseconds(halfPeriodDelta*(i + 1));
      Serial.printf("Step: %d\tHalf Period: %d\n", i, halfPeriodDelta*(i + 1));
    }



    // Send pulses to the motor (one pulse per step) for constant velocity
    for (int i = 0; i < Nv; i++){
      // If we are going towards home and limit switch is triggered, 
      // turn off motor and say the limit switch is triggered
      if ((limitSwitchTriggered && direction == 0)){
        // Turn off motor immediately
        digitalWrite(ENABLE_OUT, HIGH);
        // Send signals
        SerialBT.println("LIMIT_STOP");
        Serial.println("Limit stop");
        // Flip Flag
        limitSwitchTriggered = false;
        return;
      }
      // If we are going away from home and are out of the range of the limit switch and the limit switch is triggered,
      // turn off motor and say we manually stopped
      else if (limitSwitchTriggered && direction == 1 &&  i > 15){
        // Turn off motor immediately
        digitalWrite(ENABLE_OUT, HIGH);
        // Send signals
        SerialBT.println("MANUAL_STOP");
        Serial.println("Manual stop");
        // Flip Flag
        limitSwitchTriggered = false;
        return;
      }
      // If we are going away from home and are in range of the limit switch and it is triggered (unpressing bounce),
      // re-enable the motor and keep going
      else if (limitSwitchTriggered && direction == 1){
        digitalWrite(ENABLE_OUT, LOW);
        limitSwitchTriggered = false;
      }
      // Do one full cycle
      digitalWrite(SIGNAL_OUT, HIGH);
      delayMicroseconds(halfPeriod);
      digitalWrite(SIGNAL_OUT, LOW);
      delayMicroseconds(halfPeriod);
      Serial.printf("Step: %d\n", i + Na + 1);
    }



    // Send pulses to the motor (one pulse per step) for decceleration
    for (int i = 0; i < Na; i++){
      // If we are going towards home and limit switch is triggered, 
      // turn off motor and say the limit switch is triggered
      if ((limitSwitchTriggered && direction == 0)){
        // Turn off motor immediately
        digitalWrite(ENABLE_OUT, HIGH);
        // Send signals
        SerialBT.println("LIMIT_STOP");
        Serial.println("Limit stop");
        // Flip Flag
        limitSwitchTriggered = false;
        return;
      }
      // If we are going away from home and are out of the range of the limit switch and the limit switch is triggered,
      // turn off motor and say we manually stopped
      else if (limitSwitchTriggered && direction == 1 &&  i > 15){
        // Turn off motor immediately
        digitalWrite(ENABLE_OUT, HIGH);
        // Send signals
        SerialBT.println("MANUAL_STOP");
        Serial.println("Manual stop");
        // Flip Flag
        limitSwitchTriggered = false;
        return;
      }
      // If we are going away from home and are in range of the limit switch and it is triggered (unpressing bounce),
      // re-enable the motor and keep going
      else if (limitSwitchTriggered && direction == 1){
        digitalWrite(ENABLE_OUT, LOW);
        limitSwitchTriggered = false;
      }
      // Do one full cycle
      digitalWrite(SIGNAL_OUT, HIGH);
      delayMicroseconds(halfPeriodDelta*(Na - i - 1));
      digitalWrite(SIGNAL_OUT, LOW);
      delayMicroseconds(halfPeriodDelta*(Na - i - 1));
      Serial.printf("Step: %d\tHalf Period: %d\n", i, halfPeriodDelta*(Na - i - 1));
    }



    // Disable the motor
    digitalWrite(ENABLE_OUT, HIGH);
    // Send completion message
    SerialBT.println("DONE_MOTION");
    Serial.println("Done Motion.");
  }
  
  // else{
  //   // Calculate the half period in microseconds
  //   int halfPeriod = 500000 / frequency;

  //   // Enable the motor
  //   digitalWrite(ENABLE_OUT, LOW);
  //   delay(10);

  //   // Write the direction to the motor
  //   digitalWrite(DIRECTION_OUT, direction);

  //   // Send pulses to the motor (one pulse per step)
  //   for (int i = 0; i < steps; i++){
  //     // If we are going towards home and limit switch is triggered, 
  //     // turn off motor and say the limit switch is triggered
  //     if ((limitSwitchTriggered && direction == 0)){
  //       // Turn off motor immediately
  //       // digitalWrite(ENABLE_OUT, HIGH);
  //       // Send signals
  //       SerialBT.println("LIMIT_STOP");
  //       Serial.println("Limit stop");
  //       // Flip Flag
  //       limitSwitchTriggered = false;
  //       return;
  //     }
  //     // If we are going away from home and are out of the range of the limit switch and the limit switch is triggered,
  //     // turn off motor and say we manually stopped
  //     else if (limitSwitchTriggered && direction == 1 &&  i > 15){
  //       // Turn off motor immediately
  //       // digitalWrite(ENABLE_OUT, HIGH);
  //       // Send signals
  //       SerialBT.println("MANUAL_STOP");
  //       Serial.println("Manual stop");
  //       // Flip Flag
  //       limitSwitchTriggered = false;
  //       return;
  //     }
  //     // If we are going away from home and are in range of the limit switch and it is triggered (unpressing bounce),
  //     // re-enable the motor and keep going
  //     else if (limitSwitchTriggered && direction == 1){
  //       digitalWrite(ENABLE_OUT, LOW);
  //       limitSwitchTriggered = false;
  //     }
  //     // Do one full cycle
  //     digitalWrite(SIGNAL_OUT, HIGH);
  //     delayMicroseconds(halfPeriod);
  //     digitalWrite(SIGNAL_OUT, LOW);
  //     delayMicroseconds(halfPeriod);
  //   }

  //   // Disable the motor
  //   // digitalWrite(ENABLE_OUT, HIGH);
  //   // Send completion message
  //   SerialBT.println("DONE_MOTION");
  //   Serial.println("Done Motion.");
  // }
}

// ISR on the limit switch
void IRAM_ATTR onLimitSwitchPress(){
  // Flag for void loop
  limitSwitchTriggered = true;
}