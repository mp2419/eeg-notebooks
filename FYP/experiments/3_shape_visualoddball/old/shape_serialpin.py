import serial
import time

def change_shape(direction):
    # - connect to Arduino -
    ser = serial.Serial('COM9', 9600,  timeout=10)
    start_time = time.time()
    print("Move ", direction)

    start_time = time.time()
    while time.time() - start_time < 1:
        if direction == "left":
            ser.write(b'1 Left\n')
        elif direction == "right":
            ser.write(b'2 Right\n')

    time.sleep(1) 
    bytesToRead = ser.inWaiting()
    data=ser.read(bytesToRead)
    print(data)
    ser.write(b'0\n')
    time.sleep(1) 
    
    # - STOP -
    bytesToRead = ser.inWaiting()
    ser.read(bytesToRead)
    print(data)
    print("Done")
    ser.close()

# - Test -python 
while(True):
    change_shape("right")
    time.sleep(2)
    change_shape("left")

