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

app.config['BABEL_DEFAULT_LOCALE'] = 'en'
babel = Babel(app)

@app.route('/')
@cache.cached(timeout=Config.timeout)
def index():
    '''
    Funkcija poziva funkciju genre bez id parametra za prikaz svih žanrova

    :return: genre('')
   
    '''    
    return genre('')

@app.route('/<id>')
@cache.cached(timeout=Config.timeout)
def genre(id):
    '''
    Funkcija dohvaća JSON objekt sa Openwhyd API servisa prema id-u oznake žanra i formatira ga za prikaz

    :param str id: Oznaka žanra
    :return: Stranica index.html sa jsonMusic objektom
   
    '''    

    app.logger.info("Pozvan žanr sa oznakom: "+id)

    parameters = { 'format': 'json', 'limit': Config.limit}

    response = requests.get(Config.allURL + id, params=parameters)
 
    jsonMusic = response.json()

    for music in jsonMusic["tracks"]:

        if (music["eId"].startswith('/sc/')) or (music["eId"].startswith('/vi/')):
               jsonMusic["tracks"].remove(music)
        
        music["eId"] = music["eId"].replace('/yt/','')
        if (music["rankIncr"] == None):
               music["rankIncr"] = ""
      
    return render_template('index.html', jsonMusic=jsonMusic)

@app.route("/user/<userId>")
@cache.cached(timeout=Config.timeout)
def user(userId):
    '''
    Funkcija dohvaća JSON objekt sa Openwhyd API servisa prema id-u korisnika i formatira ga za prikaz

    :param int userId: Oznaka korisnika
    :return: Stranica user.html sa user objektom
    
    '''    
    
    app.logger.info("Pozvan user sa oznakom: "+userId)
   
    parameters = { 'format': 'json', 'limit': Config.limit}
 
    response = requests.get(Config.userURL + userId, params=parameters)
    
    user = response.json()

    for music in user:
        if (music["eId"].startswith('/sc/')) or (music["eId"].startswith('/vi/')):
                user.remove(music)
        
        music["eId"] = music["eId"].replace('/yt/','')
        
    return render_template("user.html", user=user)

@app.route("/search", methods=['GET', 'POST'])
@cache.cached(timeout=Config.timeout)
def search():
    '''
    Funkcija dohvaća JSON objekt sa Openwhyd API servisa prema unosu query parametra i formatira ga za prikaz

    :return: Stranica search.html sa search objektom
   
    '''    

    query = request.args.get('query')

    app.logger.info("Pozvano pretraživanje sa parametrom: "+query)

    if (query!=""):

        parameters = { 'context': 'addTrack', 'q': query, 'limit': Config.limit, 'format': 'json' }

        response = requests.get(Config.searchURL, params=parameters)

        search = response.json()

        for music in search:
            if (music["eId"].startswith('/sc/')) or (music["eId"].startswith('/vi/')):
                    search.remove(music)
        
            music["eId"] = music["eId"].replace('/yt/','')
    
        return render_template("search.html", search=search)    

    else:

        return redirect(url_for('index'))

@babel.localeselector
def get_locale():
    if request.args.get('lang'):
        session['lang'] = request.args.get('lang')
    return session.get('lang', 'en')

if __name__ == "__main__":

    formatter = logging.Formatter("[%(asctime)s] {%(pathname)s:%(lineno)d} %(levelname)s - %(message)s")
    handler = logging.FileHandler('openwhydApp.log')
    handler.setLevel(logging.INFO)
    handler.setFormatter(formatter)
    app.logger.addHandler(handler)

    app.run()

