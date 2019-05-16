from flask import Flask, render_template, request
import requests
import json
import os

app = Flask(__name__)
key = os.environ["key"]
url_base = "https://api.themoviedb.org/3"

@app.route('/',methods=["GET","POST"])
@app.route('/<page>')
def inicio(page=1):
	payload = {"api_key":key,"language":"es-ES","page":page}
	r = requests.get(url_base+"/movie/popular",params=payload)
	if r.status_code == 200:
		doc = r.json()
		novedades = doc["results"]
	return render_template("inicio.html",novedades=novedades,page=int(page)+1)

@app.route('/busquedapeliculas',methods=["GET","POST"])
def peliculas():
	peliculas = request.form.get('pelicula')
	payload2 = {"api_key":key,"language":"es-ES","query":peliculas}
	r2 = requests.get(url_base+"/search/movie",params=payload2)
	if r2.status_code == 200:
		doc2 = r2.json()
		peliculas = doc2["results"]
	return render_template("peliculas.html",peliculas=peliculas)

@app.route('/busquedaseries',methods=["GET","POST"])
def series():
	series = request.form.get('serie')
	payload3 = {"api_key":key,"language":"es-ES","query":series}
	r3 = requests.get(url_base+"/search/tv",params=payload3)
	if r3.status_code == 200:
		doc3 = r3.json()
		series = doc3["results"]
	return render_template("series.html",series=series)
		

if __name__ == '__main__':
	port=os.environ["PORT"]
	app.run('0.0.0.0',int(port),debug=True)