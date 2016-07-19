import sys
import spotipy
import spotipy.util as util
import subprocess as sp
import csv
import eyed3
import glob

paths = glob.glob('music/*.mp3')

scope = 'user-library-modify playlist-modify-private'
#client_id = 'your-client-id'
#client_secret = 'your-client-secret'
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

def searchTrack(spManager,tracksList,name,artist,album):
	song_str = name + " by " + artist
	print "Searching for " + song_str

	if album == '':
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

def csvParse(spManager,tracks,filename):
	try:
		parseFile = open(filename)
	except IOError:
		print "File Doesn't exist. Quitting script.."
		sys.exit()
	try:
		reader = csv.reader(parseFile)
		for row in reader:
			if row[0].strip() == '' or row[1].strip() == '':
				print "Error in CSV! Missing data! Skipping row"
			else:
				if row[2].split() == '':
					row[2] = ''
				searchTrack(spManager,tracks,row[0],row[1],row[2])
	finally:
		parseFile.close()

def generateCSVFile():
	songDataList = []
	for file in paths:
		audioFile = eyed3.load(file)
		title = audioFile.tag.title
		artist = audioFile.tag.artist
		album = audioFile.tag.album
		songData = [title,artist,album]
		songDataList.append(songData)
	filename = raw_input("Enter a name for the CSV file:")
	outputFile = open(filename,"wb")
	try:
		writer = csv.writer(outputFile)
		for song in songDataList:
			writer.writerow(song)
	finally:
		outputFile.close()
	return filename

def main():
	if len(sys.argv) > 1:
		username = sys.argv[1]
	else:
		print "Usage: %s username" % (sys.argv[0],)
		sys.exit()
	filename = generateCSVFile()
	server = createTemporaryServer()
	token = util.prompt_for_user_token(username, scope, client_id , client_secret,redirect_uri)
	closeTemporaryServer(server)

	if token:
		tracks = []
		spManager = spotipy.Spotify(auth=token)
		csvParse(spManager,tracks,filename)

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