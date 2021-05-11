import json
import sys

import requests
from retry import retry


class LastfmGenreFetcher:
    API_URL = "http://ws.audioscrobbler.com/2.0/"

    def __init__(self, api_key):
        self.api_key = api_key

    @retry(tries=5, delay=5)
    def fetch_artist_top_tags(self, artist_name):
        params = {
            "method": "artist.getTopTags",
            "artist": artist_name,
            "autocorrect": 1,
            "api_key": self.api_key,
            "format": "json",
        }
        result = json.loads(requests.get(self.API_URL, params=params).text)
        if "error" in result:
            print(f"{repr(artist_name)}: {result}")
            raise Exception
        return result


def main():
    if len(sys.argv) != 3:
        sys.exit(1)
    api_key = sys.argv[1]
    artist_name = sys.argv[2]

    fetcher = LastfmGenreFetcher(api_key)

    top_tags = fetcher.fetch_artist_top_tags(artist_name)
    print(top_tags)


if __name__ == "__main__":
    main()
