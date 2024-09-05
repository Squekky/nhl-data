from datetime import timezone
import requests
import os

def getStats(season: int):
    
    hatTricks = {}
    gameNum = 0
    while True:
        if gameNum % 20 == 0:
            print(f"{gameNum} Games in: {hatTricks}")
        gameNum += 1
        GAME_URL = f"https://api-web.nhle.com/v1/gamecenter/{season}02{'{:0>4}'.format(str(gameNum))}/boxscore"

        response = requests.get(GAME_URL, params={"Content-Type": "application/json"})
        if response.status_code == 404:
            break
        game = response.json()
        for team in ['homeTeam', 'awayTeam']:
            if game[team]['score'] < 3:
                continue
            for position in game['boxscore']['playerByGameStats'][team].keys():
                for player in game['boxscore']['playerByGameStats'][team][position]:
                    try:
                        goalCount = player['goals']
                    except KeyError:    # Goalies don't score very often do they
                        continue
                    if goalCount >= 3:
                        numHatTricks = goalCount // 3
                        PLAYER_URL = f"https://api-web.nhle.com/v1/player/{player['playerId']}/landing"
                        response = requests.get(PLAYER_URL, params={"Content-Type": "application/json"})
                        playerInfo = response.json()
                        print(game[team].keys())
                        print(game[team]['abbrev'])
                        playerName = f"{playerInfo['firstName']['default']} {playerInfo['lastName']['default']}"
                        try:
                            hatTricks[playerName]['count'] += numHatTricks
                        except KeyError:
                            hatTricks[playerName] = {'count': numHatTricks, 'teams': [game[team]['abbrev']]}

                        if game[team]['abbrev'] not in hatTricks[playerName]['teams']:
                            hatTricks[playerName]['teams'].append(game[team]['abbrev'])
                        


    sortedHatTricks = sorted(hatTricks.items(), key = lambda x: x[1]['count'], reverse=True)
    print(sortedHatTricks)
    currentHatTrickCount = sortedHatTricks[0][1]['count']
    currentPlace = 1
    print(sortedHatTricks[0])
    for hatTrick in sortedHatTricks:
        if hatTrick[1]['count'] > 1:
            if hatTrick[1]['count'] != currentHatTrickCount:
                currentPlace += 1
                currentHatTrickCount = hatTrick[1]['count']
            print(f"{currentPlace}. [**{'/'.join(hatTrick[1]['teams'])}**] {hatTrick[0]} - **{hatTrick[1]['count']}**")
                

def optimizedStats(season: int):
    GAME_URL = f"https://api-web.nhle.com/v1/gamecenter/{str(season)}020001/boxscore"
    response = requests.get(GAME_URL, params={"Content-Type": "application/json"})
    firstGame = response.json()
    currentWeek = firstGame['gameDate']

    hatTricks = {}
    weekNum = 0
    seasonString = int(f"{str(season)}{str(season+1)}")
    while seasonString != "":
        print(f"Week {weekNum} - {hatTricks}")
        weekNum += 1
        WEEK_URL = f"https://api-web.nhle.com/v1/schedule/{currentWeek}"
        response = requests.get(WEEK_URL, params={"Content-Type": "application/json"})
        schedule = response.json()
        currentWeek = schedule['nextStartDate']

        for day in schedule['gameWeek']:
            for game in day['games']:
                if game['season'] != seasonString:
                    print(f"({game['season']}) {type(game['season'])}")
                    print(f"({seasonString}) {type(seasonString)}")
                    seasonString = ""
                    break
                if game['gameType'] != 2:
                    continue
                for team in ['homeTeam', 'awayTeam']:
                    if game[team]['score'] < 3:
                        continue
                    GAME_URL = f"https://api-web.nhle.com/v1/gamecenter/{game['id']}/boxscore"
                    response = requests.get(GAME_URL, params={"Content-Type": "application/json"})
                    boxscore = response.json()
                    for position in boxscore['boxscore']['playerByGameStats'][team].keys():
                        for player in boxscore['boxscore']['playerByGameStats'][team][position]:
                            try:
                                goalCount = player['goals']
                            except KeyError:    # Goalies don't score very often do they
                                continue
                            if goalCount >= 3:
                                numHatTricks = goalCount // 3
                                PLAYER_URL = f"https://api-web.nhle.com/v1/player/{player['playerId']}/landing"
                                response = requests.get(PLAYER_URL, params={"Content-Type": "application/json"})
                                playerInfo = response.json()
                                playerName = f"{playerInfo['firstName']['default']} {playerInfo['lastName']['default']}"
                                try:
                                    hatTricks[playerName]['count'] += numHatTricks
                                except KeyError:
                                    hatTricks[playerName] = {'count': numHatTricks, 'teams': [boxscore[team]['abbrev']]}

                                if boxscore[team]['abbrev'] not in hatTricks[playerName]['teams']:
                                    hatTricks[playerName]['teams'].append(boxscore[team]['abbrev'])
                                


    sortedHatTricks = sorted(hatTricks.items(), key = lambda x: x[1]['count'], reverse=True)
    print(sortedHatTricks)
    currentHatTrickCount = sortedHatTricks[0][1]['count']
    currentPlace = 1
    print(sortedHatTricks[0])
    for hatTrick in sortedHatTricks:
        if hatTrick[1]['count'] > 1:
            if hatTrick[1]['count'] != currentHatTrickCount:
                currentPlace += 1
                currentHatTrickCount = hatTrick[1]['count']
            print(f"{currentPlace}. [**{'/'.join(hatTrick[1]['teams'])}**] {hatTrick[0]} - **{hatTrick[1]['count']}**")

"""
parent_dir = "Season Stats"
for season in seasons:
    season = str(season)
    season = season[0:4] + "-" + season[4:]  # Format season like 2019-20
    season_path = os.path.join(parent_dir, season)
    try:  # Make season folder if it doesn't exist
        os.mkdir(season_path)
    except FileExistsError:
        pass
"""

try:  # Make season folder if it doesn't exist
    os.mkdir("Season Stats")
except FileExistsError:
    pass

# getStats(1998)
optimizedStats(1990)

