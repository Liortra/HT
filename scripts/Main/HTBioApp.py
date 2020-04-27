import cv2
from kivy.app import App
from kivy.clock import Clock
from kivy.graphics.texture import Texture
from kivy.lang import Builder
from kivy.uix.image import Image
from kivy.uix.screenmanager import ScreenManager, Screen
from datetime import datetime
import os.path

# init and const
Builder.load_file("htbio.kv")
# this section creates the date object
dateTimeObj = datetime.now()
now = dateTimeObj.strftime("%d%m%Y%H%M%S")  # ddMMyyyyHHmmss
# path to scripts/HTBio_files
basepath = os.path.dirname(__file__)
nameFile = now + '.HTBio'
nameVideo = now + '.avi'
# Setting for saving the SMI video
videoName = os.path.abspath(os.path.join(basepath, "..", "HTBio_files/", nameVideo))
fourcc = cv2.VideoWriter_fourcc(*'XVID')
out = cv2.VideoWriter(videoName, fourcc, 20.0, (640, 480))
# Setting for saving HTBio file from Lepton cam
filename = os.path.abspath(os.path.join(basepath, "..", "HTBio_files/", nameFile))
file = open(filename, 'wb+')
# cameraID2 = 0  # id of FLIR Lepton - check port 0 / 2
cameraID1 = 1  # id of SMI Depstech - check port


class SMICamera(Image):
    def __init__(self, parent, capture, **kwargs):
        super(SMICamera, self).__init__(**kwargs)
        self.capture = capture  # data to read
        self.parent = parent  # this object's parent (= box layout)
        self.started = False  # start state
        self.TurnOn = False  # to turn on camera

    # starts the "Camera", capturing at 30 fps by default
    def start(self, fps=30):
        Clock.schedule_interval(self.update, 1.0 / fps)

    # run a video on screen
    def update(self, dt):
        ret, self.frame = self.capture.read()
        if ret:
            if self.started:  # push on start button
                out.write(self.frame)
            # convert it to texture
            image_texture = self.get_texture_from_frame(self.frame, 0)
            # display image from the texture
            self.texture = image_texture
            self.parent.ids['imageCamera'].texture = self.texture

    def stop(self):
        Clock.unschedule(self.update)

    def get_texture_from_frame(self, frame, flipped):
        buffer_frame = cv2.flip(frame, flipped)
        buffer_frame_str = buffer_frame.tostring()
        image_texture = Texture.create(size=(frame.shape[1], frame.shape[0]), colorfmt='bgr')
        image_texture.blit_buffer(buffer_frame_str, colorfmt='bgr', bufferfmt='ubyte')
        return image_texture

    def start_stop_RecordVideo(self):
        self.started = not self.started


class CameraScreen(Screen):
    turnOn = False
    heat = False
    # initialize the "Camera"
    SMICamera = Image(source='logo.jpg')

    def startCamera(self, imageCamera, buttonTurnOn, buttonStart, buttonStop, buttonBack, buttonHeat):
        from scripts.API import LeptonAPI
        from scripts.Arduino import on_off_led
        if not self.turnOn:
            self.capture = cv2.VideoCapture(cameraID1)  # capture SMI cam
            self.SMICamera = SMICamera(self, self.capture)  # change the window from logo to camera
            imageCamera = self.SMICamera
            self.SMICamera.start()
            # Set as started
            self.turnOn = True
            buttonTurnOn.text = 'Turn Off'
            # when started, let start enabled
            buttonStop.disabled = False  # enabled
            # Enable the Start (button)
            buttonStart.disabled = False
            # Prevent the back (button)
            buttonBack.disabled = True
            # initCam(filename, now) - delete this row
            LeptonAPI.initCam()  # init Lepton cam - need to check if needed
            buttonHeat.disabled = False # enabled
            self.heat = True
            on_off_led.initLed()  # start the Arduino
        else:  # press on TurnOff
            self.turnOn = False  # stop what was "started"
            buttonTurnOn.text = 'Turn ON'
            self.SMICamera.stop()
            # Reset camera to home image
            self.SMICamera.stop()
            self.SMICamera = Image(source='logo.jpg')
            imageCamera.source = self.SMICamera.source
            imageCamera.reload()
            # Prevent the Stop (button)
            buttonStop.disabled = True
            # Prevent the Start (button)
            buttonStart.disabled = True
            # Enabled the back (button)
            buttonBack.disabled = False
            # Prevent the Heat (button)
            buttonHeat.text = 'Heat'
            buttonHeat.disabled = True
            self.heat = False
            # Release the capture
            self.capture.release()

    # start to make a video and run Lepton Camera
    def startVideo(self):  # TODO need to check how disable stop button
        if self.turnOn:  # Was running at click
            self.SMICamera.start_stop_RecordVideo()  # start film a video
            from scripts.API import LeptonAPI
            LeptonAPI.startLepton()  # start film a temp
            # from scripts.Arduino import on_off_led
            # on_off_led.startLed()  # start the Arduino

    # stop the video
    def stopVideo(self):  # TODO need to check how disable start button
        self.SMICamera.start_stop_RecordVideo()
        from scripts.API import LeptonAPI
        LeptonAPI.stopLepton(file, now)  # stop lepton film
        # from scripts.Arduino import on_off_led
        # on_off_led.stopLed()  # stop the Arduino

    def ledHeat(self, buttonHeat):
        if self.heat:
            from scripts.Arduino import on_off_led
            on_off_led.startLed()  # start the Arduino
            buttonHeat.text = 'Cool'
            self.heat = False
        elif not self.heat:
            from scripts.Arduino import on_off_led
            on_off_led.stopLed()  # stop the Arduino
            buttonHeat.text = 'Heat'
            self.heat = True


class MainScreen(Screen):
    def exitApp(self):
        MainApp.stop()


class MainApp(App):
    def build(self):
        screenManager = ScreenManager()
        screenManager.add_widget(MainScreen(name="main"))
        screenManager.add_widget(CameraScreen(name="camera"))
        return screenManager


# Start the MainApp
if __name__ == '__main__':
    MainApp().run()
