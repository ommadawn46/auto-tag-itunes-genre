# Auto-tag iTunes Genre

This is my personal tool for synchronizing the music genres of tracks in the iTunes Library with data from web services (Last.fm, Spotify). Currently, only Windows is supported.


#### Set Credentials

Set [Last.fm API](https://www.last.fm/api) and [Spotify API](https://developer.spotify.com/documentation/web-api/) credentials to `data/input/credentials.yaml`.


#### collect_artists_data.py

Collect music genres of artists registered in iTunes Library from web services.

```
python collect_artists_data.py 'path/to/iTunes Library.xml'
```


#### generate_genre_patch.py

Based on the data gathered, determine new genres and create a patch file to apply changes.

```
python generate_genre_patch.py
```

The patch file is output to `data/output/genre_patch.csv`. The artists whose status is 'ready' will be the target of the music genre change.


#### apply_genre_patch.py

Apply the patch file to the iTunes Library to update genres. Use the [iTunes COM Interface](http://www.joshkunz.com/iTunesControl/) to control iTunes.

```
python apply_genre_patch.py 'data/output/genre_patch.csv'
```
