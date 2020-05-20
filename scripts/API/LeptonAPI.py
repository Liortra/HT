from API.ImportClr import *

clr.AddReference("ManagedIR16Filters")

from Lepton import CCI
from IR16Filters import IR16Capture, NewBytesFrameEvent
import numpy
import HTBioCreator

# init and const
numpyArr = None
listTemp = []
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


def init_cam():
    global capture
    # Build an IR16 capture device
    # methods from the DLL
    capture = IR16Capture()
    capture.SetupGraphWithBytesCallback(NewBytesFrameEvent(getFrameRaw))
    # lep.rad.SetTLinearEnableStateChecked(True)  # represents temperature in Kelvin(True) or Celsius(False)
    # lep.sys.SetGainMode(CCI.Sys.GainMode.LOW)
    print("init")


def start_lepton():
    lep.rad.SetTLinearEnableStateChecked(True)  # represents temperature in Kelvin(True) or Celsius(False)
    lep.sys.SetGainMode(CCI.Sys.GainMode.LOW)
    capture.RunGraph()  # Lepton cam start record
    print("start")


def lepton_normalization():
    lep.sys.RunFFCNormalization()
    print("FFC")


def mark_decay_point():
    global decayPoint  # 4 byte # the frame i stop heating
    decayPoint = len(listTemp) - 1


def mark_heating_point():
    global heatingPoint  # 4 byte # the frame i start heating
    heatingPoint = len(listTemp) - 1


def stop_lepton(HTBioFile, startTestTimeStamp):
    dateX = startTestTimeStamp.encode(encoding='ascii', errors='strict')
    print("stop")
    capture.StopGraph()  # method from the DLL
    HTBioCreator.run(HTBioFile, listTemp, versionId, patientId, testId, dateX, frameWidth,
                     frameHeight, decayPoint, heatingPoint)
    listTemp.clear()
    print("clean")
    # TODO try catch if i stop the test in middle of it


def close_lepton():
    capture.Dispose()  # method from the DLL
