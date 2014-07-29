#!/opt/local/bin/python2.7
# -*- coding: utf-8 -*-
""" Coded by Iheanyi Ekechukwu

http://www.twitter.com/kwuchu
http://www.github.com/iheanyi

Feel free to use this in any way you wish. I made this just for fun.

Shout out to darkf for writing a helper function for parsing the JavaScript! """

import unicodedata
import os
import urllib2

from mutagen.mp3 import MP3
from mutagen.id3 import TIT2
from mutagen.easyid3 import EasyID3
import urllib2
import sys
import jsobj
from slugify import slugify


def parse_file(url):
    print "Starting the parsing for: " + url

    response = urllib2.urlopen(url)
    r = response.read()

    # embedBlock = r.text.split("var EmbedData = ")
    embedBlock = r.split("var EmbedData = ")

    embedStringBlock = embedBlock[1]
    # embedStringBlock = unicodedata.normalize(u'NFKD', embedStringBlock).encode('ascii', 'ignore')
    embedStringBlock = embedStringBlock.split("};")[0] + "};"
    embedStringBlock = jsobj.read_js_object("var EmbedData = %s" % str(embedStringBlock))



    embedData = embedStringBlock


    albumTitle = embedData['EmbedData']['album_title']

    # block = r.text.split("var TralbumData = ")
    block = r.split("var TralbumData = ")
    #print block[0]

    stringBlock = block[1]
    # stringBlock = unicodedata.normalize('NFKD', stringBlock).encode('ascii', 'ignore')
    stringBlock = stringBlock.split("};")[0] + "};"
    stringBlock = jsobj.read_js_object("var TralbumData = %s" % str(stringBlock))


    data = stringBlock
    # print data
    artistName = data['TralbumData']['artist']

    firstLetter = artistName[0]

    if not firstLetter.isalpha:
        firstLetter = "0"
    else:
        firstLetter = firstLetter.capitalize()

    if not os.path.exists("files"):
        os.makedirs("files")


    if not os.path.exists("files/" + firstLetter):
        if (firstLetter.isalpha):
            os.makedirs("files/" + firstLetter)

    if not os.path.exists("files/" + firstLetter + "/" + artistName):
        os.makedirs("files/" + firstLetter + "/" + artistName)

    tracks = data['TralbumData']['trackinfo']

    albumPath = albumTitle.replace(" ", "").replace("/", "").replace(".", "")

    albumPath = "files/" + firstLetter + "/" + artistName + "/" + albumPath
    if not os.path.exists("files/zips"):
        os.makedirs("files/zips")

    if not os.path.exists(albumPath):
        os.makedirs(albumPath)

    for each in tracks:
        if not os.path.exists(albumPath):
            os.makedirs(albumPath)
        songTitle = each['title'].replace(" ", "").replace(".", "")
        try:
            songURL = each['file']['mp3-128']
        except:
            continue
        
        trackNum = each['track_num']

        print "Now Downloading: " + each['title'], each['file']['mp3-128']

        req = urllib2.Request(songURL, headers={'User-Agent': "Magic Browser"})
        u = urllib2.urlopen(req)
        title = slugify(unicode(each['title']))
        f = open(albumPath+'/' + title +'.mp3', 'wb')

        meta = u.info()
        file_size = int(meta.getheaders("Content-Length")[0])
        file_size_dl = 0.0
        block_sz = 8192
        while True:
            buffer = u.read(block_sz)
            if not buffer:
                break

            file_size_dl += len(buffer)
            f.write(buffer)
            p = float(file_size_dl) / file_size
            status = r"[{1:2.2%}]".format(file_size_dl, p)
            # status = status + chr(8) * (len(status) + 1)
            sys.stdout.write("Download progress: %s%%   \r" % (status))
            sys.stdout.flush()


        f.close()
        print "Encoding . . . "
        audio = MP3(albumPath + '/' + title + '.mp3')
        audio["TIT2"] = TIT2(encoding=3, text=["title"])
        audio.save()
        audio = EasyID3(albumPath + '/' + title + '.mp3')
        audio["title"] = each['title'].decode('utf-8')
        audio["artist"] = unicode(artistName)
        audio["album"] = unicode(albumTitle)
        audio["tracknumber"] = trackNum
        audio.save()

        print "Done downloading " + songTitle


if len(sys.argv) == 2:
    url = sys.argv[1]
else:
    url = raw_input("Please enter the url of the album or song you wish to download: ")
# url = 'http://gileadmedia.bandcamp.com/album/heathen'
parse_file(url)
