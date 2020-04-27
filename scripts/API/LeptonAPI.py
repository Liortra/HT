from scripts.API.import_clr import *

clr.AddReference("ManagedIR16Filters")

from IR16Filters import IR16Capture, NewBytesFrameEvent
import numpy
import struct

# init and const
numpyArr = None
tempList = []
countTemp = 0  # counter for higher temps
heatTemp = 4100 + 27315  # the heat temperature
# sec = 30  # time delay
highTemp = False
# header
version_id = 2  # 1 byte
patient_id = 11  # 4 byte
test_id = 111  # 4 byte
frame_width = 160  # 4 byte
frame_height = 120  # 4 byte
# number_of_frames = 100  # 4 byte
decay_point = 5  # 4 byte
heating_point = 2  # 4 byte


# frame callback function
# this will be called every time a new frame comes in from the camera
# method from the DLL
def getFrameRaw(arr, width, height):
    global numpyArr
    numpyArr = numpy.fromiter(arr, dtype="uint16").reshape(height, width)
    tempList.append(numpyArr)
    # if numpyArr is not None and highTemp:
    #     checkTemp(numpyArr)


def initCam():
    global capture
    # Build an IR16 capture device
    capture = IR16Capture()
    capture.SetupGraphWithBytesCallback(NewBytesFrameEvent(getFrameRaw))
    print("init")


# https://docs.python.org/3.4/library/struct.html#format-strings
def buildHeader(fout, dateX):
    fout.write(struct.pack('B', version_id))
    fout.write(struct.pack('i', patient_id))
    fout.write(struct.pack('i', test_id))
    fout.write(struct.pack('14B', *dateX))
    fout.write(struct.pack('i', frame_width))
    fout.write(struct.pack('i', frame_height))
    fout.write(struct.pack('i', len(tempList)))
    fout.write(struct.pack('i', decay_point))
    fout.write(struct.pack('i', heating_point))


def checkTemp(numpyArr):
    global countTemp
    heat = len(numpy.where(numpyArr > heatTemp))
    countTemp += heat


def startLepton():
    # global startCal
    # need restart after stop button
    capture.RunGraph()
    print("start")
    # highTemp = True


def stopLepton(file, now):
    # highTemp = False
    dateX = now.encode(encoding='ascii', errors='strict')
    print("stop")
    capture.StopGraph()
    capture.Dispose()
    buildHeader(file, dateX)
    # print(len(tempList))
    for index, item in enumerate(tempList):
        file.write(struct.pack('i', index))  # index of frame in 4 byte
        item = item - 27315
        for x in range(0, item.shape[0]):
            for y in range(0, item.shape[1]):
                file.write(struct.pack('h', item[x, y]))
    file.close()
    # print("counter high temp is: " + str(countTemp))
