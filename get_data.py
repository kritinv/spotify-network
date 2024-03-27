from collections import defaultdict
import json
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from dotenv import load_dotenv
from tqdm import tqdm

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

# Authentication
client_credentials_manager = SpotifyClientCredentials()
sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager, requests_timeout=30)

# These starting artists were top artists in each year's Billboard Year End Hot 100 Playlist
# If a song had multiple artists, only the first was selected
# Wnet down the list until 5 distinct artists were obtained
starting_artists = {
	"2013": ["5BcAKTbp20cv7tC5VqPFoC", "0ZrpamOxcZybMHGg1AYtHP", "53XhwfbYqKCa1cC15pYq2q", "25fqWEebq6PoiGQIHIrdtv", "31TPClRtHm23RisEBtV3X7"],
	"2014": ["2RdwBSPQiwcmiDo9kixcl8", "6jJ0s89eD6GaHleKKya26X", "5y2Xq6xcjJb2jVM54GHK3t", "5yG7ZAZafVaAlMTeBybKAL", "5Pwc4xIPtQLFEnJriah9YJ"],
	"2015": ["3hv9jJF3adDNsBSIQDqcjp", "6eUKZXaKkcviH0Ku9w2n3V", "137W8MRPWKqSmrBGDBFSop", "6PXS4YHDkKvl1wkIl4V8DL", "04gDigrS5kc9YWfZHwBETP"],
	"2016": ["1uNFoZAHBGtllmzznpCI3s", "3TVXtAsR1Inumwj472S9r4", "5pKCCKE2ajJHZ9KAiaK11H", "3YQKmKGau1PzlVlkL1iodx", "7pFeBzX627ff0VnN6bxPR4"],
    "2017": ["6eUKZXaKkcviH0Ku9w2n3V", "4V8Sr092TqfHkfAA5fXXqG", "0du5cEVh5yTK9QJze8zA0C", "2YZyLoL8N0Wb9xBt1NhZWg", "69GGBxA162lTqCwzJG5jLp"],
    "2018": ["3TVXtAsR1Inumwj472S9r4", "6eUKZXaKkcviH0Ku9w2n3V", "64M6ah0SkkRsnPGtGiRAbb", "4nDoRrQiYLoBzwC5BhVJzF", "246dkjvS1zLTtiykXe5h60"],
    "2019": ["7jVv8c5Fj3E9VhNjxT4snq", "246dkjvS1zLTtiykXe5h60", "26VFTg2z8YR0cCuwLzESi2", "6qqNVTkY8uBg9cP3Jd7DAH", "64KEffDW9EtZ1y2vBYgq8T"],
    "2020": ["1Xyo4u8uXC1ZmMpatF05PJ", "246dkjvS1zLTtiykXe5h60", "757aE44tKEUQEqRuT6GnEB", "6M2wZ9GZgrQXHCFfjv46we", "4r63FhuTkUYltbVAg5TQnk"],
    "2021": ["6M2wZ9GZgrQXHCFfjv46we", "1Xyo4u8uXC1ZmMpatF05PJ", "6fWVd57NKTalqvmjRd2t8Z", "1McMsnEElThX1knmY4oliG", "5cj0lLjcoR7YOSnhnX0Po5"],
	"2022": ["4yvcSjfu4PC0CYQyLy4wSq", "6KImCVD70vtIoJWnq6nGn3", "2tIP7SsRs7vjIcLrU85W8J", "4dpARuHxo51G3z768sgnrY", "6eUKZXaKkcviH0Ku9w2n3V"],
	"2023": ["4oUHIQIBe0LHzYfvXNW4QM", "5YGY8feqx7naU7z4HrwZM6", "7tYKF4w9nC0nq9CsPZTHyP", "06HL4z0CvFAxyc27GXpf02", "0iEtIxbK0KxaSlF7G42ZOp"],
}

# Parameters
max_artists = 5000
follower_threshold = 1000
queues = {year: [] for year in starting_artists.keys()}
artist_sets = {year: set() for year in starting_artists.keys()}
artist_maps = {year: defaultdict(list) for year in starting_artists.keys()}

for year, artists in starting_artists.items():
	print("Initializing " + str(year))
	for cur_id in artists:
		cur = sp.artist(cur_id)
		cur_artist = Artist(cur_id, cur["name"], cur["genres"], cur["followers"]["total"])
		artist_sets[year].add(cur_artist)
		queues[year].append(cur_artist)

###############################################
# BFS on Recommended Artists
###############################################

def artist_active_in_year(spotify_client, artist_id, year):
	albums = spotify_client.artist_albums(artist_id, album_type='album')
	for album in albums['items']:
		release_date = album['release_date']  # Release date format can be "YYYY-MM-DD", "YYYY-MM", or "YYYY"
		if release_date.startswith(str(year)):
			return True
	return False

for year, queue in queues.items():
	pbar = tqdm(queue, desc=f"Processing {year}", unit=" artists")
	while queue and len(artist_sets[year]) < max_artists:

		cur_artist = queue.pop(0)
		artists = sp.artist_related_artists(cur_artist.artist_id)
		
		for artist in artists["artists"]:
			
			if artist["followers"]["total"] < follower_threshold:
				continue
			if not artist_active_in_year(sp, artist["id"], year):
				continue
			
			related = Artist(artist["id"], artist["name"], artist["genres"], artist["followers"]["total"])
			artist_maps[year][cur_artist.artist_id].append(related.artist_id)
			
			if related not in artist_sets[year]:
				queue.append(related)  # Append tuple of (Artist, year)
				pbar.update(1)
			artist_sets[year].add(related)
			
	artist_map = artist_maps[year] 
	json.dump(artist_map, open(f"related_{year}.json", "w+"), indent=4)
	artists = {artist.artist_id: vars(artist) for artist in artist_sets[year]}
	print(f"Total artists for {year}: ", len(artists))
	json.dump(artists, open(f"artists_{year}.json", "w+"), indent=4)