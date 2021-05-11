import json
import os
import sys

import config


def norm_tag_name(tag_name):
    def resolve_alias(tag_name):
        for name_tag in config.TAG_ALIASES:
            for alias_tag in config.TAG_ALIASES[name_tag]:
                if alias_tag == tag_name:
                    return name_tag
        return tag_name

    normed_tag_name = resolve_alias(tag_name.lower())
    for prefix in config.TRIM_PREFIX:
        if normed_tag_name.startswith(prefix + " "):
            return norm_tag_name(normed_tag_name[len(prefix) + 1 :])
    return normed_tag_name


def find_sub_genre(parent_genre, target_tags):
    sub_tags = []
    for tag_name in target_tags:
        if tag_name != parent_genre:
            sub_tags.append(tag_name)

    for tag_name in sub_tags:
        if tag_name in config.SUB_GENRES[parent_genre]:
            return tag_name
    return None


def resolve_sub_genre(tag_name, tags):
    for parent_genre in config.SUB_GENRES.keys():
        if parent_genre == tag_name:
            sliced_tags = tags[: config.SUB_TAG_MAX]
            sub_genre = find_sub_genre(parent_genre, sliced_tags)
            if sub_genre:
                return sub_genre
    return None


def resolve_sub_genre_recursive(tag_name, tags):
    while True:
        sub_genre = resolve_sub_genre(tag_name, tags)
        if sub_genre:
            tag_name = sub_genre
        else:
            break
    return tag_name


def get_top_tag(tags):
    for tag_name in tags:
        if not tag_name:
            continue
        return resolve_sub_genre_recursive(tag_name, tags)


def calc_lastfm_scores(lastfm_tags):
    lastfm_tag_scores = {}
    for rank, tag in enumerate(lastfm_tags):
        norm_tag = norm_tag_name(tag["name"])
        cur_points = max(tag["count"] - rank, 0)
        if (norm_tag not in lastfm_tag_scores) or (
            norm_tag in lastfm_tag_scores and cur_points > lastfm_tag_scores[norm_tag]
        ):
            lastfm_tag_scores[norm_tag] = cur_points
    return lastfm_tag_scores


def calc_spotify_scores(spotify_genres):
    spotify_genre_scores = {}
    if spotify_genres:
        for rank, genre in enumerate(spotify_genres):
            norm_genre = norm_tag_name(genre)
            cur_points = max(100 - ((rank + 1) * 10), 0)
            if (norm_genre not in spotify_genre_scores) or (
                norm_genre in spotify_genre_scores
                and cur_points > spotify_genre_scores[norm_genre]
            ):
                spotify_genre_scores[norm_genre] = cur_points
    return spotify_genre_scores


def calc_genre_scores(lastfm_tag_scores, spotify_genre_scores):
    genre_scores = {}
    for genre in sorted(lastfm_tag_scores.keys() | spotify_genre_scores.keys()):
        lastfm_score = lastfm_tag_scores[genre] if genre in lastfm_tag_scores else 0
        spotify_score = (
            spotify_genre_scores[genre] if genre in spotify_genre_scores else 0
        )
        genre_scores[genre] = lastfm_score + spotify_score
    return genre_scores


def extract_genres(artist_name, artists_data):
    lastfm_tag_scores = calc_lastfm_scores(
        artists_data[artist_name]["lastfm"]["toptags"]["tag"]
    )
    spotify_genre_scores = calc_spotify_scores(
        artists_data[artist_name]["spotify"]["genres"]
        if artists_data[artist_name]["spotify"]
        else None
    )
    genre_scores = calc_genre_scores(lastfm_tag_scores, spotify_genre_scores)

    filtered_genres = list(
        map(
            lambda x: x[0],
            filter(
                lambda x: (x[0] not in config.NOT_GENRE_TAGS) and (x[1] > 0),
                sorted(genre_scores.items(), key=lambda x: x[1], reverse=True),
            ),
        )
    )
    return filtered_genres


def match_itunes_genre(target_genre, itunes_genre):
    parent_genre = itunes_genre.lower()
    if parent_genre == "alternative":
        parent_genre = "alternative rock"
    elif parent_genre == "punk":
        parent_genre = "punk rock"
    elif parent_genre == "rap":
        parent_genre = "hip-hop"
    elif parent_genre == "country & folk":
        parent_genre = "folk"
    elif parent_genre == "soundtrack":
        parent_genre = "soundtracks"
    elif parent_genre == "electronica":
        parent_genre = "electronic"

    def find(target_genre, parent_genre):
        if target_genre == parent_genre:
            return True
        if parent_genre not in config.SUB_GENRES:
            return False

        for sub_genre in config.SUB_GENRES[parent_genre]:
            if sub_genre == target_genre:
                return True
            if sub_genre in config.SUB_GENRES and find(target_genre, sub_genre):
                return True
        return False

    return find(target_genre, parent_genre)


def process_artist(artist_name, artists_data):
    top_genre = get_top_tag(extract_genres(artist_name, artists_data))
    if not top_genre:
        return None, "error", "failed to get genre information"

    original_genres = artists_data[artist_name]["itunes"]["genres"]
    if len(original_genres) == 1:
        if match_itunes_genre(top_genre, original_genres[0]):
            return top_genre, "ready", ""
        else:
            return top_genre, "error", "new_genre does not match original_genres"
    else:
        return top_genre, "error", "original_genres are not unique"


def main():
    import csv

    if os.path.exists(config.ARTISTS_DATA_FILE):
        with open(config.ARTISTS_DATA_FILE, "r") as f:
            artists_data = json.load(f)
    else:
        print(f"[!] Cannot find '{config.ARTISTS_DATA_FILE}'.")
        print(
            f"Please run 'collect_artists_data.py' first to build '{config.ARTISTS_DATA_FILE}.'"
        )
        sys.exit(1)

    artist_names = artists_data.keys()

    with open(config.DIFF_PATCH_FILE, "w", encoding="utf_8_sig") as f:
        writer = csv.writer(f, lineterminator="\n")
        writer.writerow(
            ["artist_name", "original_genres", "new_genre", "status", "message"]
        )
        for artist_name in sorted(artist_names):
            top_genre, status, message = process_artist(artist_name, artists_data)
            writer.writerow(
                [
                    artist_name,
                    artists_data[artist_name]["itunes"]["genres"],
                    top_genre.title() if top_genre else None,
                    status,
                    message,
                ]
            )
    print(f"Output a genre diff patch file to '{config.DIFF_PATCH_FILE}'.")


if __name__ == "__main__":
    main()
