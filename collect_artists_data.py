import json
import os
import plistlib
import sys

import tqdm
import yaml

import config
from fetcher import lastfm
from fetcher import spotify


def load_artists_from_itunes_library(xml_file):
    with open(xml_file, "rb") as f:
        itunes_library = plistlib.load(f)

    artists = {}
    for track in itunes_library["Tracks"].values():
        if "Album Artist" in track:
            artist = track["Album Artist"]
        else:
            artist = track["Artist"]

        if artist.lower() in artists:
            artists[artist.lower()]["name"] = artist
            artists[artist.lower()]["genres"].add(track["Genre"])
        else:
            artists[artist.lower()] = {
                "name": artist,
                "genres": {track["Genre"]},
            }

    artists_data = {}
    for artist_key in artists:
        artist = artists[artist_key]
        artists_data[artist["name"]] = {"genres": sorted(artist["genres"])}
    return artists_data


def collect_artists_data(
    lastfm_fetcher, spotify_fetcher, itunes_artists_data, saved_artists_data
):
    new_artists_data = {}
    for artist_name in tqdm.tqdm(itunes_artists_data):
        if artist_name in saved_artists_data:
            new_artists_data[artist_name] = saved_artists_data[artist_name]
            continue
        artist_info = {}
        artist_info["itunes"] = itunes_artists_data[artist_name]
        artist_info["lastfm"] = lastfm_fetcher.fetch_artist_top_tags(artist_name)
        artist_info["spotify"] = spotify_fetcher.fetch_artist(artist_name)
        new_artists_data[artist_name] = artist_info
    return new_artists_data


def main():
    if len(sys.argv) != 2:
        print(f"usage: {sys.argv[0]} 'path/to/iTunes Library.xml'")
        sys.exit(1)
    itunes_library_xml_file = sys.argv[1]

    saved_artists_data = {}
    if os.path.exists(config.ARTISTS_DATA_FILE):
        with open(config.ARTISTS_DATA_FILE, "r") as f:
            saved_artists_data = json.load(fp=f)

    with open(config.CREDENTIALS_FILE, "r") as f:
        credentials = yaml.safe_load(f)

    itunes_artists_data = load_artists_from_itunes_library(itunes_library_xml_file)

    lastfm_fetcher = lastfm.LastfmGenreFetcher(credentials["lastfm"]["api_key"])
    spotify_fetcher = spotify.SpotifyGenreFetcher(
        credentials["spotify"]["client_id"], credentials["spotify"]["client_secret"]
    )
    spotify_fetcher.authorize()

    new_artists_data = collect_artists_data(
        lastfm_fetcher,
        spotify_fetcher,
        itunes_artists_data,
        saved_artists_data,
    )

    data_dir = os.path.dirname(config.ARTISTS_DATA_FILE)
    if not os.path.exists(data_dir):
        os.makedirs(data_dir)

    with open(config.ARTISTS_DATA_FILE, "w") as f:
        json.dump(new_artists_data, fp=f, indent=2)


if __name__ == "__main__":
    main()
