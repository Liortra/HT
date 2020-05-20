from serial import Serial  # you need to install the pySerial :pyserial.sourceforge.net
import sys
sys.path.append('..')
# import time
from Main import HTBioApp


def on_off_function(command):
    if command == "on":
        print("The LED is on...")
        arduino.write(b'H')
    elif command == "off":
        print("The LED is off...")
        arduino.write(b'L')
    elif command == "bye":
        print("See You!...")
        arduino.close()
    else:
        print("Sorry..type another thing..!")


def init_led():
    global arduino
    # your Serial port should be different!
    arduino = Serial('COM3', 9600)
    # arduino = Serial('COM4', 9600)
    # time.sleep(3)  # waiting the initialization... (can delete this line)


def start_led():
    on_off_function("on")


def stop_led():
    on_off_function("off")


def close_led():
    on_off_function("bye")


def start_button(self, buttonStart, buttonHeat, buttonExit):
    while True:
        command = arduino.read().decode('utf-8')
        if command:
            # flush serial for unprocessed data
            arduino.flushInput()
            print("new command:", command)
            if str(command) == '1':
                print("Playing test")
                break
    print("stop loop")
    HTBioApp.CameraScreen.start_streaming(self, buttonStart, buttonHeat, buttonExit)