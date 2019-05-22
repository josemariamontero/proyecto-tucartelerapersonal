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

@app.route('/busquedageneros',methods=["GET","POST"])
def generos():
	generos = request.form.get('generos')
	payload4 = {"api_key":key,"language":"es-ES"}
	r4 = requests.get(url_base+"/genre/movie/list",params=payload4)
	if r4.status_code == 200:
		doc4 = r4.json()
		generos = doc4["genres"]
	return render_template("generos.html",generos=generos)
		
@app.route('/busquedapeliculas',methods=["GET","POST"])
def peliculas():
	peliculas = request.form.get('pelicula')
	payload2 = {"api_key":key,"language":"es-ES","query":peliculas}
	r2 = requests.get(url_base+"/search/movie",params=payload2)
	if r2.status_code == 200:
		doc2 = r2.json()
		peliculas = doc2["results"]
	return render_template("peliculas.html",peliculas=peliculas)

if __name__ == '__main__':
	port=os.environ["PORT"]
	app.run('0.0.0.0',int(port),debug=True)