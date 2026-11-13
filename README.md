# Spotify Playlist Manager

Two things Spotify doesn't let you do in bulk:

- `sync`: adds every track from your playlists to your "Liked Songs"
- `sort`: sorts the tracks of your playlists alphabetically by title

Both work only on playlists you created. "Liked Songs" can't be reordered through the Spotify API, so `sort` leaves it untouched.

## Requirements

- macOS with [Homebrew](https://brew.sh)
- A Spotify app created at [developer.spotify.com/dashboard](https://developer.spotify.com/dashboard), with Redirect URI `http://127.0.0.1:8080/callback`

## Install

```bash
brew install python
pip3 install --break-system-packages spotipy==2.26.0
```

## Credentials

Open `user_settings` and fill in the Client ID and Client Secret of your Spotify app:

```
SPOTIPY_CLIENT_ID=your_client_id
SPOTIPY_CLIENT_SECRET=your_client_secret
```

## Run

From the project folder:

```bash
python3 spotify.py sync
python3 spotify.py sort
```

The first time, the browser opens: log in and authorize the app. The login is saved in `.spotify_token_cache`, so the next runs start right away.

## Uninstall

```bash
pip3 uninstall -y --break-system-packages spotipy
brew uninstall python
```
