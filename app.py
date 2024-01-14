from dotenv import load_dotenv
import os
import requests
import json
from flask import Flask, redirect, session, jsonify, request, render_template
import urllib.parse
from datetime import datetime

load_dotenv()

app = Flask(__name__)
app.secret_key = "12b8b2851ff21b44a8515393498225ca214677b77059d74d248c1c816f6ddbfa"

AUTH_URL = "https://accounts.spotify.com/authorize"
TOKEN_URL = "https://accounts.spotify.com/api/token"
API_BASE_URL = "https://api.spotify.com/v1/"
REDIRECT_URI = "http://localhost:5000/callback"

CLIENT_ID = "eb688df0e6ff4e64bb26a196747e78a8"
CLIENT_SECRET = "291743cfeb2e4eaa81c812ba3eaae20b"

client_id = os.getenv("CLIENT_ID")
client_secret = os.getenv("CLIENT_SECRET")

@app.route('/')
def index():
    #return "<a href='/login'>log in with spotify</a>"
    print("hello")
    return render_template('index.html')

@app.route('/login')
def login():
    scope = 'user-read-private user-read-email'

    parameters = {
        'client_id': CLIENT_ID, 
        'response_type': 'code', 
        'scope': scope, 
        'redirect_uri': REDIRECT_URI, 
        'show_dialog': True
    }

    auth_url = f"{AUTH_URL}?{urllib.parse.urlencode(parameters)}"
    
    return redirect(auth_url)


@app.route('/callback')
def callback():
    if 'error' in request.args:

        #! return error message

        return jsonify({"error": request.args["error"]})
    
    if 'code' in request.args:
        req = {
            'code': request.args['code'], 
            'grant_type': 'authorization_code', 
            'redirect_uri': REDIRECT_URI, 
            'client_id': CLIENT_ID, 
            'client_secret': CLIENT_SECRET
        }

        response = requests.post(TOKEN_URL, data=req)

        token_info = response.json()

        session['access_token'] = token_info['access_token']
        session['refresh_token'] = token_info['refresh_token']
        session['expire_date'] = datetime.now().timestamp() + token_info["expires_in"]

        #return redirect('/playlists')

        return redirect('/find_songs')
    

@app.route('/find_songs')
def find_songs():
    if 'access_token' not in session:
        return redirect('/login')
    
    if datetime.now().timestamp() > session["expire_date"]:
        return redirect ('/refresh_token')
    
    headers = {
        'Authorization': f"Bearer {session['access_token']}"
    }

    response = requests.get(API_BASE_URL + 'me/playlists', headers=headers)

    playlists = response.json()

    playlists = playlists['items']

    user_playlists = []

    for i in range(len(playlists)):
        playlist = {}
        playlist['track_routes'] = playlists[i]['tracks']['href']
        playlist['cover'] = playlists[i]['images'][0]['url']
        playlist['title'] = playlists[i]['name']
        user_playlists.append(playlist)

    #-------------------------
    
    #tracks_details = requests.get(user_playlists[0]['track_routes'], headers=headers)
    #tracks_details = tracks_details.json()
    #tracks_details = tracks_details['items']

    #tracks = []

    #!

    #return render_template(, playlists=user_playlists)


@app.route('/get_album_tracks')
def get_album_tracks():
    if 'access_token' not in session:
        return redirect('/login')
    
    if datetime.now().timestamp() > session["expire_date"]:
        return redirect ('/refresh_token')
    
    headers = {
        'Authorization': f"Bearer {session['access_token']}"
    }

    #! get selected playlist
    playlist = request.form.get()

    tracks_details = requests.get(playlist, headers=headers)
    tracks_details = tracks_details.json()
    tracks_details = tracks_details['items']

    tracks = []

    for i in range(len(tracks_details)):
        tracks.append(tracks_details['items'][i]['track']['name'])

    return 1


@app.route('/refresh_token')
def refresh_token():
    if 'refresh_token' not in session:
        return redirect('/login')
    
    if datetime.now().timetamp() > session('expire_date'):
        req = {
            'grant_type': 'refresh_token', 
            'refresh_token': session["refresh_token"],
            'client_id': client_id, 
            'client_secret': client_secret
        }

        response = requests.post(TOKEN_URL, data=req)
        refreshed_token_info = response.json()

        session['access_token'] = refreshed_token_info['access_token']
        session['expire_date'] = datetime.now().timestamp() + refreshed_token_info["expires_in"]

        return redirect('/playlists')


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)