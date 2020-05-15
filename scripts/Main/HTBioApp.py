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
import threading
import sys

Config.set('graphics', 'fullscreen', 'fake')  # disable the X button
Config.set('input', 'mouse', 'mouse,multitouch_on_demand')  # disable right click red dot
sys.path.append('..')
from Main import Utils

# init and const
Builder.load_file('htbio.kv')
cameraID1 = Utils.find_camera()  # find the port of the camera


class ICTCamera(Image):
    def __init__(self, parent, capture, **kwargs):
        super(ICTCamera, self).__init__(**kwargs)
        self.capture = capture  # data to read
        self.parent = parent  # this object's parent (= box layout) - change the logo to the camera
        self.isRecording = False  # start recording video from SMI
        self.opticVideoWriter = None  # init for video writer
        self.decayFrame = []

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
            self.frame.shape
            if self.isRecording:  # push on start button
                self.opticVideoWriter.write(self.frame)  # make mp4 video
            # convert it to texture & display image from the texture
            self.parent.ids['imageCamera'].texture = self.get_texture_from_frame(self.frame, 0)

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

    def save_decay_point_frame(self,photoWriter):
        cv2.imwrite(photoWriter,self.frame)
        # self.decayFrame.append(self.frame)


class CameraScreen(Screen):
    # initialize the "Camera"
    isTurnOn = False
    isHeated = False
    isRecording = False

    # init and close the system
    def init_camera(self, imageCamera, buttonTurnOn, buttonStart, buttonBack, buttonHeat):
        from API import LeptonAPI
        from Arduino import LedController
        if not self.isTurnOn:  # Setup for the system
            self.capture = cv2.VideoCapture(cameraID1)  # capture ICT cam
            self.ICTCamera = ICTCamera(self, self.capture)  # change the window from logo to camera
            self.ICTCamera.start()
            # Set as started
            self.isTurnOn = True
            buttonTurnOn.text = 'Turn Off'
            # when started, let start enabled
            buttonStart.disabled = False  # Enable the Start (button)
            buttonBack.disabled = True  # Prevent the back (button)
            LeptonAPI.init_cam()  # init Lepton cam
            buttonHeat.disabled = False  # enabled
            LedController.init_led()  # start the Arduino
        else:  # press on TurnOff = teardown for the system
            self.isTurnOn = False  # stop what was "started"
            buttonTurnOn.text = 'Turn ON'
            # Reset camera to home image
            self.ICTCamera.stop()
            self.ICTCamera = Image(source='logo.jpg')
            imageCamera.source = self.ICTCamera.source  # get back to the logo
            imageCamera.reload()  # get back to the logo
            buttonStart.disabled = True  # Prevent the Start (button)
            buttonBack.disabled = False  # Enabled the back (button)
            buttonHeat.text = 'Heat'
            buttonHeat.disabled = True  # Prevent the Heat (button)
            self.isHeated = False
            self.capture.release()  # Release the capture
            LeptonAPI.close_lepton()  # closing Lepton cam
            LedController.close_led()  # closing Led

    # Start recording or stop recording
    def start_streaming(self, buttonTurnOn, buttonStart, buttonHeat):
        # from API import LeptonAPI
        # from Arduino import LedController
        if not self.isRecording:  # Was running at click
            print("Running test")
            self.isRecording = True
            buttonTurnOn.disabled = True  # Disable the TurnOff (button)
            buttonStart.text = 'Stop'
            buttonHeat.text = 'Cool'
            self.isHeated = True
            self.fileWriter, videoWriter, self.photoWriter ,self.startTestTimeStamp = Utils.build_files(self.capture)
            self.ICTCamera.init_record_writer(videoWriter)
            self.ICTCamera.start_stop_record_video()  # start film a video
            CameraScreen.run_test(self, self.fileWriter, self.photoWriter,self.startTestTimeStamp, buttonTurnOn, buttonStart, buttonHeat)
        else:
            self.ICTCamera.start_stop_record_video()
            self.isRecording = False
            buttonTurnOn.disabled = False  # Enable the TurnOff (button)
            buttonStart.text = 'Start'
            buttonHeat.text = 'Heat'
            self.isHeated = False
            print("Test end")
            # LeptonAPI.mark_decay_point()
            # LeptonAPI.stop_lepton(self.fileWriter, self.startTestTimeStamp)  # stop lepton film
            # LedController.stop_led()  # stop the Arduino

    def run_test(self, fileWriter, photoWriter, startTestTimeStamp, buttonTurnOn, buttonStart, buttonHeat):
        from API import LeptonAPI
        from Arduino import LedController
        # lambda dt: if you want to schedule a function that does not accept the dt argument
        Clock.schedule_once(lambda dt: LeptonAPI.start_lepton(), Utils.startTestTime)
        Clock.schedule_once(lambda dt: LeptonAPI.lepton_normalization(), Utils.startTestTime + 1)
        Clock.schedule_once(lambda dt: LedController.start_led(), Utils.steadyStateTime)
        Clock.schedule_once(lambda dt: LeptonAPI.mark_heating_point(), Utils.steadyStateTime)
        Clock.schedule_once(lambda dt: LeptonAPI.lepton_normalization(), Utils.heatingTime)
        Clock.schedule_once(lambda dt: LedController.stop_led(), Utils.decayPointFFC)
        Clock.schedule_once(lambda dt: LeptonAPI.mark_decay_point(), Utils.decayPointFFC)
        Clock.schedule_once(lambda dt: self.ICTCamera.save_decay_point_frame(photoWriter), Utils.savePhotoTime)
        Clock.schedule_once(lambda dt: LeptonAPI.lepton_normalization(), Utils.stopTestFFC)
        Clock.schedule_once(lambda dt: LeptonAPI.stop_lepton(fileWriter, startTestTimeStamp), Utils.stopTestFFC)
        Clock.schedule_once(lambda dt: CameraScreen.start_streaming(self, buttonTurnOn, buttonStart, buttonHeat),
                            Utils.stopTestFFC)

    def on_off_heat(self, buttonHeat):  #
        from Arduino import LedController
        # from API import LeptonAPI
        if not self.isHeated:
            LedController.start_led()  # start the Arduino
            # LeptonAPI.mark_heating_point()
            self.isHeated = True
            buttonHeat.text = 'Cool'
        else:
            LedController.stop_led()  # stop the Arduino
            # LeptonAPI.mark_decay_point()
            self.isHeated = False
            buttonHeat.text = 'Heat'

    def close_camera(self):  # it's here for future function
        print("Closing System")


class MainScreen(Screen):
    def exit_app(self):
        App.get_running_app().stop()


class MainApp(App):
    def build(self):
        screenManager = ScreenManager()
        screenManager.add_widget(MainScreen(name="main"))
        screenManager.add_widget(CameraScreen(name="camera"))
        return screenManager


# Start the MainApp
if __name__ == '__main__':
    MainApp().run()
