from flask import *
from classes import *
import pyrebase

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

# initializing firebase database
firebase = pyrebase.initialize_app(firebaseConfig)
db = firebase.database()

# db.child("players").child(player.player_id).set(player.player_to_dict())
# db.child("teams").child(player.team_name).set(player.team_to_dict())

app = Flask(__name__)
app.secret_key = '3d6f45a5fc12445dbac2f59c3b6c7cb1'
app.static_folder = 'static'

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
        return redirect(url_for("psearch", id=queue))
    else:
        return render_template("search.html")    

@app.route("/player-search/<id>") 
def psearch(id):
    player = Player(85, "https://media-1.api-sports.io/football/teams/160.png", "Paris Saint Germain", 278, "K. Mbapp\u00e9", "https://media-1.api-sports.io/football/players/125.png", 25, "178 cm", "75 kg", "Attacker", "France", 252, 163, "100 Out Of 153", 182, 12, 2)
    return render_template("player.html", player=player)


if __name__ == "__main__":
    app.run(debug=True)