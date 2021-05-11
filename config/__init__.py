import yaml

uniq_sorted = lambda lst: sorted(set(lst))


def load_not_genre_tags():
    file = "config/not_genre_tags.yaml"
    with open(file, "r") as f:
        load_not_genre = uniq_sorted(yaml.safe_load(f))
    with open(file, "w") as f:
        f.write(yaml.dump(load_not_genre))
    return load_not_genre


def load_tag_aliases():
    file = "config/tag_aliases.yaml"
    with open(file, "r") as f:
        tag_aliases = yaml.safe_load(f)
        for tag in tag_aliases:
            tag_aliases[tag] = uniq_sorted(tag_aliases[tag])
    with open(file, "w") as f:
        f.write(yaml.dump(tag_aliases))
    return tag_aliases


def load_sub_genres():
    file = "config/sub_genres.yaml"
    with open(file, "r") as f:
        sub_genres = yaml.safe_load(f)
        for genre in sub_genres:
            sub_genres[genre] = uniq_sorted(sub_genres[genre])
    with open(file, "w") as f:
        f.write(yaml.dump(sub_genres))
    return sub_genres


def load_trim_prefix():
    file = "config/trim_prefix.yaml"
    with open(file, "r") as f:
        trim_prefix = uniq_sorted(yaml.safe_load(f))
    with open(file, "w") as f:
        f.write(yaml.dump(trim_prefix))
    return trim_prefix


NOT_GENRE_TAGS = load_not_genre_tags()
TAG_ALIASES = load_tag_aliases()
SUB_GENRES = load_sub_genres()
TRIM_PREFIX = load_trim_prefix()
NOT_GENRE_TAGS += TRIM_PREFIX

SUB_TAG_MAX = 8

CREDENTIALS_FILE = "data/input/credentials.yaml"
ARTISTS_DATA_FILE = "data/work/artists_data.json"
DIFF_PATCH_FILE = "data/output/genre_patch.csv"
