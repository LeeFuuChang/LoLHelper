from constants import *

import functions

from spellIcons import spellIcons

import requests as rq
from urllib3.exceptions import InsecureRequestWarning
rq.packages.urllib3.disable_warnings(InsecureRequestWarning)
import keyboard
import win32gui
import win32con
import win32api
import win32ui
from ctypes import windll
user32 = windll.user32
user32.SetProcessDPIAware()
import numpy
import time
import math
import json
import cv2
import os


class LoLHelper:

    KEYBOARD_LANGUAGE_IDS = {
        "zh-TW": 0x404,
        "en-US": 0x409
    }

    LANES = ["TOP", "JG", "MID", "AD", "SUP"]

    SPELL_COOLDOWNS = {
        "Barrier": 180,
        "Clarity": 240,
        "Cleanse": 210,
        "Exhaust": 210,
        "Flash": 300,
        "Ghost": 210,
        "Heal": 240,
        "Ignite": 180,
        "Mark": 80,
        "Smite": 90,
        "Teleport": 240,
    }

    LOL_CLIENT_WINDOW_NAME = "League of Legends"
    LOL_GAME_WINDOW_NAME = "League of Legends (TM) Client"


    def __init__(self):
        self.LoLPath = ""
        self.getLoLPath()
        self.CurrentSeason = 0
        self.RiotClientAccessUrl = ""
        self.RiotUserAccessToken = ""
        self.reset()
        self.initialize()


    def getLoLPath(self):
        data = {}
        if(os.path.exists(DATA_STORAGE)):
            with open(DATA_STORAGE, "r") as f:
                data = json.load(f)
            self.LoLPath = data.get("LoLPath", "")
            if(os.path.exists(os.path.join(f"{self.LoLPath}", "Logs"))): return
        print("First time opening LoLHelper. . .")
        print("Locating LoL storage location. . .")
        self.LoLPath = functions.FindLoLPath()
        data["LoLPath"] = self.LoLPath
        if(not os.path.exists(os.path.join(self.LoLPath, "Logs"))):
            while(not os.path.exists(os.path.join(self.LoLPath, "Logs"))):
                print("-"*SEPERATING_COUNT)
                print("Failed to locate LoL storage location")
                self.LoLPath = input("Please enter LoL path (e.g. C:\Riot Games\League of Legends): ")
                self.LoLPath = self.LoLPath.replace("\"", "").replace("\'", "")
                print("-"*SEPERATING_COUNT)
        print("-"*SEPERATING_COUNT)
        print("LoL storage location: ", self.LoLPath)
        print("-"*SEPERATING_COUNT)
        with open(DATA_STORAGE, "w") as f:
            json.dump(data, f)



    def initialize(self):
        if(not self.LoLPath or not os.path.exists(self.LoLPath)): return
        if(not win32gui.FindWindow(None, self.LOL_CLIENT_WINDOW_NAME)):
            print("Please Open League of Legends. . .")
            time.sleep(5)
            return

        for file in functions.listdir(f"{self.LoLPath}\\Logs\\LeagueClient Logs\\"):
            if CLIENT_LOG_FILETYPE in file:
                LatestClientLog = file
                break

        with open(LatestClientLog, "r", encoding="utf-8") as f:
            log = f.read()
        log = log.split("Application Version:")[1]
        vsn = int(log[:functions.indexOf(log, ".")])

        idx = functions.indexOf(log, RIOT_BASE_URL)
        RiotClientAccessUrl = log[idx : functions.indexOf(log, "/", idx+len(RIOT_BASE_URL))]
        RiotUserAccessToken = RiotClientAccessUrl[len(RIOT_BASE_URL) : functions.indexOf(RiotClientAccessUrl, "@")]
        RiotClientAccessUrl = RiotClientAccessUrl[:len(HTTPS)] + RiotClientAccessUrl[functions.indexOf(RiotClientAccessUrl, "@")+1:]

        self.CurrentSeason = vsn
        self.RiotClientAccessUrl = RiotClientAccessUrl
        self.RiotUserAccessToken = RiotUserAccessToken

        ready = self.contactServer()
        if(not ready["success"]): 
            print("Please Open League of Legends. . .")
            time.sleep(5)
            return

        print("-"*SEPERATING_COUNT)
        print(f"LoL Client Version : {vsn}")
        print(f"LoL ClientAccessURL: {RiotClientAccessUrl}")
        print(f"LoL UserAccessToken: {RiotUserAccessToken}")
        print("-"*SEPERATING_COUNT)



    def contactServer(self):
        data = self.fetch(f"lol-summoner/v1/current-summoner")
        if not data["success"]: return FAILED_JSON_RETURN.copy()
        else: data = data["res"]
        if data.get("errorCode"): return FAILED_JSON_RETURN.copy()

        puuid = data.get("puuid", None)
        username = data.get("displayName", None)
        accountId = data.get("accountId", None)
        if puuid is None or username is None or accountId is None: return FAILED_JSON_RETURN.copy()

        self.post(f"Login", payload={"puuid":puuid, "username":username, "accountId":accountId})

        return SUCCESS_JSON_RETURN.copy()



    def reset(self):
        self.loadedLogData = {"logDir": ""}
        self.enemyData = {
            "TOP": {
                "C": "",
                "D": {
                    "name": "",
                    "conf": 0,
                    "time": 0
                },
                "F": {
                    "name": "",
                    "conf": 0,
                    "time": 0
                },
            },
            "JG": {
                "C": "",
                "D": {
                    "name": "",
                    "conf": 0,
                    "time": 0
                },
                "F": {
                    "name": "",
                    "conf": 0,
                    "time": 0
                },
            },
            "MID": {
                "C": "",
                "D": {
                    "name": "",
                    "conf": 0,
                    "time": 0
                },
                "F": {
                    "name": "",
                    "conf": 0,
                    "time": 0
                },
            },
            "AD": {
                "C": "",
                "D": {
                    "name": "",
                    "conf": 0,
                    "time": 0
                },
                "F": {
                    "name": "",
                    "conf": 0,
                    "time": 0
                },
            },
            "SUP": {
                "C": "",
                "D": {
                    "name": "",
                    "conf": 0,
                    "time": 0
                },
                "F": {
                    "name": "",
                    "conf": 0,
                    "time": 0
                },
            },
        }



    def isReady(self):
        return self.CurrentSeason != 0 and self.RiotClientAccessUrl != "" and self.RiotUserAccessToken != ""



    def dataFilled(self):
        if(not self.isReady()): return False
        return all((
            self.loadedLogData["logDir"] == functions.listdir(f"{self.LoLPath}\\Logs\\GameLogs\\")[0] and
            self.enemyData[lane]["C"] and 
            self.enemyData[lane]["D"]["name"] and 
            self.enemyData[lane]["F"]["name"] and
            self.enemyData[lane]["D"]["conf"] > 0.5 and 
            self.enemyData[lane]["F"]["conf"] > 0.5
        ) for lane in self.LANES)



    def fetch(self, route):
        if not self.isReady(): return FAILED_JSON_RETURN.copy()
        try:
            res = rq.get(
                f"{self.RiotClientAccessUrl}/{route}", auth=(
                    "riot", f"{self.RiotUserAccessToken}"
                ), verify=False
            ).json()
            data = {"success":True, "res":res}
        except:
            return FAILED_JSON_RETURN.copy()
        return data



    def post(self, route, payload):
        try:
            res = rq.get(f"{LOL_HELPER_SERVER_BASE_URL}/{route}", params=payload).json()
            data = {"success":True, "res":res}
        except:
            return FAILED_JSON_RETURN.copy()
        return data



    def checkSummonerGamePhase(self):
        data = self.fetch("lol-gameflow/v1/gameflow-phase")
        if not data["success"]: 
            self.initialize()
            return False
        return data["res"].lower()



    def getLoLGameHWND(self):
        # return win32gui.GetForegroundWindow()
        return win32gui.FindWindow(None, self.LOL_GAME_WINDOW_NAME)
        


    def getLoLScreenShot(self):
        hwnd = self.getLoLGameHWND()

        # get window region
        if hwnd:
            info = win32gui.GetWindowRect(hwnd)
            region = (info[0], info[1], info[2]-info[0], info[3]-info[1])
        else:
            region = (0, 0, user32.GetSystemMetrics(0), user32.GetSystemMetrics(1))
        if hwnd:
            if win32gui.GetWindowRect(hwnd) == (0, 0, user32.GetSystemMetrics(0), user32.GetSystemMetrics(1)):
                hwnd = 0

        # get the window image data
        wDC = win32gui.GetWindowDC(hwnd)
        dcObj = win32ui.CreateDCFromHandle(wDC)
        cDC = dcObj.CreateCompatibleDC()
        dataBitMap = win32ui.CreateBitmap()
        dataBitMap.CreateCompatibleBitmap(dcObj, region[2], region[3])
        cDC.SelectObject(dataBitMap)
        cDC.BitBlt((0, 0), (region[2]+region[0], region[3]+region[1]), dcObj, (region[0], region[1]), win32con.SRCCOPY)

        # convert the raw data into a format opencv can read
        #dataBitMap.SaveBitmapFile(cDC, 'debug.bmp')
        signedIntsArray = dataBitMap.GetBitmapBits(True)
        img = numpy.frombuffer(signedIntsArray, dtype=numpy.uint8)
        img.shape = (region[3], region[2], 4)

        # free resources
        dcObj.DeleteDC()
        cDC.DeleteDC()
        win32gui.ReleaseDC(hwnd, wDC)
        win32gui.DeleteObject(dataBitMap.GetHandle())

        # drop the alpha channel, or cv.matchTemplate() will throw an error like:
        #   error: (-215:Assertion failed) (depth == CV_8U || depth == CV_32F) && type == _templ.type() 
        #   && _img.dims() <= 2 in function 'cv::matchTemplate'
        img = img[...,:3]

        # make image C_CONTIGUOUS to avoid errors that look like:
        #   File ... in draw_rectangles
        #   TypeError: an integer is required (got type tuple)
        # see the discussion here:
        # https://github.com/opencv/opencv/issues/14866#issuecomment-580207109
        img = numpy.ascontiguousarray(img)

        self.preGameScreenShot = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

        return self.preGameScreenShot



    def processGameLogString(self, logString):
        looking = ""
        currentIdx = 0
        isLocal = "**LOCAL**" in logString

        looking = "Team"
        currentIdx = functions.indexOf(logString, looking)
        side =  logString[currentIdx+len(looking) : functions.indexOf(logString, " ", currentIdx+1)] if(currentIdx>=0)else None
        side = "R" if(side == "Chaos")else "B" 

        looking = "'"
        currentIdx = functions.indexOf(logString, looking)
        username =  logString[currentIdx+len(looking) : functions.indexOf(logString, "'", currentIdx+1)] if(currentIdx>=0)else None

        looking = "Champion("
        currentIdx = functions.indexOf(logString, looking)
        champion =  logString[currentIdx+len(looking) : functions.indexOf(logString, ")", currentIdx+1)] if(currentIdx>=0)else None

        looking = "TeamBuilderRole("
        currentIdx = functions.indexOf(logString, looking)
        role =  logString[currentIdx+len(looking) : functions.indexOf(logString, ")", currentIdx+1)] if(currentIdx>=0)else None

        looking = "PUUID("
        currentIdx = functions.indexOf(logString, looking)
        puuid =  logString[currentIdx+len(looking) : functions.indexOf(logString, ")", currentIdx+1)] if(currentIdx>=0)else None

        result = {
            "puuid": puuid,
            "username": username,
            "champion": champion,
            "isLocal": isLocal,
            "role": ROLE_ABBREVIATION.get(role, None),
            "side": side,
        }

        return result



    def getAllPlayerData(self):
        if not self.isReady(): self.initialize()

        logDir = functions.listdir(f"{self.LoLPath}\\Logs\\GameLogs\\")[0]
        if(logDir == self.loadedLogData["logDir"]): return self.loadedLogData["data"]

        self.reset()

        # print("Latest Game Dir:", logDir)
        with open(os.path.join(logDir, f"{os.path.split(logDir)[1]}_r3dlog.txt"), "r", encoding="utf-8") as f:
            logData = f.read()

        local = None
        current_idx = 0
        OrderPlayerDatas = []
        ChaosPlayerDatas = []

        for i in range(5):
            current_idx = functions.indexOf(logData, f"TeamOrder {i}) ")
            if(current_idx >= 0):
                logString = logData[current_idx : functions.indexOf(logData, "\n", current_idx)]
                playerData = self.processGameLogString(logString)
                OrderPlayerDatas.append(playerData)
                if(playerData["isLocal"]): local = playerData

        for i in range(5):
            current_idx = functions.indexOf(logData, f"TeamChaos {i}) ")
            if(current_idx >= 0):
                logString = logData[current_idx : functions.indexOf(logData, "\n", current_idx)]
                playerData = self.processGameLogString(logString)
                ChaosPlayerDatas.append(playerData)
                if(playerData["isLocal"]): local = playerData

        ally  = OrderPlayerDatas if( local and local["side"] == "B" )else ChaosPlayerDatas
        enemy = ChaosPlayerDatas if( local and local["side"] == "B" )else OrderPlayerDatas

        if( local and ally and enemy ):
            self.loadedLogData["logDir"] = logDir
            self.loadedLogData["data"] = (local, ally, enemy)
            # print("Latest Game Dir Loaded")

        return local, ally, enemy



    def collectEnemyData(self):
        local, ally, enemy = self.getAllPlayerData()
        # print("Collecting EnemyData")
        if( not local ): return self.reset()
        enemySide = "B" if( local["side"] == "R" )else "R"
        h, w, c = self.preGameScreenShot.shape
        gcd = math.gcd(w, h)
        ratio = f"{w//gcd}:{h//gcd}"
        if ratio not in GAME_RATIO_CROP_COORDNATES:
            # print("No Such Ratio(", ratio, ")")
            return
        if( (w, h) != GAME_RATIO_CROP_COORDNATES[ratio]["standard"] ):
            # print("Resize Image")
            self.preGameScreenShot = cv2.resize(self.preGameScreenShot, GAME_RATIO_CROP_COORDNATES[ratio]["standard"])

        templateMatchingTimes = 3

        if(not all(p["role"] for p in enemy)):
            for playerIndex in range(5):
                self.enemyData[self.LANES[playerIndex]]["C"] = enemy[playerIndex]["champion"]
                spells = list(self.SPELL_COOLDOWNS.keys())
                for spellIndex in range(2):
                    detectResult = [[spell, 0] for spell in spells]
                    for idx, spellName in enumerate(spells):
                        bestResult = 0
                        for t in range(templateMatchingTimes):
                            x1, y1, x2, y2 = GAME_RATIO_CROP_COORDNATES[ratio][f"{enemySide}_Spell"][playerIndex][spellIndex]
                            img = self.preGameScreenShot[y1:y2, x1:x2]
                            template = functions.loadBytesImageCv(spellIcons[spellName])
                            result = cv2.minMaxLoc(
                                cv2.matchTemplate(img, template, cv2.TM_CCOEFF_NORMED)
                            )[1]
                            bestResult = max(bestResult, result)
                        detectResult[idx][1] = bestResult
                    detectResult.sort(key=lambda x:x[1], reverse=True)
                    if(detectResult[0][1] < self.enemyData[self.LANES[playerIndex]][["D", "F"][spellIndex]]["conf"]): continue
                    spells.remove(detectResult[0][0])
                    # print(playerIndex, ["D", "F"][spellIndex], detectResult[0])
                    self.enemyData[self.LANES[playerIndex]][["D", "F"][spellIndex]]["name"] = detectResult[0][0]
                    self.enemyData[self.LANES[playerIndex]][["D", "F"][spellIndex]]["conf"] = detectResult[0][1]
                # print()
        else:
            for playerIndex, player in enumerate(enemy):
                self.enemyData[player["role"]]["C"] = player["champion"]
                spells = list(self.SPELL_COOLDOWNS.keys())
                for spellIndex in range(2):
                    detectResult = [[spell, 0] for spell in spells]
                    for idx, spellName in enumerate(spells):
                        bestResult = 0
                        for t in range(templateMatchingTimes):
                            x1, y1, x2, y2 = GAME_RATIO_CROP_COORDNATES[ratio][f"{enemySide}_Spell"][playerIndex][spellIndex]
                            img = self.preGameScreenShot[y1:y2, x1:x2]
                            template = functions.loadBytesImageCv(spellIcons[spellName])
                            result = cv2.minMaxLoc(
                                cv2.matchTemplate(img, template, cv2.TM_CCOEFF_NORMED)
                            )[1]
                            bestResult = max(bestResult, result)
                        detectResult[idx][1] = bestResult
                    detectResult.sort(key=lambda x:x[1], reverse=True)
                    if(detectResult[0][1] < self.enemyData[self.LANES[playerIndex]][["D", "F"][spellIndex]]["conf"]): continue
                    spells.remove(detectResult[0][0])
                    # print(playerIndex, ["D", "F"][spellIndex], detectResult[0])
                    self.enemyData[player["role"]][["D", "F"][spellIndex]]["name"] = detectResult[0][0]
                    self.enemyData[player["role"]][["D", "F"][spellIndex]]["conf"] = detectResult[0][1]
                # print()
        # print("-"*100)
        if( self.dataFilled() ):
            print("-"*SEPERATING_COUNT)
            for role in self.LANES:
                for spellIndex in range(2):
                    spellKey = ["D", "F"][spellIndex]
                    print(f"{role:>3} {spellKey} {int(self.enemyData[role][spellKey]['conf']*100):>3}% {self.enemyData[role][spellKey]['name']}")
                print()
            print("-"*SEPERATING_COUNT)



    def setSpellCastTime(self, laneIndex, spellIndex, time):
        if(not self.dataFilled()): return
        print(f"recorded {self.LANES[laneIndex]:>3} {['D', 'F'][spellIndex]} cast time")
        self.enemyData[self.LANES[laneIndex]][["D", "F"][spellIndex]]["time"] = time


    def resetSpellCastTime(self, laneIndex, spellIndex):
        if(not self.dataFilled()): return
        print(f" cleared {self.LANES[laneIndex]:>3} {['D', 'F'][spellIndex]} cast time")
        self.enemyData[self.LANES[laneIndex]][["D", "F"][spellIndex]]["time"] = 0


    def broadcastEnemySpellCooldown(self, lanes=None):
        nowTime = time.time()
        hwnd = self.getLoLGameHWND()
        print("broadcasting spell cooldown of: ", " | ".join(lanes))
        if(not hwnd): return print("can't fint LoL game window, cancel broadcast")
        win32gui.SetWindowPos(hwnd, win32con.HWND_TOPMOST, 0,0,0,0, win32con.SWP_NOMOVE | win32con.SWP_NOSIZE)
        win32api.SendMessage(hwnd, win32con.WM_INPUTLANGCHANGEREQUEST, 0, self.KEYBOARD_LANGUAGE_IDS["en-US"])
        if( win32api.GetKeyState(win32con.VK_CAPITAL) ): win32api.keybd_event(0x14, 0, 0, 0)
        time.sleep(0.05)
        win32api.keybd_event(0x14, 0, win32con.KEYEVENTF_KEYUP, 0)
        for lane in (lanes if(lanes)else self.LANES):
            print(f"broadcast {lane:_>3} spell cooldown ( {self.enemyData[lane]['C']} )")
            DcastTime = self.enemyData[lane]["D"]["time"]
            FcastTime = self.enemyData[lane]["F"]["time"]

            Dcooldown = self.SPELL_COOLDOWNS[self.enemyData[lane]["D"]["name"]]
            Fcooldown = self.SPELL_COOLDOWNS[self.enemyData[lane]["F"]["name"]]

            DleftTime = max(Dcooldown-int(nowTime-DcastTime), 0)
            FleftTime = max(Fcooldown-int(nowTime-FcastTime), 0)

            text = f"{lane:_>3} | D {DleftTime:0>3}s | F {FleftTime:0>3}s | ( {self.enemyData[lane]['C']} )"
            print(text)

            keyboard.press_and_release("enter")
            time.sleep(0.025)
            keyboard.write(text)
            time.sleep(0.025)
            keyboard.press_and_release("enter")
        win32api.SendMessage(hwnd, win32con.WM_INPUTLANGCHANGEREQUEST, 0, self.KEYBOARD_LANGUAGE_IDS["zh-TW"])
        win32gui.SetWindowPos(hwnd, win32con.HWND_NOTOPMOST, 0,0,0,0, win32con.SWP_NOMOVE | win32con.SWP_NOSIZE)
        time.sleep(0.05)



    def update(self):
        nowTime = time.time()
        for lane in self.LANES:
            DcastTime = self.enemyData[lane]["D"]["time"]
            FcastTime = self.enemyData[lane]["F"]["time"]
            if(not (DcastTime+FcastTime)): continue

            Dcooldown = self.SPELL_COOLDOWNS[self.enemyData[lane]["D"]["name"]]
            Fcooldown = self.SPELL_COOLDOWNS[self.enemyData[lane]["F"]["name"]]

            DleftTime = Dcooldown-int(nowTime-DcastTime)
            if(DleftTime <= 0): self.enemyData[lane]["D"]["time"] = 0
            FleftTime = Fcooldown-int(nowTime-FcastTime)
            if(FleftTime <= 0): self.enemyData[lane]["F"]["time"] = 0
