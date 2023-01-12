from constants import *
import functions

import win32gui
import win32con
from ctypes import windll
user32 = windll.user32
user32.SetProcessDPIAware()
import time
import sys
import os
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = '1'
import pygame
pygame.init()

from championIcons import championIcons
from spellIcons import spellIcons

from LoLhelper import LoLHelper


class Interface:
    def __init__(self):
        screenWidth = user32.GetSystemMetrics(0)
        screenHeight = user32.GetSystemMetrics(1)

        self.borderWidth = max(int(((screenHeight//4) / 5) * 0.037), 1)
        self.spellIconSize = int( (((screenHeight//4) / 5) - self.borderWidth*2) / 2 )
        self.championIconSize = self.spellIconSize*2
        self.minimumDraggingDistance = self.championIconSize/6

        self.displayWidth = self.borderWidth + self.spellIconSize + self.championIconSize + self.borderWidth
        self.displayHeight = (
            self.borderWidth +
            self.championIconSize +
            self.borderWidth +
            self.borderWidth +
            self.championIconSize +
            self.borderWidth +
            self.borderWidth +
            self.championIconSize +
            self.borderWidth +
            self.borderWidth +
            self.championIconSize +
            self.borderWidth +
            self.borderWidth +
            self.championIconSize +
            self.borderWidth
        )

        self.championBlockSize = self.borderWidth+self.championIconSize+self.borderWidth

        os.environ['SDL_VIDEO_WINDOW_POS'] = f"{screenWidth-self.displayWidth},{(screenHeight-self.displayHeight)/2}"

        self.mouseClickTime = 0
        self.mouseClickPosition = (0, 0)

        self.clock = pygame.time.Clock()
        self.window = pygame.display.set_mode((self.displayWidth, self.displayHeight), pygame.NOFRAME)
        self.playerSurfaces = [[pygame.Surface((self.displayWidth, self.championBlockSize)), False, 0] for i in range(5)]

        self.windowObject = pygame.display.get_wm_info()["window"]
        self.setInterfaceTopmost()



    def setInterfaceTopmost(self):
        win32gui.SetWindowPos(self.windowObject, win32con.HWND_TOPMOST, 0,0,0,0, win32con.SWP_NOMOVE | win32con.SWP_NOSIZE)



    def draw(self):
        self.window.fill("#000000")

        nowTime = time.time()

        for playerIndex, (surface, dragging, offset) in sorted(enumerate(self.playerSurfaces), key=lambda x:x[1][1]):
            playerData = self.LoLhelper.enemyData[self.LoLhelper.LANES[playerIndex]]

            surface.fill("#ffffff")

            # Summoner Spell D
            spellIconByte = spellIcons.get(playerData["D"]["name"], spellIcons["Na"])
            surface.blit(
                pygame.transform.scale(
                    functions.loadBytesImagePy(spellIconByte), (self.spellIconSize, self.spellIconSize)
                ), (self.borderWidth, self.borderWidth)
            )
            if(self.LoLhelper.dataFilled()):
                Dcooldown = self.LoLhelper.SPELL_COOLDOWNS[self.LoLhelper.enemyData[self.LoLhelper.LANES[playerIndex]]["D"]["name"]]
                DcastTime = self.LoLhelper.enemyData[self.LoLhelper.LANES[playerIndex]]["D"]["time"]
                DleftTime = max(Dcooldown-int(nowTime-DcastTime), 0)
                coverSize = int(self.spellIconSize*(DleftTime/Dcooldown))
                if(DleftTime and coverSize):
                    coverSurface = pygame.Surface((self.spellIconSize, coverSize))
                    coverSurface.set_alpha(170)
                    surface.blit(coverSurface, (self.borderWidth, self.borderWidth+self.spellIconSize-coverSize))

            # Summoner Spell F
            spellIconByte = spellIcons.get(playerData["F"]["name"], spellIcons["Na"])
            surface.blit(
                pygame.transform.scale(
                    functions.loadBytesImagePy(spellIconByte), (self.spellIconSize, self.spellIconSize)
                ), (self.borderWidth, self.borderWidth+self.spellIconSize)
            )
            if(self.LoLhelper.dataFilled()):
                Fcooldown = self.LoLhelper.SPELL_COOLDOWNS[self.LoLhelper.enemyData[self.LoLhelper.LANES[playerIndex]]["F"]["name"]]
                FcastTime = self.LoLhelper.enemyData[self.LoLhelper.LANES[playerIndex]]["F"]["time"]
                FleftTime = max(Fcooldown-int(nowTime-FcastTime), 0)
                coverSize = int(self.spellIconSize*(FleftTime/Fcooldown))
                if(FleftTime and coverSize):
                    coverSurface = pygame.Surface((self.spellIconSize, coverSize))
                    coverSurface.set_alpha(170)
                    surface.blit(coverSurface, (self.borderWidth, self.borderWidth+(self.spellIconSize*2)-coverSize))

            # Summoner Champion
            championIconByte = championIcons.get(playerData["C"].capitalize(), championIcons["Na"])
            surface.blit(
                pygame.transform.scale(
                    functions.loadBytesImagePy(championIconByte), (self.championIconSize, self.championIconSize)
                ), (self.borderWidth+self.spellIconSize, self.borderWidth)
            )

            self.window.blit(surface, (0, self.championBlockSize*playerIndex + offset*dragging))



    def getCoordnateDisplayLane(self, x, y):
        return (x >= self.borderWidth+self.spellIconSize), (y//self.championBlockSize), (y%self.championBlockSize >= self.borderWidth+self.spellIconSize)



    def update(self):
        nowTime = time.time()
        mx, my = pygame.mouse.get_pos()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False

            if event.type == pygame.MOUSEBUTTONUP:
                if(not self.LoLhelper.dataFilled()): continue
                clickOnChampion, laneIndex, spellIndex = self.getCoordnateDisplayLane(*self.mouseClickPosition)
                if event.button == pygame.BUTTON_LEFT:
                    dragDistance = abs(my - self.mouseClickPosition[1])
                    self.playerSurfaces[laneIndex][1] = False
                    self.playerSurfaces[laneIndex][2] = 0
                    self.mouseClickPosition = (0, 0)
                    if dragDistance < self.minimumDraggingDistance and nowTime-self.mouseClickTime < 0.2:
                        if clickOnChampion:
                            self.LoLhelper.broadcastEnemySpellCooldown(lanes=[self.LoLhelper.LANES[laneIndex], ])
                            self.setInterfaceTopmost()
                        else:
                            self.LoLhelper.setSpellCastTime(laneIndex, spellIndex, time.time())
                elif event.button == pygame.BUTTON_RIGHT and nowTime-self.mouseClickTime < 0.2:
                    if clickOnChampion:
                        self.LoLhelper.resetSpellCastTime(laneIndex, 0)
                        self.LoLhelper.resetSpellCastTime(laneIndex, 1)
                    else:
                        self.LoLhelper.resetSpellCastTime(laneIndex, spellIndex)

            if event.type == pygame.MOUSEBUTTONDOWN:
                self.mouseClickTime = nowTime
                self.mouseClickPosition = (mx, my)

        if pygame.mouse.get_pressed()[0] and self.LoLhelper.dataFilled():
            dragDistance = abs(my - self.mouseClickPosition[1])
            _, laneIndex, _ = self.getCoordnateDisplayLane(*self.mouseClickPosition)
            if dragDistance > self.minimumDraggingDistance:
                self.playerSurfaces[laneIndex][1] = True
                _, nowLaneIndex, _ = self.getCoordnateDisplayLane(mx, my)
                if nowLaneIndex != laneIndex:
                    a, b = self.LoLhelper.enemyData[self.LoLhelper.LANES[laneIndex]], self.LoLhelper.enemyData[self.LoLhelper.LANES[nowLaneIndex]]
                    self.LoLhelper.enemyData[self.LoLhelper.LANES[laneIndex]], self.LoLhelper.enemyData[self.LoLhelper.LANES[nowLaneIndex]] = b, a
                    self.playerSurfaces[laneIndex][1] = False
                    self.playerSurfaces[laneIndex][2] = 0
                    self.playerSurfaces[nowLaneIndex][1] = True
                    self.mouseClickPosition = (mx, my)
                self.playerSurfaces[nowLaneIndex][2] = (my - self.championBlockSize/2) - self.championBlockSize*nowLaneIndex
            else:
                self.playerSurfaces[laneIndex][1] = False
                self.playerSurfaces[laneIndex][2] = 0



    def mainloop(self, LoLhelper):
        self.LoLhelper = LoLhelper
        while(True):
            gamePhase = self.LoLhelper.checkSummonerGamePhase()
            if(gamePhase == "readycheck"):
                pass # ( center, 25/32 )
            elif(gamePhase == "inprogress" or gamePhase == "gamestart"):
                if(not self.LoLhelper.dataFilled()):
                    self.LoLhelper.getLoLScreenShot()
                    self.LoLhelper.collectEnemyData()
                else:
                    self.LoLhelper.update()
            elif(gamePhase == "preendofgame" or gamePhase == "endofgame"):
                self.LoLhelper.reset()
            self.update()
            self.draw()
            self.clock.tick(60)
            pygame.display.update()




os.system("cls")
if not functions.isAdmin() and not sys.argv[0].endswith(".py"):
    windll.shell32.ShellExecuteW(None, "runas", sys.executable, " ".join(sys.argv), None, 1)
    os._exit(0)
else:
    lolHelper = LoLHelper()

    # import cv2
    # lolHelper.preGameScreenShot = cv2.imread("111.png")
    # lolHelper.collectEnemyData()

    interface = Interface()
    interface.mainloop(lolHelper)