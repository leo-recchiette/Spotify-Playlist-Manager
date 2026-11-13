"""
Script per aggiungere tutti i brani delle tue playlist Spotify
alla playlist di default "Brani che ti piacciono" (Liked Songs).

Richiede: pip install spotipy

Prima di eseguire, imposta le variabili SPOTIPY_CLIENT_ID, SPOTIPY_CLIENT_SECRET
e SPOTIPY_REDIRECT_URI come variabili d'ambiente, oppure modifica i valori qui sotto.
"""

import os
import sys
import time
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from spotipy.exceptions import SpotifyException

CLIENT_ID = os.environ.get("SPOTIPY_CLIENT_ID", "")
CLIENT_SECRET = os.environ.get("SPOTIPY_CLIENT_SECRET", "")
REDIRECT_URI = os.environ.get("SPOTIPY_REDIRECT_URI", "http://127.0.0.1:8080/callback")

# Scope necessari: leggere le playlist (anche collaborative/private) e modificare i Liked Songs
SCOPE = "playlist-read-private playlist-read-collaborative user-library-read user-library-modify"

# Se vuoi limitare lo script solo a certe playlist, metti qui i loro nomi esatti.
# Lascia None per processare TUTTE le playlist dell'utente.
PLAYLIST_NAMES_FILTER = None  # es: ["Running", "Chill", "Workout"]

BATCH_SIZE = 40  # limite imposto dall'API Spotify per /me/library (save/check)

# Con --dry-run lo script mostra cosa aggiungerebbe senza modificare nulla.
DRY_RUN = "--dry-run" in sys.argv


def get_client():
    auth_manager = SpotifyOAuth(
        client_id=CLIENT_ID,
        client_secret=CLIENT_SECRET,
        redirect_uri=REDIRECT_URI,
        scope=SCOPE,
        cache_path=".spotify_token_cache",
    )
    return spotipy.Spotify(auth_manager=auth_manager)


def get_all_user_playlists(sp, owned_only=True):
    """Recupera le playlist dell'utente. Se owned_only=True, tiene solo
    quelle di cui l'utente loggato è il proprietario (esclude playlist
    seguite, editoriali Spotify, o create da altri)."""
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
    # Dal 2026 l'API Spotify restituisce il brano nel campo "item" (prima era "track").
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
    """Ritorna il set dei track_id già presenti in Liked Songs, per evitare chiamate inutili."""
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


def main():
    sp = get_client()

    print("Recupero le tue playlist (solo quelle create da te)...")
    playlists = get_all_user_playlists(sp, owned_only=True)

    if PLAYLIST_NAMES_FILTER:
        playlists = [p for p in playlists if p["name"] in PLAYLIST_NAMES_FILTER]

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

    if to_add and DRY_RUN:
        print("Modalità --dry-run: nessuna modifica effettuata.")
    elif to_add:
        add_tracks_to_liked(sp, to_add)
        print("\nFatto! Tutti i brani sono stati aggiunti a 'Brani che ti piacciono'.")
    else:
        print("Nessun brano da aggiungere, tutto già sincronizzato.")


if __name__ == "__main__":
    main()