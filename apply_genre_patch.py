import csv
import logging
import sys

import win32com.client

logging.basicConfig(filename="data/logs/patch_apply.log", level=logging.INFO)


def load_diff_patch_file(diff_patch_file):
    artist_diffs = {}
    with open(diff_patch_file, "r", encoding="utf_8_sig") as f:
        reader = csv.reader(f, lineterminator="\n")
        _ = next(reader)
        for artist_name, original_genres, new_genre, status, message in reader:
            artist_name_lower = artist_name.lower()
            artist_diffs[artist_name_lower] = (
                original_genres,
                new_genre,
                status,
                message,
            )
    return artist_diffs


def set_new_genres_to_itunes_tracks(artist_diffs):
    itunes = win32com.client.gencache.EnsureDispatch("iTunes.Application")
    library_playlist = itunes.LibraryPlaylist

    for iittrack in library_playlist.Tracks:
        track = win32com.client.CastTo(iittrack, "IITFileOrCDTrack")
        artist_name = track.AlbumArtist
        if artist_name == "":
            artist_name = track.Artist
        artist_name_lower = artist_name.lower()

        if artist_name_lower in artist_diffs:
            old_genre = track.Genre
            original_genres, new_genre, status, message = artist_diffs[
                artist_name_lower
            ]
            if status == "ready":
                if new_genre != old_genre:
                    track.Genre = new_genre
                    logging.info(
                        f"[+] {artist_name} - {track.Name}: {old_genre} -> {new_genre}"
                    )
                else:
                    logging.info(f"[+] {artist_name} - {track.Name}: no change")
            else:
                logging.warning(f"[!] {artist_name} - {track.Name}: not ready")
        else:
            logging.error(f"[!] {artist_name} - {track.Name}: not found")


def main():
    if len(sys.argv) != 2:
        sys.exit(1)
    diff_patch_file = sys.argv[1]

    artist_diffs = load_diff_patch_file(diff_patch_file)
    set_new_genres_to_itunes_tracks(artist_diffs)


if __name__ == "__main__":
    main()
