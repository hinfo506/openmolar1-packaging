#! /usr/bin/python

import subprocess

IMAGE_FILE = "/home/neil/openmolar/openmolar1/src/openmolar/resources/openmolar_256x256.png"

commands = ["convert", IMAGE_FILE,
            "-define", 'icon:auto-resize=\"256,128,96,64,48,32,16\"',
            "openmolar.ico"]

print(" ".join(commands))

p = subprocess.Popen(commands)
p.wait()
