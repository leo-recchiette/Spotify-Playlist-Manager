# Spotify Playlist Manager

Two things Spotify doesn't let you do in bulk:

- `sync`: adds every track from your playlists to your "Liked Songs"
- `sort`: sorts the tracks of your playlists alphabetically by title

Both work only on playlists you created. "Liked Songs" can't be reordered through the Spotify API, so `sort` leaves it untouched.

## Requirements

- [Docker](https://www.docker.com/products/docker-desktop/), or Python 3.9+ (see [Without Docker](#without-docker))
- A Spotify app created at [developer.spotify.com/dashboard](https://developer.spotify.com/dashboard), with Redirect URI `http://127.0.0.1:8080/callback`

## 1. Credentials

Open `user_settings` and fill in the Client ID and Client Secret of your Spotify app:

```
SPOTIPY_CLIENT_ID=your_client_id
SPOTIPY_CLIENT_SECRET=your_client_secret
```

## 2. Run

```bash
docker compose run --rm spotify sync
docker compose run --rm spotify sort
```

Builds the image, runs the command and removes the container.

## Without Docker

Install Python from [python.org](https://www.python.org/downloads/) (Homebrew's Python blocks `pip3 install`), then from the project folder:

```bash
pip3 install spotipy==2.26.0
python3 spotify.py sync
python3 spotify.py sort
```

The first command is needed only once. The login is saved in `.spotify_token_cache`, so you only do it on the first run.

## Login

1. The script prints a link `https://accounts.spotify.com/authorize?...`: open it in your browser and authorize the app.
2. The browser takes you to `http://127.0.0.1:8080/callback?code=...` and shows a "page can't be reached" error: that's expected.
3. Copy the address from the browser's address bar and paste it into the terminal.
