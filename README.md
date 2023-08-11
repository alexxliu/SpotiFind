# SpotiFind
Automatically create a playlist of new releases from artists you follow <br />
Uses OAuth2.0 and Spotify Web API

![image](https://github.com/alexxliu/SpotiFind/assets/72209628/0d6cc110-989a-4e16-9feb-383281770a6b)


## Setup
1. Download findNewReleases.py
2. Go to https://developer.spotify.com/dashboard and create an app
3. Choose your App Name and App Description and set the Redirect URI to http://127.0.0.1:5000/redirect
4. In the file's directory run the following on the terminal
```
pip install flask spotipy
```
5. Run the program and go to http://127.0.0.1:5000

### References

https://developer.spotify.com/documentation/web-api

https://spotipy.readthedocs.io/en/2.19.0/
