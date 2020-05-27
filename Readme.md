# HTBioApp

Hello everyone,

Here is a guide to operating the system for the first time

## Pre installation

** Follow the steps listed here

Download and install python 3.7.4

Run PreRequisite.py from HT\scripts\Utils\ in cmd
```bash
python PreRequisite.py
```

Install  VC from HT\scripts\Utils\Redistributables  VC_redist.x{64/86(32)} 
* check before install 32bit or 64bit

Unblock the DLL files from x64/x86
```bash
dir -Recurse | Unblock-File
```
or
```bash
get-childitem "full path of folder" -recurse | unblock-file -confirm
```
* from powerShell or cmd

##Appendices

What Left:

1. Make script from Readme
2. Fix video & fps
3. Handle disconnect CV2 & Lepton
4. Close Led in crash of the app
5. Adding button from the arduino