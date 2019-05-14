from flask import Flask, render_template, request
import requests
import json
import os

app = Flask(__name__)
key = os.environ["key"]
url_base = "https://api.themoviedb.org/3"

@app.route('/',methods=["GET","POST"])
def inicio():
	payload = {"api_key":"key","language":"es-ES"}
	r = requests.get(url_base+"/movie/popular",params=payload)
	if r.status_code == 200:
		doc = r.json()
		novedades = doc["results"]
	return render_template("inicio.html")

@app.route('/busquedapeliculas',methods=["GET","POST"])
def peliculas():
	peliculas = request.form.get('pelicula')
	payload2 = {"api_key":"key","language":"es-ES","query":peliculas}
	r2 = requests.get(url_base+"/search/movie/",params=payload2)
	if r2.status_code == 200:
		doc2 = r2.json()
		peliculas = doc2["results"]
		return render_template("peliculas.html",peliculas=peliculas)
		

if __name__ == '__main__':
	port=os.environ["PORT"]
	app.run('0.0.0.0',int(port),debug=True)