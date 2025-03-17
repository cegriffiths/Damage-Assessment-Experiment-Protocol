#include <Arduino.h>

// Pin definitions
#define SIGNAL_OUT 12
#define DIRECTION_OUT 13
#define ENABLE_OUT 14
#define LIMIT_SWITCH_IN 15

#define STEPS_TO_DISTANCE 0.025 // mm/step

volatile bool limitSwitchTriggered = false;

// Function definitions
void moveStage(int, int, int, bool);
void parseCommand(String command);
void IRAM_ATTR onLimitSwitchPress();
bool checkSwitch(int, int);

// Initiate pins and serials
void setup() {
  pinMode(SIGNAL_OUT, OUTPUT);            //Signal to the motor
  pinMode(DIRECTION_OUT, OUTPUT);         //true (1) is towards end with motor, false (0) is towards end without motor
  pinMode(ENABLE_OUT, OUTPUT);            //Low is enabled, High is disabled
  pinMode(LIMIT_SWITCH_IN, INPUT_PULLUP); //Regularly high, low when pressed

  attachInterrupt(digitalPinToInterrupt(LIMIT_SWITCH_IN), onLimitSwitchPress, FALLING);

  Serial.begin(921600);
  Serial.print("Setup Finished");
  digitalWrite(ENABLE_OUT, LOW);
}

// Listening over serialBT for commands
void loop() {
  // Check if there is a message
  if (Serial.available()){
    // Serial.println("BT Command Recieved");
    String command = Serial.readStringUntil('\n');
    // Serial.printf("Command recieved: %s\n", command.c_str());

    parseCommand(command);
  }

  delay(10);
}

// Take inputs over bluetooth
// Currently assumes a string of the form "frequency,steps,direction"
void parseCommand(String command){
  // Find indices of commas
  int firstcomma = command.indexOf(',');
  int secondcomma = command.indexOf(',', firstcomma + 1);
  int thirdcomma = command.indexOf(',', secondcomma + 1);

  // Split command string into expected variables
  int distance = command.substring(0, firstcomma).toInt();
  int velocity = command.substring(firstcomma+1, secondcomma).toInt();
  int acceleration = command.substring(secondcomma+1, thirdcomma).toInt();
  bool direction = command.substring(thirdcomma + 1).toInt() == 1;

  Serial.printf("Command recieved: Distance: %d, Velocity: %d, Acceleration: %d, Direction: %d\n", distance, velocity, acceleration, direction);

  moveStage(distance, velocity, acceleration, direction);
}

// Moves linear stage
// Takes input a frequency, number of steps, and a direction
// Outputs a square wave to a specified pin with the given frequency and a number of periods equaling the number of steps
// Outputs a direction boolean to another specified pin
// Toggles an enable pin at the beginning and end of the function
void moveStage(int distance, int velocity, int acceleration, bool direction){
  // If going towards home and already home, to not move motor
  if (direction == 0 && digitalRead(LIMIT_SWITCH_IN) == LOW){
    // Send signal
    Serial.println("LIMIT_STOP");
  }
  else{
    // Define distances and derivative in terms of steps
    int total_steps = distance / STEPS_TO_DISTANCE;
    int vel_steps = velocity / STEPS_TO_DISTANCE;
    int accel_steps = acceleration / STEPS_TO_DISTANCE;

    // Find distances to travel while accelerating, decelerating or moving at constant speed
    int accel_steps_count = (vel_steps*vel_steps) / (2*accel_steps);
    int const_steps_count = total_steps - 2*accel_steps_count;

    // If it takes over half the distance to accelerate, just accelerate for half the distance then decelerate
    if (const_steps_count < 0){
      accel_steps_count = total_steps/2;
      const_steps_count = 0;
    }

    Serial.printf("Total Steps: %d, Accel Steps: %d\n", total_steps, accel_steps_count);

    // Stage State variables
    int step_delay = 0;

    // Enable the motor
    digitalWrite(ENABLE_OUT, LOW);
    delay(10);

    // Write the direction to the motor
    digitalWrite(DIRECTION_OUT, direction);

    // For loop for motion
    for(int step_count = 0; step_count < total_steps; step_count++){
      // Check if the stage should keep moving
      bool keepMoving = !checkSwitch(direction, step_count);

      // Check if stage should be accelerating
      if(step_count < accel_steps_count && keepMoving){
        step_delay = 1000000 / sqrt(2 * accel_steps * (step_count + 1));
        if(step_count == 0){
          Serial.println("Accelerating");
        }
      }
      // Check if stage should be at constant velocity
      else if(step_count < (accel_steps_count + const_steps_count) && keepMoving){
        step_delay = 1000000 / vel_steps;
        if(step_count == accel_steps_count){
          Serial.println("Constant Speed");
        }
      }
      // Check if stage should be decelerating
      else if(keepMoving){
        step_delay = 1000000 / sqrt(2 * accel_steps * (total_steps - step_count));
        // Serial.println("Decelerating");
        if(step_count == (accel_steps_count + const_steps_count)){
          Serial.println("Decelerating");
        }
      }
      // Check if stage should stop
      else if(!keepMoving){
        return;
      }
      
      // Do one full cycle
      digitalWrite(SIGNAL_OUT, HIGH);
      delayMicroseconds(step_delay/2);
      digitalWrite(SIGNAL_OUT, LOW);
      delayMicroseconds(step_delay/2);
    }

    // Disable the motor
    digitalWrite(ENABLE_OUT, HIGH);
    // Send completion message
    Serial.println("DONE_MOTION");
  }
}

// Check if the limit switch has been pressed and if the stage is in a place where it should stop motion
bool checkSwitch(int direction, int step_count){
  // If we are going towards home and limit switch is triggered, 
  // turn off motor and say the limit switch is triggered
  if ((limitSwitchTriggered && direction == 0)){
    // Turn off motor immediately
    digitalWrite(ENABLE_OUT, HIGH);
    // Send signals
    // SerialBT.println("LIMIT_STOP");
    Serial.println("LIMIT_STOP");
    // Flip Flag
    limitSwitchTriggered = false;
    return true;
  }
  // If we are going away from home and are out of the range of the limit switch and the limit switch is triggered,
  // turn off motor and say we manually stopped
  else if (limitSwitchTriggered && direction == 1 &&  step_count > 15){
    // Turn off motor immediately
    digitalWrite(ENABLE_OUT, HIGH);
    // Send signals
    // SerialBT.println("MANUAL_STOP");
    Serial.println("MANUAL_STOP");
    // Flip Flag
    limitSwitchTriggered = false;
    return true;
  }
  // If we are going away from home and are in range of the limit switch and it is triggered (unpressing bounce),
  // re-enable the motor and keep going
  else if (limitSwitchTriggered && direction == 1){
    digitalWrite(ENABLE_OUT, LOW);
    limitSwitchTriggered = false;
  }
  // Stage can keep going
  return false;
}


// ISR on the limit switch
void IRAM_ATTR onLimitSwitchPress(){
  // Flag for void loop
  limitSwitchTriggered = true;
}