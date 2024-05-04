#!/usr/bin/python

import sys, os
from imgbox_uploader import imgboxUploader, screenshotGenerator

if not len(sys.argv) == 3:
    print("Not enough command line arguments supplied, expecting 2")
    exit(1)
if not os.path.isfile(sys.argv[1]):
    print("Invalid input file path")
    exit(1)
if not sys.argv[2].isdigit():
    exit(1)

screenshotList = screenshotGenerator.generateScreenshots(os.path.abspath(sys.argv[1]), sys.argv[2])
imgboxUploader.imgboxUpload(screenshotList)

if len(screenshotList) == int(sys.argv[2]):
    for file in screenshotList:
        if os.path.splitext(file)[1].lower() in [".gif", ".jpeg", ".jpg", ".png"]:
            os.remove(file)
