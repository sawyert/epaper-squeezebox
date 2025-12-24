# show previous, current, next track on epaper from a raspberry pi zero

import urllib.request
import json
import os, sys, time

from PIL import Image, ImageDraw, ImageFont

def fetchTrackData():
    SQUEEZE_URL = 'http://headwell:9000/jsonrpc.js'
    RPC_BODY = {
        "id": 1, 
        "method": "slim.request", 
        "params": ["02:42:0a:dc:e6:6f", ["status", "0", "20", "tags:uBqal"]]
    }

    req = urllib.request.Request(SQUEEZE_URL, data=json.dumps(RPC_BODY).encode('utf-8'), method='POST')
    req.add_header('Content-Type', 'application/json')
    
    with urllib.request.urlopen(req) as fp:
        pageBytes = fp.read()
    
    squeezeData = json.loads(pageBytes.decode("utf8"))
    result = squeezeData.get('result', {})
    playlist_loop = result.get('playlist_loop', [])
    cur_index = result.get('playlist_cur_index')

    def get_track_dict(index):
        if index is not None and 0 <= index < len(playlist_loop):
            track = playlist_loop[index]
            return {
                "song": track.get('title', ''),
                "artist": track.get('artist', ''),
                "album": track.get('album', '')
            }
        return {"song": "", "artist": "", "album": ""}

    previousTrackDict = get_track_dict(None if cur_index is None else cur_index - 1)
    currentTrackDict = get_track_dict(cur_index)
    nextTrackDict = get_track_dict(None if cur_index is None else cur_index + 1)

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