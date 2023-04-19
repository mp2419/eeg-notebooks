import serial
import time

def vibrate(direction):
    # - connect to Arduino -
    ser = serial.Serial('COM9', 9600,  timeout=10)
    start_time = time.time()
    print("Vibrate ", direction)

    # - RUN -
    while time.time() - start_time < 5:
        if direction == "left":
            ser.write(b'9\n')
        elif direction == "right":
            ser.write(b'5\n')
        # bytesToRead = ser.inWaiting()
        # data=ser.read(bytesToRead)
        # print(data, " Vibrate")
        time.sleep(0.5)

    # - STOP -
    while time.time() - (start_time) < 7:
        ser.write(b'1\n')
        # bytesToRead = ser.inWaiting()
        # ser.read(bytesToRead)
        # print(data, " Done")
    ser.close()

# - Test -
# vibrate("left")
# time.sleep(2)
# vibrate("right")

