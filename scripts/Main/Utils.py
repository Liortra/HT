# D:\PycharmProjects\HT\scripts;D:\PycharmProjects\HT\scripts\API;
# D:\PycharmProjects\HT\scripts\Arduino;
# D:\PycharmProjects\HT\scripts\Main;
# D:\PycharmProjects\HT\scripts\x64;
# D:\PycharmProjects\HT\scripts\x86;

import cv2  # https://docs.opencv.org/master/d6/d00/tutorial_py_root.html
from datetime import datetime
import os.path

# const
startTestTime = 1
heatingTime = 20
testTime = 60
steadyStateTime = 3
decayPointFFC = heatingTime + steadyStateTime
stopTestFFC = testTime - steadyStateTime


def find_camera():  # TODO fix find_camera
    # for i in reversed(range(10)):
    # for i in range(1, 10):
    #     print("Testing for presence of camera #{0}...".format(i))
    for i in reversed(range(10)):  # TODO from 0 and check
        cv2_cap = cv2.VideoCapture(i)
        # print("Testing for presence of camera #{0}...".format(i))
        if cv2_cap.isOpened():
            cv2_cap.release()
            cv2.destroyAllWindows()
            return i

    if not cv2_cap.isOpened():
        print("Camera not found!")
        exit(1)


def build_files():
    # this section creates the date object
    dateTimeObj = datetime.now()
    startTestTimeStamp = dateTimeObj.strftime("%d%m%Y%H%M%S")  # time format = DDMMYYYYHHMMSS
    # path to scripts/HTBio_files
    basePath = os.path.dirname(__file__)
    nameFile = startTestTimeStamp + '.HTBio'
    nameVideo = startTestTimeStamp + '.mp4'
    # nameVideo = startTestTimeStamp + '.avi'
    # Setting for saving the SMI videoWriter
    videoName = os.path.abspath(os.path.join(basePath, "..", "HTBio_files/", nameVideo))
    videoWriterFourcc = cv2.VideoWriter_fourcc(*'mp4v')  # http://www.fourcc.org/codecs.php - list of available codes
    # videoWriterFourcc = cv2.VideoWriter_fourcc(*'XVID')
    # videoWriter = cv2.VideoWriter(videoName, videoWriterFourcc, 30.0, (1920, 1080))
    videoWriter = cv2.VideoWriter(videoName, videoWriterFourcc, 60, (640, 480))
    # (const String &filename, int fourcc, double fps, Size frameSize, bool isColor=true)
    # fps - const for utils and update
    # TODO check resolution  - f
    # Setting for saving HTBio HTBioFile from Lepton cam
    filename = os.path.abspath(os.path.join(basePath, "..", "HTBio_files/", nameFile))
    HTBioFile = open(filename, 'wb+')  # TODO send the name HTBioName for creator
    return HTBioFile, videoWriter, startTestTimeStamp
