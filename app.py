from flask import *
from classes import *
import random
import pyrebase
from flask_apscheduler import APScheduler
from flask_login import *
import cv2

#for file removal
import os

#location
import geocoder

#async
import aiohttp
import asyncio

firebaseConfig = {
  "apiKey": "AIzaSyCKRxeLwSq9giQXpo7pOQ-UaAy4i_UfFZQ",
  "authDomain": "football-stats-7d1b2.firebaseapp.com",
  "databaseURL": "https://football-stats-7d1b2-default-rtdb.firebaseio.com",
  "projectId": "football-stats-7d1b2",
  "storageBucket": "football-stats-7d1b2.appspot.com",
  "messagingSenderId": "419599850111",
  "appId": "1:419599850111:web:5724fff9a527ec7ac37d4a",
  "measurementId": "G-N7L05EM3XD",
  "serviceAccount": "static/firebase-key.json"
}

# api headers
headers = {
	"X-RapidAPI-Key": "6e71f3c849b6b6ed48729a6a9c7272f4",
	"X-RapidAPI-Host": "https://v3.football.api-sports.io/"
}

# initializing firebase database
firebase = pyrebase.initialize_app(firebaseConfig)
db = firebase.database()
storage = firebase.storage()

# flask startup
app = Flask(__name__)
app.secret_key = '3d6f45a5fc12445dbac2f59c3b6c7cb1'
app.static_folder = 'static'

# scheduler startup
scheduler = APScheduler()
scheduler.api_enabled = False
scheduler.init_app(app)

# scheduler on/off switch for debug
on_switch = False

# login manager startup
login_manager = LoginManager()
login_manager.login_view = 'login'
login_manager.init_app(app)

@login_manager.user_loader
def load_user(username):
    user_db = dict(db.child('users').child(username).get().val())
    user = build_user(user_db['username'], user_db['password'], user_db['location'], user_db['photo'])
    return user

# league names by id
league_names = {"78": "Bundesliga", "39": "Premier League", "61": "Ligue 1", "140": "La Liga", "135": "Serie A", "88": "Eredivisie", "383": "Ligat Ha'al", "382": "Liga Leumit"}

@scheduler.task('interval', id='update_database', seconds=300)
def job1():
    league_ids = [78, 39, 61, 140, 135, 88, 383, 382]
    
    player_response = asyncio.run(RequestRandomPlayers(league_ids[random.randint(0, len(league_ids)-1)]))
    
    if player_response['results'] == 0:
        return
    
    player_obj = translate_response(player_response, index=random.randint(0, len(player_response['response'])-1))

    try:
        check_data(player_obj)
        print('Successfuly Updated The Database With The Player: '+player_obj.player_name)
    except:
        print("Error Loading Player Into Database Asynchronously. Continuing")
        return

# asynchronous function for making a request
async def RequestPlayer(player_name, league_id):

    async with aiohttp.ClientSession() as session:

        player_url = "https://v3.football.api-sports.io/players"
        player_quarystring = {"search":player_name, "league":league_id}
        
        async with session.get(player_url, headers=headers, params=player_quarystring) as resp:
            player = await resp.json()
            return player

async def RequestRandomPlayers(league_id):

    async with aiohttp.ClientSession() as session:

        player_url = "https://v3.football.api-sports.io/players"
        player_quarystring = {"league":league_id, "season": "2023"}
        
        async with session.get(player_url, headers=headers, params=player_quarystring) as resp:
            players = await resp.json()
            return players

# accepts json response
def translate_response(response: dict, index = 0):
    
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
    for i in response['response'][index]['statistics']:
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
    
    
    player = Player(response['response'][index]['statistics'][0]['team']['id'], 
                    response['response'][index]['statistics'][0]['team']['logo'],
                    response['response'][index]['statistics'][0]['team']['name'],
                    response['response'][index]['player']['id'],
                    response['response'][index]['player']['name'],
                    response['response'][index]['player']['photo'],
                    response['response'][index]['player']['age'],
                    response['response'][index]['player']['height'],
                    response['response'][index]['player']['weight'],
                    response['response'][index]['statistics'][0]['games']['position'],
                    response['response'][index]['player']['nationality'],
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

def gen(camera):
    try:
        success, image = camera.read()
    except:
        return "Camera Not Detected!"
        
    return image

def build_user(username, password, location, photo):
    user = Users(username, password, location, photo)
    return user

def insert_user(user: Users):
    db.child('users').child(user.username).set(user.user_to_dict())

def update_user(user: Users):
    db.child('users').child(user.username).update(user.user_to_dict())

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

def check_user(username: str):
    try:
        if db.child("users").child(username).get().val() != None:
            return True
        else:
            return False
    except:
        return False

def check_credentials(user: Users):
    try:
        if dict(db.child("users").child(user.username).get().val())['password'] == user.password:
            return True
        else: 
            return False
    except:
        return False

def update_storage(image, username):
    try:
        storage.child(f'profiles/{username}.jpg').put(image)
        return storage.child(f'profiles/{username}.jpg').get_url(None)
    except:
        return "Error Inserting the Profile Pic"

# accepts player object
def get_data(obj: Player):
    try:
        player = db.child("players").child(obj.player_id).get()
        team = db.child("teams").child(obj.team_id).get()
    except:
        raise Exception("Cant Get Data")
    return player.val(), team.val()

def validate_input(text: str):
    final = text
    if final.count(' ') > 0:
        final = text.split(' ')[1]
    return final


@app.route("/")
def home():
    return render_template("index.html")

@app.route("/select/")
def select():
    return render_template("select.html")

@app.route("/search/", methods=["POST", "GET"])
def search():
    league = request.args.get("id")
    if league not in league_names.keys(): return "<h1>Incorrect League ID!</h1>"
    
    if request.method == "POST":
        queue = request.form['nm']
        fixed_queue = validate_input(queue)
        return redirect(url_for("psearch", league_id=league, player_name=fixed_queue))
    else:
        return render_template("search.html", league_name=league_names[league])    

@app.route("/player-search/<league_id>/<player_name>") 
def psearch(player_name, league_id):
    player_response = asyncio.run(RequestPlayer(player_name, league_id))
    
    if player_response['results'] == 0:
        return "<h1>Player Not Found!</h1>"
    
    player_obj = translate_response(player_response)

    try:
        check_data(player_obj)
        player, team = get_data(player_obj)
    except:
        return "<h1>Error</h1>"
    return render_template("player.html", player=player, team=team)

@app.route("/signup", methods=["POST", "GET"])
def signup():
    if request.method == 'POST':
        username = request.form.get('username')
        if check_user(username):
            flash('This Username already exists')
            return redirect(url_for('signup'))
        
        password = request.form.get('password')
        
        if request.remote_addr == '127.0.0.1':
            location_obj = geocoder.ip('me')
        else:
            location_obj = geocoder.ip(request.remote_addr)
            
        if location_obj == None:
            location = ""
        else:  
            location = f"{location_obj.country}, {location_obj.city}"
            
        user = build_user(username, password, location, 'None')
        insert_user(user)
        return redirect(url_for('login'))
    else:      
        return render_template('sign-up.html')

@app.route("/login", methods=["POST", "GET"])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = build_user(username, password, '', '')
        
        if check_user(username) and check_credentials(user):
            remember = True if request.form.get('remember') else False
            login_user(user, remember=remember)
            return redirect(url_for('profile'))
        else:
            flash('One Or More Of The Entered Was Incorrect. Please Try Again')
            return redirect(url_for('login')) 
    else:
        return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))

@app.route("/profile")
@login_required
def profile():
    return render_template('profile.html', user=current_user)

@app.route("/set-picture", methods=["POST", "GET"])
@login_required
def setPic():
    camera = cv2.VideoCapture(0, cv2.CAP_DSHOW)
    if request.method == 'POST':
        pic = gen(camera)
        path = f'static/img/tmp/{current_user.username}.jpg'
        cv2.imwrite(path, pic)
        
        url = update_storage(path, current_user.username)
        new_user = Users(current_user.username, current_user.password, current_user.location, str(url))
        update_user(new_user)
        camera.release()
        
        os.remove(path)
        return redirect(url_for('logout'))
    else:
        return render_template('set_pic.html')

if __name__ == "__main__":
    if on_switch: scheduler.start()
    app.run(debug=False)