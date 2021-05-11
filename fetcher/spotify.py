import json
import sys
import time

import requests
from retry import retry


class SpotifyGenreFetcher:
    def __init__(self, client_id, client_secret):
        self.client_id = client_id
        self.client_secret = client_secret
        self.access_token = None

    def get_access_token(self):
        token_resp = requests.post(
            "https://accounts.spotify.com/api/token",
            params={
                "grant_type": "client_credentials",
            },
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            auth=(self.client_id, self.client_secret),
            allow_redirects=False,
        )
        token_body = json.loads(token_resp.text)
        return token_body["access_token"]

    def authorize(self):
        if not self.access_token:
            self.access_token = self.get_access_token()

    @retry(tries=5, delay=5)
    def fetch_artist(self, artist_name):
        if not self.access_token:
            raise Exception("need authorize")

        search_resp = requests.get(
            "https://api.spotify.com/v1/search",
            params={
                "q": artist_name,
                "type": "artist",
                "market": "US",
            },
            headers={"Authorization": f"Bearer {self.access_token}"},
        )
        if "Retry-After" in search_resp.headers:
            time.sleep(int(search_resp.headers["Retry-After"]))
            return self.fetch_artist(self.access_token, artist_name)

        search_body = json.loads(search_resp.text)
        if len(search_body["artists"]["items"]) == 0:
            return None

        for item in search_body["artists"]["items"]:
            if item["name"].lower() == artist_name.lower():
                return item
        return None


def main():
    if len(sys.argv) != 4:
        sys.exit(1)
    client_id = sys.argv[1]
    client_secret = sys.argv[2]
    artist_name = sys.argv[3]

    fetcher = SpotifyGenreFetcher(client_id, client_secret)
    fetcher.authorize()

    artist = fetcher.fetch_artist(artist_name)
    print(artist)


if __name__ == "__main__":
    main()
