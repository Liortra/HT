"""
Assumptions:


"""

from kivy.config import Config
from kivy.app import App
from kivy.clock import Clock
from kivy.graphics.texture import Texture
from kivy.lang import Builder
from kivy.uix.image import Image
from kivy.uix.screenmanager import ScreenManager, Screen
import cv2
import time
import threading
import sys

# Configuration for the screen
Config.set('graphics', 'fullscreen', 'fake')  # disable the X button
Config.set('input', 'mouse', 'mouse,multitouch_on_demand')  # disable right click red dot
Config.set('graphics', 'width', 1280)  # change the width of the window
Config.set('graphics', 'height', 720)  # change the height of the window

sys.path.append('..')
from Utils.Utils import catch_exception
from Utils import Utils
from Utils import WindowsInhibitor

# init and const
osSleep = WindowsInhibitor.WindowsInhibitor()
osSleep.inhibit()  # prevent windows to sleep
Builder.load_file('htbio.kv')


class ICTCamera(Image):
    @catch_exception
    def __init__(self, parent, capture, **kwargs):
        super(ICTCamera, self).__init__(**kwargs)
        self.capture = capture  # data to read
        self.parent = parent  # this object's parent (= box layout) - change the logo to the camera
        self.isRecording = False  # start recording video from SMI
        self.opticVideoWriter = None  # init for video writer
        self.fps = capture.get(cv2.CAP_PROP_FPS)

        thread = threading.Thread(target=self.start, args=())
        thread.daemon = True  # Daemonize thread
        thread.start()

        # starts the "Camera", capturing at 30 fps by default

    def start(self, fps=30):  # TODO check fps
        Clock.schedule_interval(self.update, 1.0 / fps)  # Schedule an event to be called every <timeout> seconds.

    # run a video on screen
    def update(self, dt):  # TypeError: schedule_interval() takes exactly 2 positional arguments, dt - delta time
        ret, self.frame = self.capture.read()
        if ret:
            if self.isRecording:  # push on start button
                self.opticVideoWriter.write(self.frame)  # make mp4 video
            # convert it to texture & display image from the texture
            self.parent.ids['imageCamera'].texture = self.get_texture_from_frame(self.frame, 0)
        else:  # TODO if the camera is disconnected
            print("Cam disconnect")
            self.stop()
            CameraScreen.reconnect()

    def stop(self):
        Clock.unschedule(self.update)

    def get_texture_from_frame(self, frame, flipped):
        bufferFrame = cv2.flip(frame, flipped)
        bufferFrameStr = bufferFrame.tostring()
        imageTexture = Texture.create(size=(frame.shape[1], frame.shape[0]), colorfmt='bgr')
        imageTexture.blit_buffer(bufferFrameStr, colorfmt='bgr', bufferfmt='ubyte')
        return imageTexture

    def start_stop_record_video(self):
        if not self.isRecording:
            self.isRecording = not self.isRecording
        else:
            self.isRecording = not self.isRecording
            self.opticVideoWriter.release()

    def init_record_writer(self, opticVideoWriter):
        self.opticVideoWriter = opticVideoWriter
        print("init video")

    def save_decay_point_frame(self, photoWriter):
        cv2.imwrite(photoWriter, self.frame)


class CameraScreen(Screen):
    def __init__(self, **kw):
        # initialize the "Camera"
        super().__init__(**kw)
        self.isTurnOn = False
        self.isHeated = False
        self.isRecording = False
        self.init_camera()

    # init and close the system
    @catch_exception
    def init_camera(self):
        from API import LeptonAPI
        from Arduino import UnoController
        if not self.isTurnOn:  # Setup for the system
            cameraID1 = Utils.find_camera()  # find the port of the camera
            self.capture = cv2.VideoCapture(cameraID1)  # capture ICT cam
            self.capture.set(3, 1920)  # 1920X1080 / 2592X1944 / 1280X720 - default
            self.capture.set(4, 1080)
            self.ICTCamera = ICTCamera(self, self.capture)  # change the window from logo to camera
            self.ICTCamera.start()
            LeptonAPI.init_cam()  # init Lepton cam
            UnoController.init_led()  # start the Arduino
            # Set as started
            self.isTurnOn = True
            # TODO create listener to the button in the arduino (it's work with joystick button)
            # # sending the ids of the buttons to start_streaming from LedController
            # self.thread2 = threading.Thread(target=UnoController.start_button, args=(self, self.ids['buttonStart'],
            #                                                                          self.ids['buttonHeat'],
            #                                                                          self.ids['buttonExit']))
            # self.thread2.daemon = True  # Daemonize thread
            # self.thread2.start()
        else:  # press on Exit = teardown for the system
            UnoController.stop_led()  # Turn Off the led
            self.ICTCamera.stop()  # Stop the camera
            self.capture.release()  # Release the capture
            LeptonAPI.close_lepton()  # closing Lepton cam
            UnoController.close_led()  # closing Led
            self.isTurnOn = False  # stop what was "started"
            self.isHeated = False

    # Start recording or stop recording
    @catch_exception
    def start_streaming(self, buttonStart, buttonHeat, buttonExit):
        from Arduino import UnoController
        if not self.isRecording:  # Was running at click
            print("Running test")
            self.isRecording = True
            buttonExit.disabled = True  # Disable the Exit (button)
            buttonHeat.disabled = True  # Disable the Heat (button)
            buttonStart.text = 'Stop'
            self.fileWriter, videoWriter, self.photoWriter, self.startTestTimeStamp = Utils.build_files(self.capture)
            self.ICTCamera.init_record_writer(videoWriter)
            self.ICTCamera.start_stop_record_video()  # start film a video
            self.run_test(self.fileWriter, self.photoWriter, self.startTestTimeStamp,
                          buttonStart, buttonHeat, buttonExit)
        else:
            UnoController.stop_led()  # Turn Off the led
            self.ICTCamera.start_stop_record_video()
            CameraScreen.stop_test(self)  # cancel all run_test(for push stop manually)
            self.isRecording = False
            buttonExit.disabled = False  # Enable the Exit (button)
            buttonHeat.disabled = False  # Enable the Heat (button)
            buttonStart.text = 'Start'
            CameraScreen.end_test_beep()  # make beep in end of the test
            time.sleep(0.25)
            print("Test end")

    def run_test(self, fileWriter, photoWriter, startTestTimeStamp, buttonStart, buttonHeat, buttonExit):
        from API import LeptonAPI
        from Arduino import UnoController
        # lambda dt: if you want to schedule a function that does not accept the dt argument
        # by creating event the clock activate the method
        self.event1 = Clock.schedule_once(lambda dt: LeptonAPI.start_lepton(), 0)  # start record from letpon
        self.event2 = Clock.schedule_once(lambda dt: LeptonAPI.lepton_normalization(),
                                          Utils.FFCFirstTime)  # FFC before heating
        self.event3 = Clock.schedule_once(lambda dt: UnoController.start_led(), Utils.steadyStateTime)  # turnOn Led
        self.event4 = Clock.schedule_once(lambda dt: LeptonAPI.mark_heating_point(),
                                          Utils.steadyStateTime)  # mark heating point
        self.event5 = Clock.schedule_once(lambda dt: LeptonAPI.lepton_normalization(),
                                          Utils.FFCSecondTime)  # FFC after FFCSecondTime seconds after turnOn Led
        self.event6 = Clock.schedule_once(lambda dt: LeptonAPI.lepton_normalization(),
                                          Utils.FFCThirdTime)  # FFC before turnOff Led
        self.event7 = Clock.schedule_once(lambda dt: UnoController.stop_led(), Utils.decayPoint)  # turnOff Led
        self.event8 = Clock.schedule_once(lambda dt: LeptonAPI.mark_decay_point(), Utils.decayPoint)  # mark decay point
        self.event9 = Clock.schedule_once(lambda dt: self.ICTCamera.save_decay_point_frame(photoWriter),
                                          Utils.savePhotoTime)  # save image 1 second after turnOff Led
        self.event10 = Clock.schedule_once(lambda dt: LeptonAPI.lepton_normalization(),
                                           Utils.stopTestFFC)  # FFC before stop test
        self.event11 = Clock.schedule_once(lambda dt: LeptonAPI.stop_lepton(fileWriter, startTestTimeStamp),
                                           Utils.testTime)  # stop record from letpon and save HTBIO file
        self.event12 = Clock.schedule_once(lambda dt: CameraScreen.start_streaming(self, buttonStart, buttonHeat,
                                                                                   buttonExit), Utils.testTime)
        # event 12 = CameraScreen.start_streaming - stop test after testTime seconds

    def stop_test(self):  # Cancel all events if i push the button
        self.event1.cancel()
        self.event2.cancel()
        self.event3.cancel()
        self.event4.cancel()
        self.event5.cancel()
        self.event6.cancel()
        self.event7.cancel()
        self.event8.cancel()
        self.event9.cancel()
        self.event10.cancel()
        self.event11.cancel()
        self.event12.cancel()

    def on_off_heat(self, buttonStart, buttonHeat):
        from Arduino import UnoController
        if not self.isHeated:
            buttonStart.disabled = True  # Disable the Start (button)
            UnoController.start_led()  # Turn On the led
            self.isHeated = True
            buttonHeat.text = 'Cool'
        else:
            buttonStart.disabled = False  # Enable the Start (button)
            UnoController.stop_led()  # Turn Off the led
            self.isHeated = False
            buttonHeat.text = 'Heat'

    @staticmethod
    def reconnect():  # TODO need to boot the connect of the camera
        print("disconnect")
        # CameraScreen.init_camera()
        print("reconnect")
        # CameraScreen.init_camera()

    @staticmethod
    def end_test_beep():
        import winsound
        duration = 1000  # milliseconds
        freq = 800  # Hz
        winsound.Beep(freq, duration)

    def close_camera(self):
        print("Closing System")
        self.init_camera()  # teardown of the system
        osSleep.uninhibit()  # enable sleep mode
        App.get_running_app().stop()  # closing the GUI


class MainApp(App):
    @catch_exception
    def build(self):
        screenManager = ScreenManager()  # by this we can add more screens in the future
        screenManager.add_widget(CameraScreen(name="camera"))
        return screenManager


# Start the MainApp
if __name__ == '__main__':
    MainApp().run()
