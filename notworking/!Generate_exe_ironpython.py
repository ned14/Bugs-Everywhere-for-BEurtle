# Invoke IronPython to spit out a .NET ILM version of BE
import sys, os, subprocess

IPYEXE="""g:\Program Files\IronPython 2.7.1\ipy.exe"""
PYC="""g:\Program Files\IronPython 2.7.1\Tools\Scripts\pyc.py"""
files=["be.py"]
for dirpath, dirnames, filenames in os.walk("libbe"):
    for filename in filenames:
        if filename[-3:]==".py":
            files.append(os.path.join(dirpath, filename))
for dirpath, dirnames, filenames in os.walk("yaml"):
    for filename in filenames:
        if filename[-3:]==".py":
            files.append(os.path.join(dirpath, filename))

cmd="\""+IPYEXE+"\" \""+PYC+"\" /main:be.py /target:exe "+" ".join(files)
print cmd
subprocess.call(cmd)
