import cv2  # https://docs.opencv.org/master/d6/d00/tutorial_py_root.html
from datetime import datetime
import os.path
import functools

# const
FFCFirstTime = 1
steadyStateTime = 3
heatingTime = 12
testTime = 60
FFCSecondTime = steadyStateTime + 5
FFCThirdTime = heatingTime + steadyStateTime - 2
decayPoint = heatingTime + steadyStateTime
savePhotoTime = decayPoint + 1
stopTestFFC = testTime - steadyStateTime


def find_camera():
    # for i in range(0,5):  # 0 is laptop cam(personal laptop)
    for i in reversed(range(5)):
        cv2_cap = cv2.VideoCapture(i)
        if cv2_cap.isOpened():
            ret, frame = cv2_cap.read()
            if ret:
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
    fps = capture.get(cv2.CAP_PROP_FPS)
    videoWriter = cv2.VideoWriter(videoName, videoWriterFourcc, fps, (int(capture.get(3)), int(capture.get(4))))
    # (const String &filename, int fourcc, double fps, Size frameSize(width,height))
    # Setting for saving HTBio HTBioFile from Lepton cam
    filename = os.path.abspath(os.path.join(basePath, "..", "HTBio_files/", nameFile))
    HTBioFile = open(filename, 'wb+')
    return HTBioFile, videoWriter, photoName, startTestTimeStamp


# show from which func we got exception and what is the the exception
def catch_exception(f):
    @functools.wraps(f)
    def func(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except Exception as e:
            print('Caught an exception in', f.__name__)
            print(e)

    return func
