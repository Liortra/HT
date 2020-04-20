from import_clr import *

clr.AddReference("ManagedIR16Filters")
from IR16Filters import IR16Capture, NewBytesFrameEvent

import numpy
import time
from datetime import datetime
import struct
import binascii

# init and const
numpyArr = None
tempDict = {}
filename = 'test.HTBio'
fout = open(filename, 'wb')

version_id = 1  # 1 byte
patient_id = 11  # 4 byte
test_id = 111  # 4 byte
# split time to array of int
timestampString = datetime.now()
print(timestampString)
dt_string = timestampString.strftime("%d/%m/%Y %H:%M:%S")
line = ''.join([i for i in dt_string if i.isdigit()])
line = [char for char in line]  # 1 byte
#
frame_width = 160  # 4 byte
frame_height = 120  # 4 byte
number_of_frames = 10  # 4 byte
decay_point = 2  # 4 byte
heating_point = 5  # 4 byte


# https://docs.python.org/3.4/library/struct.html#format-strings
def buildHeader():
    fout.write("HEADER".encode('ascii'))
    fout.write(binascii.hexlify(struct.pack('<b', version_id)))
    fout.write(binascii.hexlify(struct.pack('<i', patient_id)))
    fout.write(binascii.hexlify(struct.pack('<i', test_id)))
    # write the current time
    [fout.write(binascii.hexlify(struct.pack('<b', int(i)))) for i in line]
    #
    fout.write(binascii.hexlify(struct.pack('<i', frame_width)))
    fout.write(binascii.hexlify(struct.pack('<i', frame_height)))
    fout.write(binascii.hexlify(struct.pack('<i', number_of_frames)))
    fout.write(binascii.hexlify(struct.pack('<i', decay_point)))
    fout.write(binascii.hexlify(struct.pack('<i', heating_point)))

    # fout.close()


def printHeader():
    with open(filename, "rb") as f:
        byte = f.read(2)
        while byte:
            # Do stuff with byte.
            print(byte)
            byte = f.read(2)


# frame callback function
# this will be called every time a new frame comes in from the camera
# method from the DLL
def getFrameRaw(arr, width, height):
    global numpyArr
    numpyArr = numpy.fromiter(arr, dtype="uint16").reshape(height, width)


# Build an IR16 capture device
capture = IR16Capture()
capture.SetupGraphWithBytesCallback(NewBytesFrameEvent(getFrameRaw))
capture.RunGraph()

# time for the callback
while numpyArr is None:
    time.sleep(.1)


buildHeader()
printHeader()

try:
    for k in range(100):
        fout.write("FRAME".encode('ascii'))
        fout.write(binascii.hexlify(struct.pack('<i', k)))  # index of frame in 1 byte
        for x in range(0, numpyArr.shape[0]):
            for y in range(0, numpyArr.shape[1]):
                numpyArr[x, y] = numpyArr[x,y] - 27315
                print(numpyArr[x, y])
                fout.write(binascii.hexlify(struct.pack('<h', numpyArr[x, y])))
            tempDict[k] = numpyArr
    #     print("========================1")
    #     print(tempDict[k])
    # print("========================2")

finally:
    fout.close()
    capture.StopGraph()
    capture.Dispose()
