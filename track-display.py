# show previous, current, next track on epaper from a raspberry pi zero

import urllib.request

from PIL import Image, ImageDraw, ImageFont
from bs4 import BeautifulSoup
from waveshare_epd import epd5in83_V2

SQUEEZE_URL = 'http://wellhead:9002/status.html?player=02:42:47:ab:fd:11' # Master in kitchen
LIST_INDEX_ID_PREFIX = 'playlistSong'
PLAYLIST_ITEM_DETAILS_CLASS = 'playlistSongDetail'

fp = urllib.request.urlopen(SQUEEZE_URL)
pageBytes = fp.read()

squeezeHtml = pageBytes.decode("utf8")
fp.close()

soup = BeautifulSoup(squeezeHtml, 'html.parser')
playList = soup.find(id='playList')
currentTrack = soup.find("div", class_="currentSong")

currentTrackNumber = int(currentTrack.get('id')[len(LIST_INDEX_ID_PREFIX):])
previousTrackNumber = currentTrackNumber - 1
nextTrackNumber = currentTrackNumber + 1

previousTrack = soup.find("div", id='%s%d' % (LIST_INDEX_ID_PREFIX, previousTrackNumber))
nextTrack = soup.find("div", id='%s%d' % (LIST_INDEX_ID_PREFIX, nextTrackNumber))

songDetails = currentTrack.find_all("div", class_=PLAYLIST_ITEM_DETAILS_CLASS)
song = songDetails[0].text.strip()
artist = songDetails[1].text.strip()
album = songDetails[2].text.strip()

previousSongDetails = previousTrack.find_all("div", class_=PLAYLIST_ITEM_DETAILS_CLASS)
previousSong = previousSongDetails[0].text.strip()
previousArtist = previousSongDetails[1].text.strip()
previousAlbum = previousSongDetails[2].text.strip()

nextSongDetails = nextTrack.find_all("div", class_=PLAYLIST_ITEM_DETAILS_CLASS)
nextSong = nextSongDetails[0].text.strip()
nextArtist = nextSongDetails[1].text.strip()
nextAlbum = nextSongDetails[2].text.strip()

print ("%s %s %s" % (previousSong, previousArtist, previousAlbum))
print ("%s %s %s" % (song, artist, album))
print ("%s %s %s" % (nextSong, nextArtist, nextAlbum))

epd = epd5in83_V2.EPD()
epd.init()

FONT_FILE = "coolvetica rg.otf"

font24 = ImageFont.truetype(FONT_FILE, 24)
font18 = ImageFont.truetype(FONT_FILE, 18)

Himage = Image.new('1', (epd.width, epd.height), 255)  # 255: clear the frame
draw = ImageDraw.Draw(Himage)

draw.text((10, 0), artist, font = font18, fill = 0)
draw.text((10, 20), song, font = font24, fill = 0)
draw.text((10, 30), album, font = font18, fill = 0)
epd.display(epd.getbuffer(Himage))

epd5in83_V2.epdconfig.module_exit()