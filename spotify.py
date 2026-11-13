import os
import sys
import time
import unicodedata
from pathlib import Path

import spotipy
from spotipy.oauth2 import SpotifyOAuth
from spotipy.exceptions import SpotifyException

REDIRECT_URI = "http://127.0.0.1:8080/callback"
SCOPE = (
    "playlist-read-private playlist-read-collaborative "
    "playlist-modify-private playlist-modify-public "
    "user-library-read user-library-modify"
)
BATCH_SIZE = 40
SETTINGS_FILE = Path(__file__).with_name("user_settings")


def load_user_settings():
    if not SETTINGS_FILE.exists():
        return
    for line in SETTINGS_FILE.read_text().splitlines():
        key, sep, value = line.partition("=")
        if sep:
            os.environ[key.strip()] = value.strip()


def get_client():
    load_user_settings()
    client_id = os.environ.get("SPOTIPY_CLIENT_ID")
    client_secret = os.environ.get("SPOTIPY_CLIENT_SECRET")
    if not client_id or not client_secret:
        sys.exit("Inserisci SPOTIPY_CLIENT_ID e SPOTIPY_CLIENT_SECRET nel file user_settings")
    auth_manager = SpotifyOAuth(
        client_id=client_id,
        client_secret=client_secret,
        redirect_uri=REDIRECT_URI,
        scope=SCOPE,
        cache_path=".spotify_token_cache",
        open_browser=False,
    )
    return spotipy.Spotify(auth_manager=auth_manager)


def get_all_user_playlists(sp, owned_only=True):
    me = sp.current_user()
    my_id = me["id"]

    playlists = []
    results = sp.current_user_playlists(limit=50)
    while results:
        playlists.extend(results["items"])
        results = sp.next(results) if results["next"] else None

    if owned_only:
        playlists = [p for p in playlists if p.get("owner", {}).get("id") == my_id]

    return playlists


def get_all_track_ids_from_playlist(sp, playlist_id):
    track_ids = []
    results = sp.playlist_items(
        playlist_id,
        fields="items(item(id,type,is_local)),next",
        additional_types=["track"],
    )
    while results:
        for entry in results["items"]:
            track = entry.get("item") or entry.get("track")
            if (
                isinstance(track, dict)
                and track.get("id")
                and track.get("type", "track") == "track"
                and not track.get("is_local")
            ):
                track_ids.append(track["id"])
        results = sp.next(results) if results["next"] else None
    return track_ids


def already_liked(sp, track_ids):
    liked = set()
    for i in range(0, len(track_ids), BATCH_SIZE):
        batch = track_ids[i : i + BATCH_SIZE]
        statuses = sp.current_user_saved_tracks_contains(batch)
        for tid, is_liked in zip(batch, statuses):
            if is_liked:
                liked.add(tid)
        time.sleep(0.1)
    return liked


def add_tracks_to_liked(sp, track_ids):
    for i in range(0, len(track_ids), BATCH_SIZE):
        batch = track_ids[i : i + BATCH_SIZE]
        sp.current_user_saved_tracks_add(tracks=batch)
        print(f"  Aggiunti {len(batch)} brani ai Liked Songs...")
        time.sleep(0.2)


def get_playlist_titles(sp, playlist_id):
    titles = []
    results = sp.playlist_items(
        playlist_id,
        fields="items(item(name)),next",
        additional_types=["track", "episode"],
    )
    while results:
        for entry in results["items"]:
            titles.append((entry.get("item") or {}).get("name") or "")
        results = sp.next(results) if results["next"] else None
    return titles


def title_key(title):
    decomposed = unicodedata.normalize("NFKD", title)
    return "".join(c for c in decomposed if not unicodedata.combining(c)).casefold()


def sort_playlist(sp, playlist_id):
    titles = get_playlist_titles(sp, playlist_id)
    target = sorted(range(len(titles)), key=lambda k: title_key(titles[k]))
    current = list(range(len(titles)))
    moves = 0
    for position, wanted in enumerate(target):
        index = current.index(wanted, position)
        if index == position:
            continue
        sp.playlist_reorder_items(playlist_id, range_start=index, insert_before=position)
        current.insert(position, current.pop(index))
        moves += 1
        time.sleep(0.1)
    return moves


def sync_liked(sp):
    print("Recupero le tue playlist (solo quelle create da te)...")
    playlists = get_all_user_playlists(sp, owned_only=True)

    print(f"Trovate {len(playlists)} playlist da processare.\n")

    all_track_ids = set()
    for playlist in playlists:
        name = playlist["name"]
        print(f"Lettura playlist: {name}")
        try:
            track_ids = get_all_track_ids_from_playlist(sp, playlist["id"])
        except SpotifyException as e:
            print(f"  Saltata ({e}).")
            continue
        print(f"  {len(track_ids)} brani trovati.")
        all_track_ids.update(track_ids)

    all_track_ids = list(all_track_ids)
    print(f"\nTotale brani unici raccolti da tutte le playlist: {len(all_track_ids)}")

    print("Controllo quali sono già nei Liked Songs...")
    liked = already_liked(sp, all_track_ids)
    to_add = [tid for tid in all_track_ids if tid not in liked]

    print(f"Brani già presenti nei Liked Songs: {len(liked)}")
    print(f"Brani da aggiungere: {len(to_add)}\n")

    if to_add:
        add_tracks_to_liked(sp, to_add)
        print("\nFatto! Tutti i brani sono stati aggiunti a 'Brani che ti piacciono'.")
    else:
        print("Nessun brano da aggiungere, tutto già sincronizzato.")


def sort_playlists(sp):
    print("Recupero le tue playlist (solo quelle create da te)...")
    playlists = get_all_user_playlists(sp, owned_only=True)

    print(f"Trovate {len(playlists)} playlist da ordinare.\n")

    for playlist in playlists:
        print(f"Ordino playlist: {playlist['name']}")
        try:
            moves = sort_playlist(sp, playlist["id"])
        except SpotifyException as e:
            print(f"  Saltata ({e}).")
            continue
        print(f"  {moves} brani spostati." if moves else "  Già in ordine.")

    print("\nFatto! Playlist ordinate per titolo.")


COMMANDS = {"sync": sync_liked, "sort": sort_playlists}


def main():
    command = sys.argv[1] if len(sys.argv) > 1 else ""
    if command not in COMMANDS:
        sys.exit("Specifica un comando: sync oppure sort")
    COMMANDS[command](get_client())


if __name__ == "__main__":
    main()
