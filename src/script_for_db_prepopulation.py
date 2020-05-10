import spotipy
import spotipy.util as util
import pprint
import pymongo

username = 'f'
scope = 'user-library-read user-top-read'
client_id = 'b4e8d875ebc74954a74b53ca13f1761b'
client_secret = '6e7b7779c1bc461a936d3e7bea55eea5'
redirect_uri = 'http://localhost:8080'
token = util.prompt_for_user_token(username,
                                   scope,
                                   client_id,
                                   client_secret,
                                   redirect_uri)

sp = spotipy.Spotify(auth=token)

client = pymongo.MongoClient('localhost', 27017)
db = client.music_data
collection = db.songs

file = open("../artists.txt", "r", encoding='utf8')
for i in range(10):
    try:
        artist = next(file)[:-1]
    except StopIteration:
        print('Koniec')
        break
    for i in range(0, 50, 50):
        track_results = sp.search(q=artist, type='track', limit=50, offset=i)
        for i, t in enumerate(track_results['tracks']['items']):

            track_artists = [x['name'] for x in t['artists']]
            track_artists_ids = [x['uri'] for x in t['artists']]
            genres = list(set([item for sublist in [sp.artist(x)['genres'] for x in track_artists_ids] for item in sublist]))
            print(t['name'])
            print('         _id: ', t['id'])
            print('         album: ', t['album']['name'])
            print('         artists: ', track_artists)
            print('         genres: ', genres)
            print('         duration: ', t['duration_ms'])
            print('         okładka: ', t['album']['images'][0]['url'])

            try:
                song = {'_id': t['id'], 'name': t['name'], 'album': t['album']['name'],
                        'artist': track_artists, 'genres': genres,
                        'duration': t['duration_ms'], 'image_url': t['album']['images'][0]['url']}
                collection.insert_one(song)
            except:
                print('Duplikat')
