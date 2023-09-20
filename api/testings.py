import requests
import json

headers = {
	"X-RapidAPI-Key": "6e71f3c849b6b6ed48729a6a9c7272f4",
	"X-RapidAPI-Host": "https://v3.football.api-sports.io/"
}

league_name = input("enter the league name: ")

league_url = "https://v3.football.api-sports.io/leagues"
league_quarystring= {"name":league_name}

league_response = requests.get(league_url, headers=headers, params=league_quarystring)
league_id = league_response.json()["response"][0]["league"]["id"]

player_name = input("enter the player name: ")

player_url = "https://v3.football.api-sports.io/players"
player_quarystring= {"search":player_name, "league":league_id}

player_response = requests.get(player_url, headers=headers, params=player_quarystring)

with open("stats.json", "w") as outfile:
    json.dump(player_response.json(), outfile, indent=4)