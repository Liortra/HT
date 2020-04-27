from serial import Serial  # you need to install the pySerial :pyserial.sourceforge.net
import time

# your Serial port should be different!
arduino = Serial('COM3', 9600)


def onOffFunction(command):
    # command = raw_input("Type something..: (on/ off / bye )");
    if command == "on":
        print("The LED is on...")
        time.sleep(1)
        arduino.write(b'H')
    # onOffFunction()
    elif command == "off":
        print("The LED is off...")
        time.sleep(1)
        arduino.write(b'L')
    # onOffFunction()
    elif command == "bye":
        print("See You!...")
        time.sleep(1)
        arduino.close()
    else:
        print("Sorry..type another thing..!")
    # onOffFunction()


# need to check the time and if i need to use it
def initLed():
    time.sleep(5)  # waiting the initialization...


def startLed():
    onOffFunction("on")


def stopLed():
    onOffFunction("off")


def sleepLed():
    onOffFunction("bye")


def main():
    time.sleep(5)  # waiting the initialization...
    onOffFunction("off")
    time.sleep(2)
    onOffFunction("on")
    time.sleep(2)
    onOffFunction("off")
    time.sleep(2)
    onOffFunction("on")
    time.sleep(2)
    onOffFunction("off")
    time.sleep(2)
    onOffFunction("on")
    time.sleep(2)
    onOffFunction("off")
    time.sleep(2)
