#include <Servo.h> //import the servo library

Servo SERVO_X; //the servo that will rotate on the x axis
Servo SERVO_Y; //the servo that will rotate on the y axis

const int SERVO_X_PIN = 11; //the pin for the servo that rotates on the x axis
const int SERVO_Y_PIN = 10; //the pin for the servo that rotates on the y axis
const int SERVO_MIN_ROTATION = 0; //the minimum degree of rotation that the servos can handle
const int SERVO_MAX_ROTATION = 180; //the maximum degree of rotation that the servos can handle
const int SERVO_ROTATION_STEP = 3; //the amount the servos rotation will increase or decrease
const int SERVO_DIRECTION_ID_UP = '1'; //the integer that will be read through serial to tell the servo to rotate up
const int SERVO_DIRECTION_ID_DOWN = '2'; //the integer that will be read through serial to tell the servo to rotate down
const int SERVO_DIRECTION_ID_LEFT = '3'; //the integer that will be read through serial to tell the servo to rotate left
const int SERVO_DIRECTION_ID_RIGHT = '4'; //the integer that will be read through serial to tell the servo to rotate right
int XRotationServoPosition = SERVO_MAX_ROTATION / 2; //the angle that the yaw controlling (x axis) servo will be set to (defaults to the center)
int YRotationServoPosition = SERVO_MAX_ROTATION / 2; //the angle that the pitch contrilling (y axis) servo will be set to (defaults to the center)
int reading; //the reading that the serial will give

void setup() { //setup function
    Serial.begin(9600); //begin serial communication on 9600 baud
    while (!Serial) {;} //wait for serial communication to begin
    
    SERVO_X.attach(SERVO_X_PIN); //attach the yaw controller servo to the designated pin
    SERVO_Y.attach(SERVO_Y_PIN); //attach the pitch controller servo to the designated pin
    
    pinMode(LED_BUILTIN, OUTPUT); //set the pinmode for the builtin led
}

void loop() { //main loop function
    while (Serial.available() > 0) { //while there still is serial left to read then read it and adjust stuff
      
        digitalWrite(LED_BUILTIN, HIGH); //turn on the builtin led to show that there is serial being read
        
        reading = Serial.read(); //read the serial
        
        if (reading == SERVO_DIRECTION_ID_UP) { //if the reading matches the id of the up command then pitch the servo up
            YRotationServoPosition += SERVO_ROTATION_STEP;
        } else if (reading == SERVO_DIRECTION_ID_DOWN) { //if the reading matches the id of the down command then pitch the servo down
            YRotationServoPosition -= SERVO_ROTATION_STEP;
        } else if (reading == SERVO_DIRECTION_ID_LEFT) { //if the reading matches the id of the left command the yaw the servo left
            XRotationServoPosition -= SERVO_ROTATION_STEP;
        } else if (reading == SERVO_DIRECTION_ID_RIGHT) { //if the reading matches the id of the right command then yaw the servo right
            XRotationServoPosition += SERVO_ROTATION_STEP;
        }
        
        if (XRotationServoPosition > SERVO_MAX_ROTATION) { //if the yaw servo is over the max bounds then set it to the max rotation
            XRotationServoPosition = SERVO_MAX_ROTATION;
        } else if (XRotationServoPosition < SERVO_MIN_ROTATION) { //if the yaw servo is under the minimum bounds then set it to the minimum rotation
            XRotationServoPosition = SERVO_MIN_ROTATION;
        }

        if (YRotationServoPosition > SERVO_MAX_ROTATION) { //if the pitch servo is over the max bounds then set it to the max rotation
            YRotationServoPosition = SERVO_MAX_ROTATION;
        } else if (YRotationServoPosition < SERVO_MIN_ROTATION) { //if the pitch servo is under the minimum bounds then set it to the minimum rotation
            YRotationServoPosition = SERVO_MIN_ROTATION;
        }
        
        SERVO_X.write(XRotationServoPosition); //tell the servo to move to the position its supposed to be at
        SERVO_Y.write(YRotationServoPosition); //tell the servo to move to the position its supposed to be at
        
        delay(20);
    }
    digitalWrite(LED_BUILTIN, LOW); //turn off the builtin led to show that there is no serial being read
}
