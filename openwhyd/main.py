from flask import Flask, render_template, request, redirect, url_for, session
from flask_bootstrap import Bootstrap
import requests
from datetime import datetime
from flask_caching import Cache
from config import Config
from flask_babel import Babel
import logging


app = Flask(__name__)
app.secret_key = 'blabla'
bootstrap = Bootstrap(app)
cache = Cache(app, config={'CACHE_TYPE': 'simple'})

# Prijevod
app.config['BABEL_DEFAULT_LOCALE'] = 'en'
babel = Babel(app)

@app.route('/')
@cache.cached(timeout=Config.timeout)
def index():

    return genre('')

@app.route('/<id>')
@cache.cached(timeout=Config.timeout)
def genre(id):
    
    # Log
    app.logger.info("Pozvan žanr sa oznakom: "+id)

    # Priprema parametara
    parameters = { 'format': 'json', 'limit': Config.limit}
    
    # Poziv REST servisa, HTTP GET
    response = requests.get(Config.allURL + id, params=parameters)
   
    # JSON decoder (http://docs.python-requests.org/en/latest/user/quickstart/#json-response-content)
    jsonMusic = response.json()
  
     # Iteracija kroz JSON objekt i formatiranje podataka za prikaz
    for music in jsonMusic["tracks"]:

        if (music["eId"].startswith('/sc/')) or (music["eId"].startswith('/vi/')):
               jsonMusic["tracks"].remove(music)
        
        music["eId"] = music["eId"].replace('/yt/','')
      
    return render_template('index.html', jsonMusic=jsonMusic)

@app.route("/user/<userId>")
@cache.cached(timeout=Config.timeout)
def user(userId):

    # Log
    app.logger.info("Pozvan user sa oznakom: "+userId)

    # Priprema parametara
    parameters = { 'format': 'json', 'limit': Config.limit}
	
    # Poziv REST servisa, HTTP GET
    response = requests.get(Config.userURL + userId, params=parameters)
	
    # JSON decoder (http://docs.python-requests.org/en/latest/user/quickstart/#json-response-content)
    user = response.json()

    # Iteracija kroz JSON objekt i formatiranje podataka za prikaz
    for music in user:
        if (music["eId"].startswith('/sc/')) or (music["eId"].startswith('/vi/')):
                user.remove(music)
        
        music["eId"] = music["eId"].replace('/yt/','')
 
    return render_template("user.html", user=user)

@app.route("/search", methods=['GET', 'POST'])
@cache.cached(timeout=Config.timeout)
def search():

    # Dohvaćanje query parametra
    query = request.args.get('query')

    # Log
    app.logger.info("Pozvano pretraživanje sa parametrom: "+query)

    # Provjera da li je prazan query
    if (query!=""):
    
	    # Priprema parametara
        parameters = { 'context': 'addTrack', 'q': query, 'limit': Config.limit, 'format': 'json' }
	
	    # Poziv REST servisa, HTTP GET
        response = requests.get(Config.searchURL, params=parameters)
	
	    # JSON decoder (http://docs.python-requests.org/en/latest/user/quickstart/#json-response-content)
        search = response.json()
        
        # Iteracija kroz JSON objekt i formatiranje podataka za prikaz
        for music in search:
            if (music["eId"].startswith('/sc/')) or (music["eId"].startswith('/vi/')):
                    search.remove(music)
        
            music["eId"] = music["eId"].replace('/yt/','')
  
    
        return render_template("search.html", search=search)    

    # Ako je query prazan preusmjeri na index
    else:

        return redirect(url_for('index'))

@babel.localeselector
def get_locale():
    if request.args.get('lang'):
        session['lang'] = request.args.get('lang')
    return session.get('lang', 'en')

if __name__ == "__main__":

    # Loggiranje
    formatter = logging.Formatter("[%(asctime)s] {%(pathname)s:%(lineno)d} %(levelname)s - %(message)s")
    handler = logging.FileHandler('openwhydApp.log')
    handler.setLevel(logging.INFO)
    handler.setFormatter(formatter)
    app.logger.addHandler(handler)

    app.run()

