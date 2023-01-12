from constants import *
from ctypes import windll
from PIL import Image
import base64
import pygame
import numpy
import cv2
import os
import io


def isAdmin():
    try:
        return windll.shell32.IsUserAnAdmin()
    except:
        return False


def loadBytesImageCv(bstring):
    img = Image.open(io.BytesIO(base64.b64decode(bstring)))
    return cv2.cvtColor(numpy.asarray(img), cv2.COLOR_RGB2BGR)


def loadBytesImagePy(bstring):
    img = Image.open(io.BytesIO(base64.b64decode(bstring)))
    return pygame.image.frombuffer(img.tobytes(), img.size, img.mode)


def indexOf(string, target, idx=0):
    try:
        return string.index(target, idx)
    except ValueError:
        return -1


def customGetLastEdit(path):
    head, tail = os.path.split(path)
    index = indexOf(tail, "T", 0)
    if(index < 0): return 0
    timeString = tail[index-10:index+9]
    date, time = timeString.split("T")
    YY, MM, DD = [int(_) for _ in date.split("-")]
    hh, mm, ss = [int(_) for _ in time.split("-")]
    return (
        (YY * 60 * 60 * 24 * 30 * 12) +
        (MM * 60 * 60 * 24 * 30) +
        (DD * 60 * 60 * 24) +
        (hh * 60 * 60) +
        (mm * 60) + ss
    )


def listdir(path):
    try:
        return sorted(
            [os.path.join(path, d) for d in os.listdir(path)],
            key = customGetLastEdit, reverse = True
        )
    except:
        return []


def FindLoLPath():
    for i in range(26):
        rootChr = chr(65+i)
        if not os.path.exists(f"{rootChr}:\\"): continue
        now = []
        nxt = []
        for child in os.listdir(f"{rootChr}:\\"):
            if os.path.isdir(f"{rootChr}:\\{child}"):
                now.append(f"{rootChr}:\\{child}")

        while(len(now) != 0):
            for path in now:
                if (LOL_PATH_TARGET1 in path) or (LOL_PATH_TARGET2 in path):
                    return path

                for child in listdir(path):
                    cpath = os.path.join(path, child)
                    if os.path.isdir(cpath):
                        if (LOL_PATH_TARGET1 in cpath) or (LOL_PATH_TARGET2 in cpath):
                            return cpath
                        nxt.append(cpath)

            now = nxt
            nxt = []
    return ""