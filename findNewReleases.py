import spotipy
import time
from datetime import date, timedelta, datetime
from spotipy.oauth2 import SpotifyOAuth

from flask import Flask, request, url_for, session, redirect

app = Flask(__name__)

app.config['SESSION_COOKIE_NAME'] = 'Spotify Cookie'
app.secret_key = 'PUT CUSTOM SECRET KEY HERE'
TOKEN_INFO = 'token_info'

@app.route('/')
def login():
    auth_url = create_spotify_oauth().get_authorize_url()
    return redirect(auth_url)

@app.route('/redirect')
def redirect_page():
    session.clear()
    code = request.args.get('code')
    token_info = create_spotify_oauth().get_access_token(code)
    session[TOKEN_INFO] = token_info
    return redirect(url_for('find_new_releases',_external=True))

@app.route('/find-new-releases')
def find_new_releases():
    # gets token or redirects to log in again
    try:
        token_info = get_token()
    except:
        print("User not logged in")
        return redirect('/')
    
    # spotipy object using the access token
    sp = spotipy.Spotify(auth=token_info['access_token'])

 # 1.We need to go through the user's followed artists and save their album information

    # extracts the ids of all following artists
    following = sp.current_user_followed_artists()["artists"]["items"]
    artist_list = []
    for item in following:
        artist_list.append(item["id"])

    # 2-d array to store all the album ids and release dates [[id, date], [id, date]...]
    album_id_date = []

    # iterating through every artist
    for artist_id in artist_list:
        all_artist_albums = sp.artist_albums(artist_id)["items"]

        #looping through every album
        for album in all_artist_albums:

            # saving the artist's ids and release dates
            album_id_date.append([album["id"], album["release_date"]])

 # 2.We need to discard all albums that were not released within the last month

    # the date 30 days ago
    cutoff_date = date.today() - timedelta(days=90)

    # new release album id list
    new_album_ids = []

    for pair in album_id_date:
        date_obj = datetime.strptime(pair[1], '%Y-%m-%d').date()
        if date_obj > cutoff_date:
            new_album_ids.append(pair[0])

 # 3.Add all the songs from the recent albums into a playlist

    # create a playlist for the user and the playlist id
    cur_user = sp.current_user()["id"]
    new_playlist =  sp.user_playlist_create(cur_user, "New Releases " + cutoff_date.strftime("%Y/%m/%d") + " - " + date.today().strftime("%Y/%m/%d"))
    new_pl_id = new_playlist["id"]

    # array to save all song uris
    song_uris = []

    # get every song uri from each album
    for album in new_album_ids:
        album_info = sp.album_tracks(album)["items"]
        for album_item in album_info:
            
            # some albums have multiple artists, so we will only save the songs from our followed artists
            for artist_info in album_item["artists"]:
                if artist_info["id"] in artist_list:
                    song_uris.append(album_item["uri"])

    # if two artists you follow create a song together, there will be duplicates in the song_uri list
    song_uris = [*set(song_uris)]

    # add the songs into the playlist
    sp.user_playlist_add_tracks("cur_user", new_pl_id, song_uris, None)

    return "Playlist Created"

def get_token():
    token_info = session.get(TOKEN_INFO, None)
    if not token_info:
        redirect(url_for('login', _external=False))
    
    now = int(time.time())

    is_expired = token_info['expires_at'] - now < 60
    if(is_expired):
        spotify_oauth = create_spotify_oauth()
        token_info = spotify_oauth.refresh_access_token(token_info['refresh_token'])

    return token_info

def create_spotify_oauth():
    return SpotifyOAuth(
        client_id = "PUT CLIENT ID HERE", 
        client_secret = "PUT CLIENT SECRET HERE",
        redirect_uri = url_for('redirect_page', _external = True),
        # permissions needed for authorization
        scope = 'user-library-read user-follow-read playlist-modify playlist-modify-private')

app.run(debug=True)