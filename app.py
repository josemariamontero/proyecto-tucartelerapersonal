from flask import Flask, render_template, request
import os

app = Flask(__name__)
key = os.envion["key"]
url_base = "https://api.themoviedb.org/3"
payload = {"api_key":"key","language":"es-ES","query":pelicula}

@app.route('/busquedapeliculas',methods=["GET","POST"])
def peliculas():
	peliculas = request.form.get('pelicula')
	r = requests.get(url_base+"/search/movie/",params=payload)
	if r.status_code == 200:
		doc = r.json()
		peliculas = doc["results"]
		return render_template("peliculas.html",peliculas=peliculas)
		
