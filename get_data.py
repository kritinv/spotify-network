from collections import defaultdict
import json
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from dotenv import load_dotenv
from tqdm import tqdm
import time

###############################################
# Before you run get_data.py
###############################################
# 1.) Install spotify api python wrapper 
#   ...........
#   pip install spotipy
#   ...........
# 2.) Create a .env and store your api credentials there
#   ...........
#   SPOTIPY_CLIENT_ID='your-spotify-client-id'
#   SPOTIPY_CLIENT_SECRET='your-spotify-client-secret'
#   SPOTIPY_REDIRECT_URI='your-app-redirect-url' (I used http://localhost)
#   ...........

load_dotenv()

class Artist:
	'''Helper class for compiling information about artists'''
	def __init__(self, artist_id, name, genres, followers):
		self.artist_id = artist_id
		self.name = name
		self.genres = genres
		self.followers = followers

	def __str__(self):
		return self.name

	def __repr__(self):
		return self.artist_id

	def __eq__(self, other):
		return self.artist_id == other.artist_id

	def __hash__(self):
		return hash(self.artist_id)


###############################################
# Authentication and Initialization
###############################################

# jessicas
#   SPOTIPY_CLIENT_ID='cd577af44aa748d98b50df5fc60efcad'
#   SPOTIPY_CLIENT_SECRET='41ef48a4f63f4b27915ac3d387cd7b86'
#   SPOTIPY_REDIRECT_URI='http://localhost:3000'

# belindas
#   SPOTIPY_CLIENT_ID='6f1d515387ea45e0be22d9f64e79f86f'
#   SPOTIPY_CLIENT_SECRET='3db998def7e542359d60c92fd7dc97e2'
#   SPOTIPY_REDIRECT_URI='http://localhost'

# kathys
#   SPOTIPY_CLIENT_ID='ffc4f29a4db942dcbb0647017847acfa'
#   SPOTIPY_CLIENT_SECRET='1bb7e334d3b34cd593ef73f8c6bfac5c'
#   SPOTIPY_REDIRECT_URI='http://localhost'

# kathy 2s
#   SPOTIPY_CLIENT_ID='5aa9b8bcdb314445b1e9e0ffa8b62651'
#   SPOTIPY_CLIENT_SECRET='d4f560624f6c434fa54aa554666ba32b'
#   SPOTIPY_REDIRECT_URI='http://localhost'

# kathy 3s
#   SPOTIPY_CLIENT_ID='748740587c3c4e249aa6e7556ec45450'
#   SPOTIPY_CLIENT_SECRET='092d3402d913406fa31df5cbfa4b62c2'
#   SPOTIPY_REDIRECT_URI='http://localhost'

# rehas
#   SPOTIPY_CLIENT_ID='5c7dd99433934d9aadc74007f1dbc77b'
#   SPOTIPY_CLIENT_SECRET='c18f75a6357d4fab866e926443959ee9'
#   SPOTIPY_REDIRECT_URI='http://localhost:3000'

# Authentication
auth_manager  = SpotifyClientCredentials()
sp = spotipy.Spotify(client_credentials_manager=auth_manager, requests_timeout=5, retries=10)

# These starting artists were top artists in each year's Billboard Year End Hot 100 Playlist
# If a song had multiple artists, only the first was selected
# Wnet down the list until 5 distinct artists were obtained
starting_artists = {
	#"2013": ["5BcAKTbp20cv7tC5VqPFoC", "0ZrpamOxcZybMHGg1AYtHP", "53XhwfbYqKCa1cC15pYq2q", "25fqWEebq6PoiGQIHIrdtv", "31TPClRtHm23RisEBtV3X7"],
	#"2014": ["5BcAKTbp20cv7tC5VqPFoC", "0ZrpamOxcZybMHGg1AYtHP", "53XhwfbYqKCa1cC15pYq2q", "25fqWEebq6PoiGQIHIrdtv", "31TPClRtHm23RisEBtV3X7"],
	#"2015": ["5BcAKTbp20cv7tC5VqPFoC", "0ZrpamOxcZybMHGg1AYtHP", "53XhwfbYqKCa1cC15pYq2q", "25fqWEebq6PoiGQIHIrdtv", "31TPClRtHm23RisEBtV3X7"],
	#"2016": ["5BcAKTbp20cv7tC5VqPFoC", "0ZrpamOxcZybMHGg1AYtHP", "53XhwfbYqKCa1cC15pYq2q", "25fqWEebq6PoiGQIHIrdtv", "31TPClRtHm23RisEBtV3X7"],
	# "2017": ["5BcAKTbp20cv7tC5VqPFoC", "0ZrpamOxcZybMHGg1AYtHP", "53XhwfbYqKCa1cC15pYq2q", "25fqWEebq6PoiGQIHIrdtv", "31TPClRtHm23RisEBtV3X7"],
	# "2018": ["5BcAKTbp20cv7tC5VqPFoC", "0ZrpamOxcZybMHGg1AYtHP", "53XhwfbYqKCa1cC15pYq2q", "25fqWEebq6PoiGQIHIrdtv", "31TPClRtHm23RisEBtV3X7"],
	# "2019": ["7jVv8c5Fj3E9VhNjxT4snq", "246dkjvS1zLTtiykXe5h60", "26VFTg2z8YR0cCuwLzESi2", "6qqNVTkY8uBg9cP3Jd7DAH", "64KEffDW9EtZ1y2vBYgq8T"],
	# "2020": ["1Xyo4u8uXC1ZmMpatF05PJ", "246dkjvS1zLTtiykXe5h60", "757aE44tKEUQEqRuT6GnEB", "6M2wZ9GZgrQXHCFfjv46we", "4r63FhuTkUYltbVAg5TQnk"],
	# "2021": ["6M2wZ9GZgrQXHCFfjv46we", "1Xyo4u8uXC1ZmMpatF05PJ", "6fWVd57NKTalqvmjRd2t8Z", "1McMsnEElThX1knmY4oliG", "5cj0lLjcoR7YOSnhnX0Po5"],
	# "2022": ["4yvcSjfu4PC0CYQyLy4wSq", "6KImCVD70vtIoJWnq6nGn3", "2tIP7SsRs7vjIcLrU85W8J", "4dpARuHxo51G3z768sgnrY", "6eUKZXaKkcviH0Ku9w2n3V"],
	# "2023": ["4oUHIQIBe0LHzYfvXNW4QM", "5YGY8feqx7naU7z4HrwZM6", "7tYKF4w9nC0nq9CsPZTHyP", "06HL4z0CvFAxyc27GXpf02", "0iEtIxbK0KxaSlF7G42ZOp"],
	}

# Parameters
max_artists = 500
follower_threshold = 1000
queues = {year: [] for year in starting_artists.keys()}
artist_sets = {year: set() for year in starting_artists.keys()}
artist_maps = {year: defaultdict(list) for year in starting_artists.keys()}
valid_artists = {year: {} for year in starting_artists.keys()}


for year, artists in starting_artists.items():
	print("Initializing " + str(year))
	for cur_id in artists:
		cur = sp.artist(cur_id)
		cur_artist = Artist(cur_id, cur["name"], cur["genres"], cur["followers"]["total"])
		artist_sets[year].add(cur_artist)
		queues[year].append(cur_artist)
		valid_artists[year][cur_artist.artist_id] = True

###############################################
# BFS on Recommended Artists
###############################################

def artist_is_valid(artist: Artist):
	valid = True
	if artist.followers < follower_threshold:
		valid = False
	if not artist_active_in_year(sp, artist.artist_id, year):
		valid = False
	return valid

def artist_active_in_year(sp, artist_id, year):
	albums = sp.artist_albums(artist_id, album_type='album')
	#time.sleep(1)
	for album in albums['items']:
		release_date = album['release_date']  # Release date format can be "YYYY-MM-DD", "YYYY-MM", or "YYYY"
		if release_date.startswith(str(year)):
			return True
	return False

for year, queue in queues.items():
	pbar = tqdm(queue, desc=f"Processing {year}", unit=" artists")
	while queue and len(artist_sets[year]) < max_artists:

		cur_artist = queue.pop(0)
		related_artists = sp.artist_related_artists(cur_artist.artist_id)
		#time.sleep(1)

		for r in related_artists["artists"]:
			artist = Artist(r["id"], r["name"], r["genres"], r["followers"]["total"])
			
			# check if artist has already been processed and is valid
			is_valid = True
			if artist.artist_id in valid_artists[year].keys():
				print('cached')
				is_valid = artist_maps[year][artist.artist_id]
			else:
				is_valid = artist_is_valid(artist)
				valid_artists[year][artist.artist_id] = is_valid
			if not is_valid:
				continue
			
			# add valid artist to cur_artist id in artist_maps
			artist_maps[year][cur_artist.artist_id].append(artist.artist_id)
			
			# add to unique artists_set
			if artist not in artist_sets[year]:
				queue.append(artist)  # Append tuple of (Artist, year)
				pbar.update(1)
				artist_sets[year].add(artist)
		

			
	artist_map = artist_maps[year] 
	json.dump(artist_map, open(f"related_{year}.json", "w+"), indent=4)
	artists = {artist.artist_id: vars(artist) for artist in artist_sets[year]}
	print(f"Total artists for {year}: ", len(artists))
	json.dump(artists, open(f"artists_{year}.json", "w+"), indent=4)