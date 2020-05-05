"""
Assumptions:


"""
import cv2
from kivy.app import App
from kivy.clock import Clock
from kivy.graphics.texture import Texture
from kivy.lang import Builder
from kivy.uix.image import Image
from kivy.uix.screenmanager import ScreenManager, Screen
import sys

sys.path.append("..")
print(sys.path)
from scripts.Main import Utils

# init and const
Builder.load_file('htbio.kv')
# cameraID1 = utils.find_camera()  # WARN 0 is from here - think what to do
cameraID1 = 1


class SMICamera(Image):
    def __init__(self, parent, capture, **kwargs):
        super(SMICamera, self).__init__(**kwargs)
        self.capture = capture  # data to read
        self.parent = parent  # this object's parent (= box layout) - change the logo to the camera
        self.isRecording = False  # start recording video from SMI
        self.opticVideoWriter = None  # init for video writer

    # starts the "Camera", capturing at 30 fps by default
    def start(self, fps=30):  # TODO check fps
        Clock.schedule_interval(self.update, 1.0 / fps)  # Schedule an event to be called every <timeout> seconds.

    # run a video on screen
    def update(self, dt):  # TypeError: schedule_interval() takes exactly 2 positional arguments
        ret, self.frame = self.capture.read()
        if ret:
            if self.isRecording:  # push on start button
                self.opticVideoWriter.write(self.frame)  # TODO if writing with this cam don't work save it in list
                # and then save
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
        self.isRecording = not self.isRecording

    def init_record_writer(self, opticVideoWriter):
        self.opticVideoWriter = opticVideoWriter


class CameraScreen(Screen):
    # initialize the "Camera"
    isTurnOn = False
    isHeated = False
    isRecording = False

    # init and close the system
    def init_camera(self, imageCamera, buttonTurnOn, buttonStart, buttonBack, buttonHeat):
        from scripts.API import LeptonAPI
        from scripts.Arduino import LedController
        if not self.isTurnOn:  # Setup for the system
            self.capture = cv2.VideoCapture(cameraID1)  # capture SMI cam
            self.SMICamera = SMICamera(self, self.capture)  # change the window from logo to camera
            self.SMICamera.start()
            # Set as started
            self.isTurnOn = True
            buttonTurnOn.text = 'Turn Off'
            # when started, let start enabled
            # buttonStop.disabled = False  # enabled
            buttonStart.disabled = False  # Enable the Start (button)
            buttonBack.disabled = True  # Prevent the back (button)
            LeptonAPI.init_cam()  # init Lepton cam
            buttonHeat.disabled = False  # enabled
            LedController.init_led()  # start the Arduino
        else:  # press on TurnOff = teardown for the system
            self.isTurnOn = False  # stop what was "started"
            buttonTurnOn.text = 'Turn ON'
            # Reset camera to home image
            self.SMICamera.stop()
            self.SMICamera = Image(source='logo.jpg')
            imageCamera.source = self.SMICamera.source  # get back to the logo
            imageCamera.reload()  # get back to the logo
            # buttonStop.disabled = True  # Prevent the Stop (button)
            buttonStart.disabled = True  # Prevent the Start (button)
            buttonBack.disabled = False  # Enabled the back (button)
            buttonHeat.text = 'Heat'
            buttonHeat.disabled = True  # Prevent the Heat (button)
            self.isHeated = False
            self.capture.release()  # Release the capture
            from scripts.Arduino import LedController
            from scripts.API import LeptonAPI
            LeptonAPI.close_lepton()  # closing Lepton cam
            LedController.close_led()  # closing Led

    # Start recording or stop recording
    def start_streaming(self, buttonTurnOn, buttonStart):  # TODO need to check how disable stop button & change name
        if not self.isRecording:  # Was running at click
            self.isRecording = True
            buttonTurnOn.disabled = True # Disable the TurnOff (button)
            buttonStart.text = 'Stop'
            self.fileWriter, videoWriter, self.startTestTimeStamp = Utils.build_files()
            self.SMICamera.init_record_writer(videoWriter)
            self.SMICamera.start_stop_record_video()  # start film a video
            from scripts.API import LeptonAPI
            LeptonAPI.start_lepton()  # start film a temp
            # from scripts.Arduino import ledController
            # LedController.start_led()  # start the Arduino
        else:
            self.isRecording = False
            buttonTurnOn.disabled = False  # Enable the TurnOff (button)
            buttonStart.text = 'Start'
            self.SMICamera.start_stop_record_video()
            from scripts.API import LeptonAPI
            LeptonAPI.stop_lepton(self.fileWriter, self.startTestTimeStamp)  # stop lepton film

    def on_off_heat(self, buttonHeat): #
        from scripts.Arduino import LedController
        from scripts.API import LeptonAPI
        if not self.isHeated:
            LedController.start_led()  # start the Arduino
            LeptonAPI.mark_heating_point()
            self.isHeated = True
            buttonHeat.text = 'Cool'
        else:
            LedController.stop_led()  # stop the Arduino
            LeptonAPI.mark_decay_point()
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
