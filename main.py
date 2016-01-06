import sys
import spotipy
import spotipy.util as util
import subprocess as sp
import csv

scope = 'user-library-modify playlist-modify-private'
client_id = 'your-client-id'
client_secret = 'your-client-secret'
redirect_uri = 'http://localhost:8888' # Setup the call back you want to  

def createTemporaryServer():
	print "Starting Temporary Server"
	s = sp.Popen(['python','redirectServer.py'])
	return s

def closeTemporaryServer(server):
	print "Closing Temporary Server"
	sp.Popen.terminate(server)

def createPlaylist(spManager,username):
	playlist_name = raw_input("Enter playlist name:")

	playlist = spManager.user_playlist_create(username,playlist_name,False)
	return playlist['id']

def searchTrack(spManager,tracksList,name,artist,album=None):
	song_str = name + " by " + artist
	print "Searching for " + song_str

	if album is None:
		res = spManager.search(q='artist:'+ artist + ' track:' + name,type="track")
	else:
		res = spManager.search(q='artist:'+ artist + ' track:' + name + ' album:' + album,type="track")

	tracks = res['tracks']['items']

	if len(tracks) < 1:
		print song_str + " not found!"
		return 

	track = res['tracks']['items'][0]
	tracksList.append(track['id'])
	print song_str + ' added.'
	return


def main ():
	if len(sys.argv) > 1:
		username = sys.argv[1]
	else:
		print "Usage: %s username" % (sys.argv[0],)
		sys.exit()

	server = createTemporaryServer()
	token = util.prompt_for_user_token(username, scope, client_id , client_secret,redirect_uri)
	closeTemporaryServer(server)

	if token:
		tracks = []
		spManager = spotipy.Spotify(auth=token)
		n = raw_input("song:")
		a = raw_input("artist:")
		x = raw_input("album:")
		searchTrack(spManager,tracks,n,a,x)
		
		if len(tracks) > 0:
			playlistID = createPlaylist(spManager,username)
			spManager.user_playlist_add_tracks(username,playlistID,tracks)
			print "Playlist created!"
		else:
			print "No songs found!"
	else:
		print "Can't get token for", username

if __name__ == '__main__':
	main()