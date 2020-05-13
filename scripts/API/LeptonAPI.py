from API.ImportClr import *

clr.AddReference("ManagedIR16Filters")

from Lepton import CCI
from IR16Filters import IR16Capture, NewBytesFrameEvent
import numpy
import struct

# init and const
numpyArr = None
listTemp = []
countTempPass = 0  # counter for higher temps
# heatTemp = 4100 + 27315  # the heat temperature
# highTemp = False
# header
versionId = 2  # 1 byte
patientId = 11  # 4 byte
testId = 111  # 4 byte
frameWidth = 160  # 4 byte
frameHeight = 120  # 4 byte

lep, = (dev.Open()
        for dev in CCI.GetDevices())


# frame callback function
# this will be called every time a new frame comes in from the camera
# method from the DLL
def getFrameRaw(arr, width, height):
    global numpyArr
    numpyArr = numpy.fromiter(arr, dtype="uint16").reshape(height, width)
    listTemp.append(numpyArr)
    print(numpyArr)


def init_cam():
    global capture
    # Build an IR16 capture device
    # methods from the DLL
    capture = IR16Capture()
    capture.SetupGraphWithBytesCallback(NewBytesFrameEvent(getFrameRaw))
    lep.rad.SetTLinearEnableStateChecked(False)  # represents temperature in Kelvin(True) or Celsius(False)
    # print("init")


# https://docs.python.org/3.4/library/struct.html#format-strings
def build_header(HTBioFile, dateX):
    HTBioFile.write(struct.pack('B', versionId))
    HTBioFile.write(struct.pack('i', patientId))
    HTBioFile.write(struct.pack('i', testId))
    HTBioFile.write(struct.pack('14B', *dateX))
    HTBioFile.write(struct.pack('i', frameWidth))
    HTBioFile.write(struct.pack('i', frameHeight))
    HTBioFile.write(struct.pack('i', len(listTemp)))
    HTBioFile.write(struct.pack('i', decayPoint))
    HTBioFile.write(struct.pack('i', heatingPoint))


# def check_temp(numpyArr):
#     global countTempPass
#     heat = len(numpy.where(numpyArr > heatTemp))
#     countTempPass += heat


def start_lepton():
    capture.RunGraph()  # Lepton cam start record
    print("start")


def lepton_normalization():
    lep.sys.RunFFCNormalization()
    print("FFC")


def mark_decay_point():
    global decayPoint  # 4 byte # the frame i stop heating
    decayPoint = len(listTemp) - 1


def mark_heating_point():
    global heatingPoint  # 4 byte # thr frame i started heating
    heatingPoint = len(listTemp) - 1


def stop_lepton(HTBioFile, startTestTimeStamp):
    dateX = startTestTimeStamp.encode(encoding='ascii', errors='strict')
    print("stop")
    capture.StopGraph()  # method from the DLL
    build_header(HTBioFile, dateX)
    for index, item in enumerate(listTemp):
        HTBioFile.write(struct.pack('i', index))  # index of frame in 4 byte
        # item = item - 27315
        for x in range(0, item.shape[0]):
            for y in range(0, item.shape[1]):
                HTBioFile.write(struct.pack('h', item[x, y]))
    HTBioFile.close()
    listTemp.clear()


def close_lepton():
    capture.Dispose()  # method from the DLL
