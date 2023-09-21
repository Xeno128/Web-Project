import flask
import os

app = flask.Flask(__name__)
app.static_folder = 'static'

@app.route("/")
def home():
    return flask.render_template("index.html")

@app.route("/select/")
def select():
    return flask.render_template("select.html")

@app.route("/search/")
def search():
    
    q = flask.request.args.get('q')
    league_id = flask.request.args.get('id')
    if q: print(q)
    if r: print(league_id)
    
    return flask.render_template("search.html")


if __name__ == "__main__":
    app.run(debug=True)