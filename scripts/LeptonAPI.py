from import_clr import *

clr.AddReference("ManagedIR16Filters")

from IR16Filters import IR16Capture, NewBytesFrameEvent
import numpy
import time
from datetime import datetime
import struct

# init and const
numpyArr = None
tempList = []

version_id = 2  # 1 byte
patient_id = 11  # 4 byte
test_id = 111  # 4 byte
frame_width = 160  # 4 byte
frame_height = 120  # 4 byte
number_of_frames = 100  # 4 byte
decay_point = 5  # 4 byte
heating_point = 2  # 4 byte


# frame callback function
# this will be called every time a new frame comes in from the camera
# method from the DLL
def getFrameRaw(arr, width, height):
    global numpyArr
    numpyArr = numpy.fromiter(arr, dtype="uint16").reshape(height, width)
    tempList.append(numpyArr)


def initCam(file, now):
    global capture
    global dateX
    global fout
    dateX = now.encode(encoding='ascii', errors='strict')
    fout = file
    # Build an IR16 capture device
    capture = IR16Capture()
    capture.SetupGraphWithBytesCallback(NewBytesFrameEvent(getFrameRaw))


# https://docs.python.org/3.4/library/struct.html#format-strings
def buildHeader():
    fout.write(struct.pack('B', version_id))
    fout.write(struct.pack('i', patient_id))
    fout.write(struct.pack('i', test_id))
    fout.write(struct.pack('14B', *dateX))
    fout.write(struct.pack('i', frame_width))
    fout.write(struct.pack('i', frame_height))
    # fout.write(struct.pack('i', number_of_frames))
    fout.write(struct.pack('i', len(tempList)))
    fout.write(struct.pack('i', decay_point))
    fout.write(struct.pack('i', heating_point))


def startLepton():
    # Build an IR16 capture device
    # capture = IR16Capture()
    # capture.SetupGraphWithBytesCallback(NewBytesFrameEvent(getFrameRaw))
    capture.RunGraph()


# def stopLepton():
def stopLepton(start_time):
    capture.StopGraph()
    capture.Dispose()
    buildHeader()
    print(len(tempList))
    for index, item in enumerate(tempList):
        fout.write(struct.pack('i', index))  # index of frame in 4 byte
        item = item - 27315
        for x in range(0, item.shape[0]):
            for y in range(0, item.shape[1]):
                fout.write(struct.pack('h', item[x, y]))
    print("--- %s seconds ---" % (time.time() - start_time))


# dateTimeObj = datetime.now()
# now = dateTimeObj.strftime("%d%m%Y%H%M%S")  # ddMMyyyyHHmmss
# filename = 'HTBio_files/' + now + '.HTBio'
# file = open(filename, 'wb')
# start_time = time.time()
# initCam(file, now)
# startLepton()
# time.sleep(5)
# stopLepton(start_time)
