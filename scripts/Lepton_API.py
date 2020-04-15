from import_clr import *
clr.AddReference("ManagedIR16Filters")
from IR16Filters import IR16Capture, NewBytesFrameEvent
import numpy
import time

# frame callback function
# this will be called everytime a new frame comes in from the camera
numpyArr = None
tempDict = {}


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

try:
    for i in range(10000):
        print()
        for i, r in enumerate(numpyArr):
            for j, c in enumerate(r):
                numpyArr[i, j] = numpyArr[i, j] / 100 - 273
        print(numpyArr)
        tempDict[i] = numpyArr
    print("========================1")
    print("========================2")
    print(numpyArr[60][60])
    print(len(tempDict))
    print(len(tempDict[0]))
finally:
    capture.StopGraph()
    capture.Dispose()
