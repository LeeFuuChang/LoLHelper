ROLE_ABBREVIATION = {
    "NONE": None,
    "TOP": "TOP",
    "JUNGLE": "JG",
    "MIDDLE": "MID",
    "BOTTOM": "AD",
    "SUPPORT": "SUP",
    "UTILITY": "SUP"
}


PATCH = "1.0.0"
APPLICATION_NAME = "LoLHelper"


HTTPS = "https://"
CLIENT_LOG_FILETYPE = "LeagueClientUx.log"
RIOT_BASE_URL = "https://riot:"


LOL_HELPER_SERVER_BASE_URL = "https://www.leefuuchang.in/projects/LoLHelper"


LOL_PATH_TARGET1 = "Riot Games/League of Legends"
LOL_PATH_TARGET2 = "Riot Games\\League of Legends"


DATA_STORAGE = "C:\\LoL_Spell_Helper_Data.json"


SEPERATING_COUNT = 50


FAILED_JSON_RETURN = {"success":False}
SUCCESS_JSON_RETURN = {"success":True}


TUTORIAL_URL = ""


GAME_RATIO_CROP_COORDNATES = {
    "16:9": {
        "standard": (1920, 1080),
        "B_Banner":[
            [ 242, 60,  497, 520],
            [ 538, 60,  793, 520],
            [ 834, 60, 1089, 520],
            [1130, 60, 1385, 520],
            [1426, 60, 1681, 520],
        ],
        "R_Banner":[
            [ 242, 595,  497, 1055],
            [ 538, 595,  793, 1055],
            [ 834, 595, 1089, 1055],
            [1130, 595, 1385, 1055],
            [1426, 595, 1681, 1055],
        ],
        "B_Spell":[
            [[ 418, 439,  446, 467], [ 451, 439,  479, 467]],
            [[ 714, 439,  742, 467], [ 747, 439,  775, 467]],
            [[1010, 439, 1038, 467], [1043, 439, 1071, 467]],
            [[1306, 439, 1334, 467], [1339, 439, 1367, 467]],
            [[1602, 439, 1630, 467], [1635, 439, 1663, 467]],
        ],
        "R_Spell":[
            [[ 418, 974,  446, 1002], [ 451, 974,  479, 1002]],
            [[ 714, 974,  742, 1002], [ 747, 974,  775, 1002]],
            [[1010, 974, 1038, 1002], [1043, 974, 1071, 1002]],
            [[1306, 974, 1334, 1002], [1339, 974, 1367, 1002]],
            [[1602, 974, 1630, 1002], [1635, 974, 1663, 1002]],
        ]
    }
}