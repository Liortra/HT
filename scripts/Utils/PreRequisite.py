import subprocess
import sys


# installation of the packages of this project
def install_pip(packages):
    for package in packages:
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])


listOfPackages = ['pythonnet', 'jupyterlab', 'numpy', 'matplotlib', 'pySerial', 'opencv-python',
                'wheel', 'setuptools', 'virtualenv', 'docutils', 'pygments',
                'pypiwin32', 'kivy_deps.sdl2==0.1.*', 'kivy_deps.glew==0.1.*',
                'kivy_deps.gstreamer==0.1.*', 'kivy_deps.angle==0.1.*', 'kivy==1.11.1']

install_pip(listOfPackages)
