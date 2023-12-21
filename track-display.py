# show previous, current, next track on epaper from a raspberry pi zero

import urllib.request
import os, sys, time

from PIL import Image, ImageDraw, ImageFont
from bs4 import BeautifulSoup

def fetchTrackData():
    SQUEEZE_URL = 'http://wellhead:9002/status.html?player=02:42:0a:dc:e6:6f' # Master in kitchen
    LIST_INDEX_ID_PREFIX = 'playlistSong'
    PLAYLIST_ITEM_DETAILS_CLASS = 'playlistSongDetail'

    fp = urllib.request.urlopen(SQUEEZE_URL)
    pageBytes = fp.read()

    squeezeHtml = pageBytes.decode("utf8")
    fp.close()

    soup = BeautifulSoup(squeezeHtml, 'html.parser')
    currentTrack = soup.find("div", class_="currentSong")

    currentTrackNumber = int(currentTrack.get('id')[len(LIST_INDEX_ID_PREFIX):])
    previousTrackNumber = currentTrackNumber - 1
    nextTrackNumber = currentTrackNumber + 1

    previousTrack = soup.find("div", id='%s%d' % (LIST_INDEX_ID_PREFIX, previousTrackNumber))
    nextTrack = soup.find("div", id='%s%d' % (LIST_INDEX_ID_PREFIX, nextTrackNumber))

    songDetails = currentTrack.find_all("div", class_=PLAYLIST_ITEM_DETAILS_CLASS)
    currentSong = songDetails[0].text.strip()
    currentArtist = songDetails[1].text.strip()
    currentAlbum = songDetails[2].text.strip()

    previousSongDetails = previousTrack.find_all("div", class_=PLAYLIST_ITEM_DETAILS_CLASS)
    previousSong = previousSongDetails[0].text.strip()
    previousArtist = previousSongDetails[1].text.strip()
    previousAlbum = previousSongDetails[2].text.strip()

    nextSongDetails = nextTrack.find_all("div", class_=PLAYLIST_ITEM_DETAILS_CLASS)
    nextSong = nextSongDetails[0].text.strip()
    nextArtist = nextSongDetails[1].text.strip()
    nextAlbum = nextSongDetails[2].text.strip()

    previousTrackDict = {
        "song": previousSong,
        "artist": previousArtist,
        "album": previousAlbum
    }

    currentTrackDict = {
        "song": currentSong,
        "artist": currentArtist,
        "album": currentAlbum
    }

    nextTrackDict = {
        "song": nextSong,
        "artist": nextArtist,
        "album": nextAlbum
    }

    returnDict = {
        "previous": previousTrackDict,
        "current": currentTrackDict,
        "next": nextTrackDict
    }
    
    return returnDict

def updateDisplay(data, epd):
    FONT_FILE = "coolvetica rg.otf"
    font30 = ImageFont.truetype(FONT_FILE, 30)
    font40 = ImageFont.truetype(FONT_FILE, 40)
    font60 = ImageFont.truetype(FONT_FILE, 60)

    Himage = Image.new('1', (epd.width, epd.height), 255)  # 255: clear the frame
    draw = ImageDraw.Draw(Himage)

    draw.text((15, 20), data['previous']['artist'], font = font30, fill = 0)
    draw.text((15, 50), data['previous']['song'], font = font40, fill = 0)
    draw.text((15, 90), data['previous']['album'], font = font30, fill = 0)

    draw.text((15, 170), data['current']['artist'], font = font40, fill = 0)
    draw.text((15, 210), data['current']['song'], font = font60, fill = 0)
    draw.text((15, 280), data['current']['album'], font = font40, fill = 0)

    draw.text((15, 360), data['next']['artist'], font = font30, fill = 0)
    draw.text((15, 390), data['next']['song'], font = font40, fill = 0)
    draw.text((15, 430), data['next']['album'], font = font30, fill = 0)

    epd.display(epd.getbuffer(Himage))


sys.path.append('lib')
from waveshare_epd import epd5in83_V2

epd = epd5in83_V2.EPD()
epd.init()

oldTrackData = None
while(True):
    trackData = fetchTrackData()
    if trackData != oldTrackData:
        oldTrackData = trackData
        updateDisplay(trackData, epd)
    time.sleep(20)

# epd5in83_V2.epdconfig.module_exit()    