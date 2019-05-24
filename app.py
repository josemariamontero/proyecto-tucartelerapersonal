from flask import Flask, render_template, url_for, request, redirect, session
import requests
import json
import os
from requests_oauthlib import OAuth1
from requests_oauthlib import OAuth2Session
from urllib.parse import parse_qs

app = Flask(__name__)
key = os.environ["key"]
url_base = "https://api.themoviedb.org/3"
app.secret_key= 'eYEzl2yhmWQ2ChUJ8KeyZ9IvbbL7TLtp5U4YwRITB1ejg'

REQUEST_TOKEN_URL = "https://api.twitter.com/oauth/request_token"
AUTHENTICATE_URL = "https://api.twitter.com/oauth/authenticate?oauth_token="
ACCESS_TOKEN_URL = "https://api.twitter.com/oauth/access_token"

@app.route('/',methods=["GET","POST"])
@app.route('/<page>')
def inicio(page=1):
    payload = {"api_key":key,"language":"es-ES","page":page}
    r = requests.get(url_base+"/movie/now_playing",params=payload)
    if r.status_code == 200:
        doc = r.json()
        novedades = doc["results"]
    return render_template("inicio.html",novedades=novedades,page=int(page)+1)
    
@app.route('/busquedaseries',methods=["GET","POST"])
def series():
    series = request.form.get('serie')
    payload3 = {"api_key":key,"language":"es-ES","query":series}
    r3 = requests.get(url_base+"/search/tv",params=payload3)
    if r3.status_code == 200:
        doc3 = r3.json()
        series = doc3["results"]
    return render_template("series.html",series=series)

        
@app.route('/busquedapeliculas',methods=["GET","POST"])
def peliculas():
    peliculas = request.form.get('pelicula')
    payload2 = {"api_key":key,"language":"es-ES","query":peliculas}
    r2 = requests.get(url_base+"/search/movie",params=payload2)
    if r2.status_code == 200:
        doc2 = r2.json()
        peliculas = doc2["results"]
    return render_template("peliculas.html",peliculas=peliculas)

def get_request_token_oauth1():
    oauth = OAuth1(os.environ["CONSUMER_KEY"],
                  client_secret=os.environ["CONSUMER_SECRET"])
    r = requests.post(url=REQUEST_TOKEN_URL, auth=oauth)
    credentials = parse_qs(r.content)
    return credentials.get(b'oauth_token')[0],credentials.get(b'oauth_token_secret')[0]

def get_access_token_oauth1(request_token,request_token_secret,verifier):
    oauth = OAuth1(os.environ["CONSUMER_KEY"],
                   client_secret=os.environ["CONSUMER_SECRET"],
                   resource_owner_key=request_token,
                   resource_owner_secret=request_token_secret,
                   verifier=verifier,)


    r = requests.post(url=ACCESS_TOKEN_URL, auth=oauth)
    credentials = parse_qs(r.content)
    return credentials.get(b'oauth_token')[0],credentials.get(b'oauth_token_secret')[0]

@app.route('/twitter')
def twitter():
    request_token,request_token_secret = get_request_token_oauth1()
    authorize_url = AUTHENTICATE_URL + request_token.decode("utf-8")
    session["request_token"]=request_token.decode("utf-8")
    session["request_token_secret"]=request_token_secret.decode("utf-8")
    return redirect(authorize_url)

@app.route('/callback')
def twitter_callback():
    request_token=session["request_token"]
    request_token_secret=session["request_token_secret"]
    verifier  = request.args.get("oauth_verifier")
    access_token,access_token_secret= get_access_token_oauth1(request_token,request_token_secret,verifier)
    session["access_token"]= access_token.decode("utf-8")
    session["access_token_secret"]= access_token_secret.decode("utf-8")
    return redirect('/twittear')

@app.route('/twittear')
def vertweet():
    access_token=session["access_token"]
    access_token_secret=session["access_token_secret"]
    oauth = OAuth1(os.environ["CONSUMER_KEY"],
                   client_secret=os.environ["CONSUMER_SECRET"],
                   resource_owner_key=access_token,
                   resource_owner_secret=access_token_secret)
    url = 'https://api.twitter.com/1.1/statuses/update.json'
    payload={"status":"Si necesitas conocer información sobre películas visita ésta página web: https://tucartelerapersonal.herokuapp.com."}
    r = requests.post(url=url,auth=oauth,params=payload)
    if r.status_code==200:
        return render_template("twittear.html",datos=r.json())
    else:
        return redirect("/twitter")  

redirect_uri_sp = 'https://tucartelerapersonal.com/spotify_callback'
scope_sp = 'user-read-private user-read-email'
token_url_sp = "https://accounts.spotify.com/api/token"

def token_valido_spotify():
    try:
        token=json.loads(session["token_sp"])
    except:
        token = False
    if token:
        token_ok = True
        try:
            oauth2 = OAuth2Session(os.environ["client_id_spotify"], token=token)
            r = oauth2.get('https://api.spotify.com/v1/me')
        except TokenExpiredError as e:
            token_ok = False
    else:
        token_ok = False
    return token_ok

@app.route('/spotify')
def spotify():
    return render_template("spotify.html")

@app.route('/perfil_spotify')
def info_perfil_spotify():
  if token_valido_spotify():
    return redirect("/perfil_usuario_spotify")
  else:
    oauth2 = OAuth2Session(os.environ["client_id_spotify"], redirect_uri=redirect_uri_sp,scope=scope_sp)
    authorization_url, state = oauth2.authorization_url('https://accounts.spotify.com/authorize')
    session.pop("token_sp",None)
    session["oauth_state_sp"]=state
    return redirect(authorization_url) 

@app.route('/spotify_callback')
def get_token_spotify():
    oauth2 = OAuth2Session(os.environ["client_id_spotify"], state=session["oauth_state_sp"],redirect_uri=redirect_uri_sp)
    print (request.url)
    token = oauth2.fetch_token(token_url_sp, client_secret=os.environ["client_secret_spotify"],authorization_response=request.url[:4]+"s"+request.url[4:])
    session["token_sp"]=json.dumps(token)
    return redirect("/perfil_usuario_spotify")


@app.route('/perfil_usuario_spotify')
def info_perfil_usuario_spotify():
    if token_valido_spotify():
        token=json.loads(session["token_sp"])
        oauth2 = OAuth2Session(os.environ["client_id_spotify"], token=token)
        r = oauth2.get('https://api.spotify.com/v1/me')
        doc=json.loads(r.content.decode("utf-8"))
        return render_template("perfil_spotify.html", datos=doc)
    else:
        return redirect('/perfil')

@app.route('/logout_spotify')
def salir_spotify():
    session.pop("token_sp",None)
    return redirect("/spotify")

if __name__ == '__main__':
    port=os.environ["PORT"]
    app.run('0.0.0.0',int(port),debug=True)