import serial
import time

def change_shape(direction):
    # - connect to Arduino -
    ser = serial.Serial('COM9', 9600,  timeout=10)
    start_time = time.time()
    print("Move ", direction)

    start_time = time.time()
    while time.time() - start_time < 2:
        if direction == "left":
            ser.write(b'1\n')
        elif direction == "right":
            ser.write(b'2\n')

        bytesToRead = ser.inWaiting()
        data=ser.read(bytesToRead)
        #print(data, " Translation")

    # - STOP -
    while time.time() - start_time < 4:
        ser.write(b'0\n')

        bytesToRead = ser.inWaiting()
        ser.read(bytesToRead)
        #print(data, " Done")
    ser.close()

# - Test -python 
change_shape("left")
time.sleep(2)
change_shape("right")

