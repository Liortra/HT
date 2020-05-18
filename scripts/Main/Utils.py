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
normalizationTimeFirst = startTestTime + 1
heatingTime = 20
testTime = 60
steadyStateTime = 3
decayPointFFC = heatingTime + steadyStateTime
savePhotoTime = decayPointFFC + 1
stopTestFFC = testTime - steadyStateTime


def find_camera():
    # for i in range(1,10):  # 0 is laptop cam(personal laptop)
    for i in reversed(range(5)):
        cv2_cap = cv2.VideoCapture(i)
        if cv2_cap.isOpened():
            cv2_cap.release()
            cv2.destroyAllWindows()
            return i

    if not cv2_cap.isOpened():
        print("Camera not found!")
        exit(1)


def build_files(capture):
    # this section creates the date object
    dateTimeObj = datetime.now()
    startTestTimeStamp = dateTimeObj.strftime("%d%m%Y%H%M%S")  # time format = DDMMYYYYHHMMSS
    # path to scripts/HTBio_files
    basePath = os.path.dirname(__file__)
    nameFile = startTestTimeStamp + '.HTBio'
    nameVideo = startTestTimeStamp + '.mp4'
    namePhoto = startTestTimeStamp + '.jpg'
    photoName = os.path.abspath(os.path.join(basePath, "..", "HTBio_files/", namePhoto))
    # Setting for saving the ICT videoWriter
    videoName = os.path.abspath(os.path.join(basePath, "..", "HTBio_files/", nameVideo))
    videoWriterFourcc = cv2.VideoWriter_fourcc(*'mp4v')  # http://www.fourcc.org/codecs.php - list of available codes
    # TODO change resolution  - f
    # print(int(capture.get(cv2.CAP_PROP_FRAME_WIDTH)))
    # print(int(capture.get(cv2.CAP_PROP_FRAME_HEIGHT)))
    fps = capture.get(cv2.CAP_PROP_FPS)
    videoWriter = cv2.VideoWriter(videoName, videoWriterFourcc, 1.0/fps, (int(capture.get(3)), int(capture.get(4))))
    # (const String &filename, int fourcc, double fps, Size frameSize(width,height))
    # int(capture.get(3) = 1280 & int(capture.get(4) = 720
    # Setting for saving HTBio HTBioFile from Lepton cam
    filename = os.path.abspath(os.path.join(basePath, "..", "HTBio_files/", nameFile))
    HTBioFile = open(filename, 'wb+')
    return HTBioFile, videoWriter, photoName, startTestTimeStamp
