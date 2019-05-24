from flask import Flask, render_template, url_for, request, redirect, session
import requests
import json
import os
from requests_oauthlib import OAuth1
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
    twitter = request.form.get('twittear')
    url = 'https://api.twitter.com/1.1/statuses/update.json'
    payload={"status":twitter}
    r = requests.post(url=url,auth=oauth,params=payload)
    if r.status_code==200:
        return render_template("twittear.html",datos=r.json())
    else:
        return redirect("/twitter")
  

if __name__ == '__main__':
    port=os.environ["PORT"]
    app.run('0.0.0.0',int(port),debug=True)