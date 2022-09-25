import requests
import pandas as pd
from bs4 import BeautifulSoup
import json
import re

proxies = {
}

def getUser(user):

    userInfo = requests.get('https://soundcloud.com/{}/'.format(user), proxies=proxies, verify=False)
    userSoup = BeautifulSoup(userInfo.text, 'html.parser')
    userId = str(userSoup).split('https://api.soundcloud.com/users/')[1].split('"')[0]
    return userId


def userLikes(user):

    headers = {
    'Accept': 'application/json, text/javascript, */*; q=0.01',
    'Referer': 'https://soundcloud.com/',
    'Origin': 'https://soundcloud.com',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.121 Safari/537.36',
    'Authorization': 'OAuth 2-290287-109566302-rP3anBZUUFsMKf',
    }

    params = (
        ('limit', '1000'),
        ('app_version', '1557747132'),
        ('app_locale', 'en'),
    )

    userId = getUser(user)
    nextHref = 'https://api-v2.soundcloud.com/users/{}/likes'.format(userId)

    tracks = []
    playlists = []

    while nextHref != None:

        response = requests.get(nextHref, headers=headers, params=params, proxies=proxies, verify=False)
        jsonLikes = json.loads(response.text)

        userTracks = [x['track'] for x in jsonLikes['collection'] if 'track' in list(x.keys())]
        trackLabels = ['title','user','label_name','publisher_metadata','tag_list','genre','kind','permalink_url','likes_count']

        trackData = []
        for x in userTracks:
            trackInfo = [x.get(label) for label in trackLabels]
            trackData.append(trackInfo)

        userPlaylists = [y['permalink_url'] for y in [x['playlist'] for x in jsonLikes['collection'] if 'playlist' in list(x.keys())]]

        tracks.append(trackData)
        playlists.append(userPlaylists)

        nextHref = jsonLikes['next_href']


    return tracks


def getArtist(row):
    try:
        return row.get('artist')
    except:
        return

def getUsername(row):
    try:
        return row.get('username')
    except:
        return

def makeFrame(user):
    tracks = userLikes(user)

    likeFrame = pd.concat(pd.DataFrame(tracks[x]) for x in range(0, len(tracks)))
    likeFrame.columns = ['title','user','label_name','publisher_metadata','tag_list','genre','kind','song_url','likes_count']
    likeFrame['artist'] = likeFrame.publisher_metadata.map(getArtist)
    likeFrame['username'] = likeFrame.user.map(getUsername)
    likeFrame = likeFrame[['title','user','label_name','tag_list','genre','kind','artist','username','song_url','likes_count']]
    likeFrame['title_user'] = likeFrame['title'] + ' % '  + likeFrame['username']
    testData = likeFrame[['title_user','artist','song_url','likes_count']]

    return testData

# many artists have emoji's in thier names or song titles, removing as they dont add any value just headache

def removeEmoji(row):
    return row.encode('ascii', 'ignore').decode('ascii').strip()

def filtData(user):
    testData = makeFrame(user)

    testData.title_user = testData.title_user.map(removeEmoji)
    testData['title_user'] = testData['title_user'].map(lambda x : x.upper())
    testData['artist'] = testData['artist'].map(lambda x :x if pd.isnull(x) else x.upper())

    return testData

def findRemix(x):

    if (str(x).count('(') == 1) & (' REMIX' in x):
        return x[x.find("(")+1:x.find("REMIX")]
    elif (str(x).count('[') == 1) & (' REMIX' in x):
        return x[x.find("[")+1:x.find("REMIX")]
    elif (str(x).count('(') == 1) & (' RMX' in x):
        return x[x.find("(")+1:x.find(" RMX")]
    elif (str(x).count('[') == 1) & (' RMX' in x):
        return x[x.find("[")+1:x.find(" RMX")]
    elif (str(x).count('(') == 1) & (' VIP)' in x):
        return x[x.find("(")+1:x[0].find(" VIP)")]
    elif (str(x).count('[') == 1) & (' VIP)' in x):
        return x[x.find("[")+1:x[0].find(" VIP)")]
    elif (str(x).count('(') == 1) & (' FLIP' in x):
        return x[x.find("(")+1:x.find(" FLIP")]
    elif (str(x).count('[') == 1) & (' FLIP' in x):
        return x[x.find("[")+1:x.find(" FLIP")]
    else:
        return

# For electronic artists, I am personally more interested in the artist who made the remix and not the original artist

def artistSong(row):

    # if there is only 1 '-' in the string and this -
    # comes BEFORE the % username, typically what is to the left of the dash is the artist
    # also strings with FT (featured artists) typicall follow the logic "song name (ft artist) - Artist"..
    # artists are found on the oposite side of the '-' where 'FEAT/FT lies'

    if row.trueArtists is None:
        if (row.title_user.count('-') == 1) & (row.title_user.find('-') < row.title_user.find('%')):
            if 'FT.' in row.title_user:
                if row.title_user.find('FT.') - row.title_user.find('-') > 0:
                    return row.title_user.split('-')[0].split('%')[0].strip()
                    print(row.title_user)
                else:
                    return row.title_user.split('-')[1].split('%')[0].strip()
                    print(row.title_user, row.title_user.split('-')[1].split('%')[0].strip())

            if 'FEAT' in row.title_user:
                if row.title_user.find('FEAT') - row.title_user.find('-') > 0:
                    return row.title_user.split('-')[0].split('%')[0].strip()
                    print(row.title_user)
                else:
                    return row.title_user.split('-')[1].split('%')[0].strip()
                    print(row.title_user, row.title_user.split('-')[1].split('%')[0].strip())
            else:
                return row.title_user.split('-')[0].strip()
        else:
            return row.trueArtists
    else:
        return row.trueArtists

def artistMatch(row):
    # if the username matches the artist name, I am confident that is the Artist
    if row.trueArtists is None:
        # don't overwrite existing artist extractions
        user = row.title_user.split('%')[1].strip()
        if user == row.artist:
            return row.artist
        else:
            return row.trueArtists
    else:
        return row.trueArtists

# a lot of times, if a track or a mix is reposted by a label, or radio station etc it can be very hard to tell the artist name, lets just omit these
# otherwise, its a good bet the username is actually the artist name as well
def omitReposts(row):
    if row.trueArtists is None:
        counter = 0
        for x in ['MIX','RECORDS','RADIO','LABEL','COLLECTIVE','GUEST','RECORDINGS','RECORD','[',']','(',')']:
            if x in row.title_user:
                counter += 1
            else:
                continue
        if (row.trueArtists is None) & (counter == 0):
            return row.title_user.split('%')[1].strip()
        else:
            return row.trueArtists
    else:
        return row.trueArtists

# split multiple artists into lists of individual artists
def splitArtists(row):
    if row is not None:
        return re.split('\s+&+\s|\s+X+\s|\s+x+\s|,', row)

def mapFilters(user):

    testData = filtData(user)

    testData['trueArtists'] = testData.title_user.map(findRemix)
    testData['trueArtists'] = testData.apply(artistSong, axis=1)
    testData['trueArtists'] = testData.apply(artistMatch, axis=1)
    testData['trueArtists'] = testData.apply(omitReposts, axis=1)
    testData['trueArtistsSplit'] = testData['trueArtists'].map(splitArtists)

    indvArtists = []
    for row in testData.values:
        try:
            for artist in row[5]:
                info = (artist.strip().upper(), row[3], row[2])
                indvArtists.append(info)
        except:
            pass


    songCounts = pd.DataFrame(indvArtists)
    songCounts.columns = ['Artist','like_count','song_url']
    songCounts['size'] = songCounts.groupby('Artist')['Artist'].transform('size')


    userLikes = []
    for x in testData['trueArtistsSplit']:
        if x is None:
            pass
        elif len(str(x)) >3:
            for y in x:
                userLikes.append(y.strip())

    return [list(set(userLikes)),songCounts]