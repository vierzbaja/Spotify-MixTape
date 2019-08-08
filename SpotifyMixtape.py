#Make radio station - get top and bottom songs per artist in popularity
import spotipy
import spotipy.util as util
import requests, re
from bs4 import BeautifulSoup
from os import path
from random import choice

#Get Spotify Username
if not path.exists("SpotifyUserInfo.txt"): #So user doesn't have to get their Spotify ID every time it runs
    usrnm = open("SpotifyUserInfo.txt",'w')
    username = input("Your username is a near-incomprehensible string of numbers and letters that you'll never remember. \nTo find it, open Spotify and click on your user profile picture. You should see 'USER' and then your name underneath it, and then a circle with 3 dots in it. Click the circle, click 'Share', and then 'Copy Profile Link'. Paste that here.")
    username = username.replace('https://open.spotify.com/user/','')
    username = username.split('?',1)[0]
    usrnm.write(username)
    usrnm.close()
usrnm = open("SpotifyUserInfo.txt",'r')
username = usrnm.read()
usrnm.close()

cid ="CID" 
secret = "SECRET"

scope = 'user-library-read playlist-read-private playlist-modify-public'
token = util.prompt_for_user_token(username,scope,client_id=cid,client_secret=secret,redirect_uri='http://google.com/')

if token:
    sp = spotipy.Spotify(auth=token)
else:
    print("Can't get token for", username)

#------------We're in!----------------------
searchString = input("Create playlist based on which artist/band?")
result = sp.search(searchString, limit=5, offset=0, type='artist', market=None)
artistName = result['artists']['items'][0]['name']
artistID = result['artists']['items'][0]['id']

def getRelatedArtists(artistIDnum): #add 10 related artists IDs to a list
    relatedIDList = []
    relatedIDList.append(artistIDnum) #add original artist to list first
    relatedArtists = sp.artist_related_artists(artistID)
    for i in range(0,10): 
        relatedIDList.append(relatedArtists['artists'][i]['id'])
    return relatedIDList #returns list of 10 artistIDs
    
def getAllAlbumIDsforArtist(artistIDnum):#Return list of album IDs for the artist
    albumIDlist = []
    albumListResults = sp.artist_albums(artistIDnum, album_type=None, country=None, limit=15, offset=0)
    for i in range(len(albumListResults)):
        albumIDlist.append(albumListResults['items'][i]['id'])
    return albumIDlist
    
def getAllSongIDsForAlbum(albumIDnum): #return first 20 song ids from an album
    albumSongList = []
    albSongResults = sp.album_tracks(albumIDnum, limit=20, offset=0)
    for i in range(len(albSongResults)):
        try:
            albumSongList.append(albSongResults['items'][i]['id'])
        except:
            print("Couldn't add song")
    return albumSongList

def allSongsForArtist(artistIDnum):
    albIDs = [] #list of all album IDs
    albSongList = [] #list of all songs on an album (will reset once per album)
    artistSongsList = [] #list of all song IDs
    albIDs = getAllAlbumIDsforArtist(artistIDnum)
    #for each album ID get track ids
    for alb in albIDs:
        albSongList = getAllSongIDsForAlbum(alb)
        for songid in albSongList:
            artistSongsList.append(songid)
    return artistSongsList

#Add track to new playlist
def CreateAndFillPlaylist(PlaylistName):
    playlist_name_var = PlaylistName
    sp.user_playlist_create(username, playlist_name_var, public=True) #works!
    
    playlists = sp.user_playlists(username)
    for playlist in playlists['items']:
        if playlist['name'] == playlist_name_var:
            playlist_id = playlist['id']
            
    sp.user_playlist_add_tracks(username, playlist_id, megaList)
    print("Done! Playlist created!")

megaList = []
artistsList = []
theirSongs = []

artistsList = getRelatedArtists(artistID)

for arts in artistsList:
    song = ''
    i = 1
    songList = []
    songList = allSongsForArtist(arts)
    print(sp.artist(arts)['name'])
    while i < 3:
        song = choice(songList)
        if song not in megaList:
            print(' - ' + sp.track(song)['name'])
            megaList.append(song)
            i+=1

CreateAndFillPlaylist(artistName + " and Friends Mixtape")
