from serial import Serial  # you need to install the pySerial :pyserial.sourceforge.net
import sys


sys.path.append('..')
from Utils.Utils import catch_exception
# import time
# from Main import HTBioApp


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


@catch_exception
def init_led():
    global arduino
    # your Serial port should be different!
    arduino = Serial('COM3', 9600)
    # arduino = Serial('COM4', 9600)


def start_led():
    on_off_function("on")


def stop_led():
    on_off_function("off")


def close_led():
    on_off_function("bye")

# TODO combine button to start_streaming (work with joystick button)
# def start_button(self, buttonStart, buttonHeat, buttonExit):
#     while True:
#         command = arduino.read().decode('utf-8')
#         if command:
#             # flush serial for unprocessed data
#             arduino.flushInput()
#             if str(command) == '0':
#                 print("Playing test")
#                 HTBioApp.CameraScreen.start_streaming(self, buttonStart, buttonHeat, buttonExit)
