from flask import *

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

@app.route("/player-search?uid=<id>") 
def psearch(id):
    return render_template("player.html", player=id)


if __name__ == "__main__":
    app.run(debug=True)