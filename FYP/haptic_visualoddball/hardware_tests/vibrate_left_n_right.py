import serial
import time

ser = serial.Serial('COM9', 9600) 
motorPin = 9
pwmValue = 0

ser.write(bytes('pinMode '+ str(motorPin) + ' OUTPUT\n', 'utf-8'))
start_time = time.time()
print("Vibrate")

while time.time() - start_time < 10:

    ser.write(bytes('analogWrite '+ str(motorPin) + ' ' + str(pwmValue) + '\n', 'utf-8'))
    ser.write(b'digitalWrite 13 HIGH\n')
    time.sleep(0.5)
    pwmValue += 128
    if pwmValue > 255:
        pwmValue = 0

print("Done")
ser.write(bytes('analogWrite '+ str(motorPin) + ' 0\n', 'utf-8'))
ser.write(b'digitalWrite 13 LOW\n')
ser.close()











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

