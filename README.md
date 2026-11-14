# Spotify Playlist Manager

Two things Spotify doesn't let you do in bulk:

- `sync`: adds every track from your playlists to your "Liked Songs"
- `sort`: sorts the tracks of your playlists alphabetically by title

Both work only on playlists you created. "Liked Songs" can't be reordered through the Spotify API, so `sort` leaves it untouched.

## Requirements

- macOS, Linux or Windows
- A Spotify app created at [developer.spotify.com/dashboard](https://developer.spotify.com/dashboard), with Redirect URI `http://127.0.0.1:8080/callback`

## Install

```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
brew install python
pip3 install spotipy
```

On macOS and Linux Python is already available, so you can skip the first two commands and just run `pip3 install spotipy`. On macOS, the first time you run `python3` the system may ask to install the Command Line Tools: accept.

On Windows Python has to be installed: download it from [python.org](https://www.python.org/downloads/windows/), tick "Add python.exe to PATH" during setup, then use `pip` and `python` instead of `pip3` and `python3`.

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
pip3 uninstall spotipy
brew uninstall python
brew autoremove
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/uninstall.sh)"
sudo rm -rf /opt/homebrew
```

If you used the system Python on macOS or Linux, `pip3 uninstall spotipy` is enough. On Windows, run `pip uninstall spotipy` and remove Python from Settings → Apps.
