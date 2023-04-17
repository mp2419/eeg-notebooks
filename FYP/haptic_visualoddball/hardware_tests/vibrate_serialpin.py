import serial
import time

def vibrate(direction):
    # set up the serial connection
    ser = serial.Serial('COM9', 9600)

    if direction == "left":
        # send a command to enable PWM output on pin 9
        ser.write(b'9\n')
        print("left")
    elif direction == "right":
        # send a command to enable PWM output on pin 5
        ser.write(b'5\n')
        print("right")

    response = ser.readline().decode().strip()
    print(response)

    time.sleep(5)

    # send a command to disable PWM output
    ser.write(b'1\n')
    response = ser.readline().decode().strip()
    print(response)

    # close the serial connection
    ser.close()

vibrate("left")
time.sleep(2)
vibrate("right")


