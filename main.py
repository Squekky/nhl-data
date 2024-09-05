from datetime import timezone
import datetime
import requests
import time
import os


def getGoals(boxscore: dict, team: str):
    return boxscore['teams'][team]['teamStats']['teamSkaterStats']['goals']


def getPlayers(boxscore: dict, team: str):
    return boxscore['teams'][team]['players']


def getTeamNames(game: dict):
    homeName = game['teams']['home']['team']['name']
    awayName = game['teams']['away']['team']['name']

    # Get abbreviations
    home_request = requests.get(f'https://statsapi.web.nhl.com{game["teams"]["home"]["team"]["link"]}')
    away_request = requests.get(f'https://statsapi.web.nhl.com{game["teams"]["away"]["team"]["link"]}')
    hr = home_request.json()
    ar = away_request.json()
    homeAbbr = hr['teams'][0]['abbreviation']
    awayAbbr = ar['teams'][0]['abbreviation']
    return {'home': {'name': homeName, 'abbreviation': homeAbbr}, 'away': {'name': awayName, 'abbreviation': awayAbbr}}


def hatTricks(season: str):
    API_URL = f"https://statsapi.web.nhl.com/api/v1/schedule?season={season}&expand=schedule.boxscore"
    response = requests.get(API_URL, params={"Content-Type": "application/json"})
    data = response.json()

    parent_dir = "C:\\Users\\Owner\\Dropbox\\Python Projects\\NHL\\Seasons"
    season = season[0:4] + "-" + season[6:]  # Format season like 2019-20
    season_path = os.path.join(parent_dir, season)
    try:  # Make season folder if it doesn't exist
        os.mkdir(season_path)
    except FileExistsError:
        pass
    count = 0
    first = ""
    last = ""
    for item in data['dates']:  # Iterate through each date in the season
        for game in item['games']:  # Iterate through each game on the date
            if game['gameType'] == "R":  # Check regular season games only
                teams = ['home', 'away']
                # Ignore the game if a hat trick isn't possible
                if game['teams']['home']['score'] < 3 and game['teams']['away']['score'] < 3:
                    continue

                date = game['gameDate']
                newDate = datetime.datetime.strptime(date, '%Y-%m-%dT%H:%M:%SZ')
                estTimeDelta = datetime.timedelta(hours=-5)
                estTime = datetime.timezone(estTimeDelta, name="EST")
                newDate = newDate.replace(tzinfo=timezone.utc).astimezone(tz=estTime)  # Convert to EST
                date = newDate.strftime('%B %d')  # [month] [day] such as October 9
                if date[-2] == "0":  # Remove leading zeros
                    date = date[:-2] + date[-1]

                # Get boxscore
                request = requests.get(f"https://statsapi.web.nhl.com/api/v1/game/{game['gamePk']}/boxscore",
                                       params={"Content-Type": "application/json"})
                boxScore = request.json()

                for team in teams:
                    total_goals = game['teams'][team]['score']
                    if total_goals < 3:
                        continue
                    players = getPlayers(boxScore, team)
                    for player in players:
                        if total_goals < 3:  # End search if hat tricks are no longer possible
                            break
                        playerName = players[player]['person']['fullName']
                        try:
                            playerGoals = players[player]['stats']['skaterStats']['goals']
                            total_goals -= playerGoals  # Reduce hat trick possibilities
                            if playerGoals >= 3:
                                teamNames = getTeamNames(game)
                                forTeam = teamNames[team]
                                againstTeam = teamNames[teams[teams.index(team) - 1]]
                                gameLink = f"https://www.nhl.com/gamecenter/{game['gamePk']}"

                                # Create team folders within season if they don't already exist
                                for_path = os.path.join(season_path, forTeam['name'])
                                against_path = os.path.join(season_path, againstTeam['name'])
                                if not os.path.exists(for_path):
                                    os.mkdir(os.path.join(season_path, forTeam['name']))
                                if not os.path.exists(against_path):
                                    os.mkdir(against_path)

                                # Get paths for hat tricks for/against text files
                                for_path = os.path.join(season_path, forTeam["name"], 'for')
                                against_path = os.path.join(season_path, againstTeam["name"], 'against')

                                # Append to Hat Tricks Against file
                                against_file = open(f'{against_path}.txt', 'a+')
                                for hatty in range(playerGoals//3):  # Account for 6+ goals
                                    against_file.write(f'{date} - [{forTeam["abbreviation"]}] {playerName}\n'
                                                       f'{gameLink}\n')
                                against_file.close()

                                # Append to Hat Tricks For file
                                for_file = open(f'{for_path}.txt', 'a+')
                                for hatty in range(playerGoals//3):  # Account for 6+ goals
                                    for_file.write(f'{date} - {playerName}\n'
                                                   f'{gameLink}\n')
                                for_file.close()
                                if count == 0:
                                    first = f'{date} \t [{forTeam["name"]}] {playerName}: {playerGoals} \t ' \
                                            f'Against: {againstTeam["abbreviation"]}'
                                count += 1
                                last = f'{date} \t [{forTeam["name"]}] {playerName}: {playerGoals} \t ' \
                                       f'Against: {againstTeam["abbreviation"]}'
                                # print(f'{date} \t [{forTeam["name"]}] {playerName}: {playerGoals} \t '
                                #      f'Against: {againstTeam["abbreviation"]}')
                        except KeyError:
                            continue
                        except FileExistsError:
                            pass
    print(f'{season}: {count} hat tricks')
    print(f'First: {first}')
    print(f'Last: {last}\n')


seasons = []
start = 1994
end = 1917
while start > end:
    seasons.append(f'{start-1}{start}')
    start -= 1

for season in seasons:
    begin = time.perf_counter_ns()
    hatTricks(season)
    stop = time.perf_counter_ns()
    # print(f'{(stop-begin)/1000000000} seconds\n')
