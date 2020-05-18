import threading
import struct


# https://docs.python.org/3.4/library/struct.html#format-strings
def build_header(HTBioFile, versionId, patientId, testId, dateX, frameWidth, frameHeight, nrFrames, decayPoint,
                 heatingPoint):
    HTBioFile.write(struct.pack('B', versionId))  # 1 byte
    HTBioFile.write(struct.pack('i', patientId))  # 4 byte
    HTBioFile.write(struct.pack('i', testId))  # 4 byte
    HTBioFile.write(struct.pack('14B', *dateX))
    HTBioFile.write(struct.pack('i', frameWidth))  # 4 byte
    HTBioFile.write(struct.pack('i', frameHeight))  # 4 byte
    HTBioFile.write(struct.pack('i', nrFrames))  # 4 byte
    HTBioFile.write(struct.pack('i', decayPoint))  # 4 byte
    HTBioFile.write(struct.pack('i', heatingPoint))  # 4 byte


# class HTBioCreator(object):
    # """ Threading example class
    # The run() method will be started and it will run in the background
    # until the application exits.
    # """
    #
    # def __init__(self, HTBioFile, listTemp, versionId, patientId, testId,
    #              dateX, frameWidth, frameHeight, decayPoint, heatingPoint):
    #     """ Constructor
    #     :type interval: int
    #     :param interval: Check interval, in seconds
    #     """
    #
    #     thread = threading.Thread(target=self.run, args=(HTBioFile, listTemp, versionId, patientId, testId,
    #                                                      dateX, frameWidth, frameHeight, decayPoint, heatingPoint))
    #     thread.daemon = True  # Daemonize thread
    #     thread.start()  # Start the execution

def run(HTBioFile, listTemp, versionId, patientId, testId,
        dateX, frameWidth, frameHeight, decayPoint, heatingPoint):
    build_header(HTBioFile, versionId, patientId, testId,
                 dateX, frameWidth, frameHeight, len(listTemp), decayPoint, heatingPoint)
    for index, item in enumerate(listTemp):
        HTBioFile.write(struct.pack('i', index))  # index of frame in 4 byte
        item = item - 27315
        for x in range(0, item.shape[0]):
            for y in range(0, item.shape[1]):
                HTBioFile.write(struct.pack('h', item[x, y]))  # 2 byte
    HTBioFile.close()
    print('HTBio file created successfully ', HTBioFile)
