import serial
import time

def vibrate(direction):
    ser = serial.Serial('COM9', 9600) 

    if (direction == 'left'):
        motorPin = 9
        motorPin_other = 5
        print(direction, motorPin)
    else:
        motorPin = 5
        motorPin_other = 9
        print(direction, motorPin)
    
    pwmValue = 0

    start_time = time.time()
    print("Vibrate", direction)
    ser.write(bytes('pinMode '+ str(motorPin) + ' OUTPUT\n', 'utf-8'))
    ser.write(bytes('pinMode '+ str(motorPin_other) + ' OUTPUT\n', 'utf-8'))

    while time.time() - start_time < 5:

        ser.write(bytes('analogWrite '+ str(motorPin) + ' ' + str(pwmValue) + '\n', 'utf-8'))
        ser.write(bytes('analogWrite '+ str(motorPin_other) + ' ' + str(pwmValue) + '\n', 'utf-8'))
        ser.write(b'digitalWrite 13 HIGH\n')
        time.sleep(0.5)
        pwmValue += 128
        if pwmValue > 255:
            print(motorPin)
            pwmValue = 0

    print("Done")
    ser.write(bytes('analogWrite '+ str(motorPin) + ' 0\n', 'utf-8'))
    ser.write(bytes('analogWrite '+ str(motorPin_other) + ' ' + str(pwmValue) + '\n', 'utf-8'))

    ser.write(b'digitalWrite 13 LOW\n')
    ser.close()

vibrate("left")
time.sleep(2)
vibrate("right")









# -----ARDUINO SCRIPT----

# int motorPin = 9; // PWM pin for the motor
# int pwmValue = 0; // starting PWM value (out of 255)
# int delayTime = 500; // delay time between changes (in milliseconds)

# void setup() {
#   pinMode(motorPin, OUTPUT); // set the motor pin as an output
#   pinMode(13, OUTPUT);
# }

# //vibrate for 0.5s then quite for 0.5
# //loop for 10s 

# void loop() {
#   if(millis() > 10000) {
#     analogWrite(motorPin, 0); // set the PWM value for the motor
#     digitalWrite(13, HIGH); 
#   }else{ 
#     digitalWrite(13, LOW);
#     analogWrite(motorPin, pwmValue); // set the PWM value for the motor
#     delay(delayTime); // wait for the specified delay time
    
#     pwmValue += 128; // increment the PWM value
#     if (pwmValue > 255) { // if we've reached the maximum PWM value
#       pwmValue = 0; // reset to the minimum PWM value
#     }
#   }

# }

