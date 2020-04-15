import cv2
from kivy.app import App
from kivy.clock import Clock
from kivy.graphics.texture import Texture
from kivy.lang import Builder
from kivy.uix.image import Image
from kivy.uix.screenmanager import ScreenManager, Screen
import runpy

Builder.load_file("htbio.kv")
# Setting for saving the SMI video
fourcc = cv2.VideoWriter_fourcc(*'XVID')
out = cv2.VideoWriter('output.avi', fourcc, 20.0, (640, 480))

# cameraID2 = 0  # id of FLIR Lepton
cameraID1 = 0  # id of SMI Depstech


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

    def update(self, dt):
        ret, self.frame = self.capture.read()
        if ret:
            if self.started:
                out.write(self.frame)
            # Since we want to show something larger on the screen than the
            # original 320x240, we resize the image again
            # Note that it would also be possible to keep the large version
            # of the baseimage and make the result image a copy of this large
            # base image and use the scaling factor to draw the rectangle
            # at the right coordinates.
            resize_frame_result = cv2.resize(self.frame, (self.frame.shape[1], self.frame.shape[0]))
            # convert it to texture
            image_texture = self.get_texture_from_frame(self.frame, 0)
            # display image from the texture
            self.texture = image_texture
            self.parent.ids['imageCamera'].texture = self.texture
            # print('updated')

    def stop(self):
        Clock.unschedule(self.update)

    def get_texture_from_frame(self, frame, flipped):
        buffer_frame = cv2.flip(frame, flipped)
        buffer_frame_str = buffer_frame.tostring()
        image_texture = Texture.create(size=(frame.shape[1], frame.shape[0]), colorfmt='bgr')
        # print('(' + str(frame.shape[1]) + ';' + str(frame.shape[0]) + ')')
        image_texture.blit_buffer(buffer_frame_str, colorfmt='bgr', bufferfmt='ubyte')
        return image_texture

    def start_stop_RecordVideo(self):
        self.started = not self.started


class CameraScreen(Screen):
    turnOn = False
    # initialize the "Camera"
    SMICamera = Image(source='logo.jpg')

    def startCamera(self, imageCamera, buttonTurnOn, buttonStart, buttonStop, buttonBack):
        if not self.turnOn:
            self.capture = cv2.VideoCapture(cameraID1)
            self.SMICamera = SMICamera(self, self.capture)
            imageCamera = self.SMICamera
            self.SMICamera.start()
            # Set as started, so next action will be 'Pause'
            self.turnOn = True
            buttonTurnOn.text = 'Turn Off'
            # when started, let start enabled
            buttonStop.disabled = False  # enabled
            # Enable the Start (button)
            buttonStart.disabled = False
            # Prevent the back (button)
            buttonBack.disabled = True
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
            # Release the capture
            self.capture.release()

    # start to make a video and run Lepton Camera
    def startVideo(self):
        if self.turnOn:  # Was running at click
            self.SMICamera.start_stop_RecordVideo()
            runpy.run_path(path_name='Lepton_API.py')

    # stop the video
    def stopVideo(self):
        self.SMICamera.start_stop_RecordVideo()


class MainScreen(Screen):
    def exitApp(self):
        MainApp.stop()


class MainApp(App):
    def build(self):
        screenManager = ScreenManager()
        screenManager.add_widget(MainScreen(name="main"))
        screenManager.add_widget(CameraScreen(name="camera"))
        return screenManager


# Start the Camera App
if __name__ == '__main__':
    MainApp().run()
