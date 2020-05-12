import spotipy
import spotipy.util as util
import pprint
import pymongo
import traceback

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

client = pymongo.MongoClient('mongodb://heroku_3lvj3gxj:pn36um10djp0di4p8dcguoulp0@ds235437.mlab.com:35437/heroku_3lvj3gxj?retryWrites=false')
db = client.heroku_3lvj3gxj
collection = db.songs

print(collection.count())

file = open("../artists.txt", "r", encoding='utf8')
a = file.readlines()
for artist in a:
    print(' ',artist)
    if collection.count() > 100000:
        print("Kolekcja pełna")
        break
    '''try:
        artist = next(file)[:-1]
    except StopIteration:
        print('Koniec')
        break'''
    for i in range(0, 2000, 50):
        try:
            print(artist)
            track_results = sp.search(q=artist, type='track', limit=50, offset=i)
        except:
            print('Empty search for ', artist)
            traceback.print_exc()

            token = util.prompt_for_user_token(username,
                                               scope,
                                               client_id,
                                               client_secret,
                                               redirect_uri)

            sp = spotipy.Spotify(auth=token)

        for i, t in enumerate(track_results['tracks']['items']):

            try:
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
            except:
                print('Error')

            try:
                cover_url = t['album']['images'][0]['url'] if len(t['album']['images']) > 0 else None
                song = {'_id': t['id'], 'name': t['name'], 'album': t['album']['name'],
                        'artist': track_artists, 'genres': genres,
                        'duration': t['duration_ms'], 'image_url': cover_url}
                collection.insert_one(song)
                print('Piosenek w kolekcji:', collection.count())

            except:
                print('Duplikat')
