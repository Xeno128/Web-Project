from flask import *
from classes import *
import pyrebase
import requests

firebaseConfig = {
  "apiKey": "AIzaSyCKRxeLwSq9giQXpo7pOQ-UaAy4i_UfFZQ",
  "authDomain": "football-stats-7d1b2.firebaseapp.com",
  "databaseURL": "https://football-stats-7d1b2-default-rtdb.firebaseio.com",
  "projectId": "football-stats-7d1b2",
  "storageBucket": "football-stats-7d1b2.appspot.com",
  "messagingSenderId": "419599850111",
  "appId": "1:419599850111:web:5724fff9a527ec7ac37d4a",
  "measurementId": "G-N7L05EM3XD"
};

#api headers
headers = {
	"X-RapidAPI-Key": "6e71f3c849b6b6ed48729a6a9c7272f4",
	"X-RapidAPI-Host": "https://v3.football.api-sports.io/"
}

player_url = "https://v3.football.api-sports.io/players"

# initializing firebase database
firebase = pyrebase.initialize_app(firebaseConfig)
db = firebase.database()

# player = Player(85, "https://media-1.api-sports.io/football/teams/160.png", "Paris Saint Germain", 278, "K. Mbapp\u00e9", "https://media-1.api-sports.io/football/players/125.png", 25, "178 cm", "75 kg", "Attacker", "France", 252, 163, "100 Out Of 153", 182, 12, 2)
# db.child("players").child(player.player_id).set(player.player_to_dict())
# db.child("teams").child(player.team_id).set(player.team_to_dict())

app = Flask(__name__)
app.secret_key = '3d6f45a5fc12445dbac2f59c3b6c7cb1'
app.static_folder = 'static'

# accepts json response
def translate_response(response: dict):
    
    appearences = 0
    goals = 0
    pen_missed = 0
    pen_scored = 0
    assists = 0
    yellows = 0
    reds = 0
    goals_conceded = 0
    saves = 0
    pen_saves = 0
    for i in response['response'][0]['statistics']:
        if i['games']['appearences'] != None: appearences += i['games']['appearences']
        if i['goals']['total'] != None: goals += i['goals']['total']
        if i['penalty']['missed'] != None: pen_missed += i['penalty']['missed']
        if i['penalty']['scored'] != None: pen_scored += i['penalty']['scored']
        if i['goals']['assists'] != None: assists += i['goals']['assists']
        if i['cards']['yellow'] != None: yellows += i['cards']['yellow']
        if i['cards']['yellowred'] != None: yellows += i['cards']['yellowred']*2
        if i['cards']['red'] != None: reds += i['cards']['red']
        if i['goals']['conceded'] != None: goals_conceded += i['goals']['conceded']
        if i['goals']['saves'] != None: saves += i['goals']['saves']
        if i['penalty']['saved'] != None: pen_saves += i['penalty']['saved']
    
    
    player = Player(response['response'][0]['statistics'][0]['team']['id'], 
                    response['response'][0]['statistics'][0]['team']['logo'],
                    response['response'][0]['statistics'][0]['team']['name'],
                    response['response'][0]['player']['id'],
                    response['response'][0]['player']['name'],
                    response['response'][0]['player']['photo'],
                    response['response'][0]['player']['age'],
                    response['response'][0]['player']['height'],
                    response['response'][0]['player']['weight'],
                    response['response'][0]['statistics'][0]['games']['position'],
                    response['response'][0]['player']['nationality'],
                    appearences,
                    goals,
                    f'{pen_scored} Out Of {pen_scored+pen_missed}',
                    assists,
                    yellows,
                    reds,
                    goals_conceded,
                    saves,
                    pen_saves       
    )
    return player

# accepts player object
def check_data(obj: Player):
    try:
        db.child("players").child(obj.player_id).get()
        db.child("players").child(obj.player_id).update(obj.player_to_dict())
    except:
        db.child("players").child(obj.player_id).set(obj.player_to_dict())
        
    try:
        db.child("teams").child(obj.team_id).get()
        db.child("teams").child(obj.team_id).update(obj.team_to_dict())
    except:
        db.child("teams").child(obj.team_id).set(obj.team_to_dict())

# accepts player object
def get_data(obj: Player):
    try:
        player = db.child("players").child(obj.player_id).get()
        team = db.child("teams").child(obj.team_id).get()
    except:
        raise Exception("Cant Get Data")
    return player.val(), team.val()
    

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/select/")
def select():
    return render_template("select.html")

@app.route("/search/", methods=["POST", "GET"])
def search():
    if request.method == "POST":
        queue = request.form['nm']
        league = request.args.get("id")
        return redirect(url_for("psearch", league_id=league, player_name=queue))
    else:
        return render_template("search.html")    

@app.route("/player-search/<league_id>/<player_name>") 
def psearch(player_name, league_id):
    player_quarystring= {"search":player_name, "league":league_id}
    player_response = requests.get(player_url, headers=headers, params=player_quarystring)
    
    if player_response.json()['results'] == 0:
        return "<h1>Player Not Found!</h1>"
    
    player_obj = translate_response(player_response.json())

    try:
        check_data(player_obj)
        player, team = get_data(player_obj)
    except:
        return "<h1>Error</h1>"
    return render_template("player.html", player=player, team=team)


if __name__ == "__main__":
    app.run(debug=True)