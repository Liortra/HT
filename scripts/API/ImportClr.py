import clr  # needs the "pythonnet" package
import sys
import os

import platform

bits, name = platform.architecture()

if bits == "64bit":
    folder = ["x64"]
else:
    folder = ["x86"]

sys.path.append(os.path.join("..", *folder))
sys.path.append(os.path.join(*folder))

# sys.path.append(os.path.join("..", "..", "ir16filters", *folder))

clr.AddReference("LeptonUVC")
clr.AddReference('System.Drawing')

