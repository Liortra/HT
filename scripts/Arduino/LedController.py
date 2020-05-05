from serial import Serial  # you need to install the pySerial :pyserial.sourceforge.net
import time


# TODO check sleep to delete
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


# TODO need to check the time and if i need to use it
def init_led():
    global arduino
    # your Serial port should be different!
    arduino = Serial('COM3', 9600)
    time.sleep(3)  # waiting the initialization...


def start_led():
    on_off_function("on")


def stop_led():
    on_off_function("off")


def close_led():
    on_off_function("bye")