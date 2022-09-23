import pycrfsuite
# import pycrfsuite
import pandas as pd
import requests
# import numpy as np
from datetime import datetime
from dateutil.parser import parse
from bs4 import BeautifulSoup
import json
import itertools
from urllib.parse import urljoin
import warnings
warnings.filterwarnings("ignore")
import nltk
import re
from concurrent import futures
import concurrent.futures
from concurrent.futures import ThreadPoolExecutor
from collections import defaultdict

tagger = pycrfsuite.Tagger()
tagger.open(r'/Users/johnschlafly/Desktop/concertFinderDjango-master/concert/home/scripts/crf.model')


proxies = {
}

def getUser(user):

    userInfo = requests.get('https://soundcloud.com/{}/'.format(user), proxies=proxies, verify=False)
    userSoup = BeautifulSoup(userInfo.text, 'html.parser')
    userId = str(userSoup).split('https://api.soundcloud.com/users/')[1].split('"')[0]
    return userId


# In[125]:


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

# def mishScrape():
#     mishQuery = requests.get('https://mishawaka.ticketforce.com/include/widgets/events/EventList.asp?category=&page=1', proxies = proxies, verify=False)
#     mishJson = mishQuery.json()

#     mishData = []
#     for event in mishJson['swEvent']:
#         headline = event['Event']
#         desc = event['Description']
#         date = event['PerformanceStart']
#         id_ = event['upcomingInfo']['EventID']
#         link = 'https://mishawaka.ticketforce.com/eventperformances.asp?evt={0}'.format(id_)
#         pic = 'https://mishawaka.ticketforce.com/uplimage/' + event['Img_1']

#         descSoup = BeautifulSoup(desc, 'html.parser')
#         try:
#             info = descSoup.find('span', {'style':'font-size: 18pt; color: #ff6600;'}).text
#         except:
#             try:
#                 info = descSoup.find('span', {'style':'color: #ff6600;'}).text
#             except:
#                 info = headline

#         res = (info, date,link, 'Mishawaka Amphitheatre', pic)
#         mishData.append(res)

#     mishFrame = pd.DataFrame(mishData)
#     mishFrame.columns = ['Artist','Date','Link','Venue','picLink']
#     mishFrame['Date'] = mishFrame['Date'].map(lambda x : x.split('T')[0])
#     mishFrame['Date'] = pd.to_datetime(mishFrame['Date'])
#     mishFrame['Date'] = mishFrame.Date + pd.Timedelta(days=-1)
#     mishFrame['Date'] = mishFrame['Date'].map(lambda x : str(x))

#     def splitArtists(row):
#         return [x.strip() for x in re.split('w/|with|,|special guests', row) if x != ' ']
#     mishFrame['FiltArtist'] = mishFrame['Artist'].map(splitArtists)

#     return mishFrame




def blue_bird_scrape():

    blue_bird = requests.get('https://www.bluebirdtheater.net/events', proxies = proxies, verify=False)
    bird_soup = BeautifulSoup(blue_bird.text, 'html.parser')
    blue_bird_events = list(zip(list(filter(None, [z.strip() for z in [y[0] for y in [x.contents for x in bird_soup.findAll('a', {'title':"More Info"})]]])),[x.contents[2].strip() for x in bird_soup.findAll('span', {'class':"date"})],[x['href'] for x in bird_soup.findAll('a',{'class':'btn-tickets accentBackground widgetBorderColor secondaryColor tickets status_1'})]))
    blue_bird_events = pd.DataFrame(blue_bird_events)
    blue_bird_events['Venue'] = 'Blue Bird'
    blue_bird_events.columns = ['Artist','Date','Link','Venue']

    def splitArtists(row):
        return [x.strip() for x in re.split('/', row) if (x is not None) & (x != '')]

    blue_bird_events['FiltArtist'] = blue_bird_events['Artist'].map(splitArtists)

    return blue_bird_events

def ogden_scrape():

    ogden = requests.get('https://www.ogdentheatre.com/events', proxies = proxies, verify=False)
    ogden_soup = BeautifulSoup(ogden.text, 'html.parser')
    ogden_events = list(zip(list(filter(None, [z.strip() for z in [y[0] for y in [x.contents for x in ogden_soup.findAll('a', {'title':"More Info"})]]])),[x.contents[2].strip() for x in ogden_soup.findAll('span', {'class':"date"})],[x['href'] for x in ogden_soup.findAll('a',{'class':'btn-tickets accentBackground widgetBorderColor secondaryColor tickets status_1'})]))
    ogden_events = pd.DataFrame(ogden_events)
    ogden_events['Venue'] = 'Ogden'
    ogden_events.columns = ['Artist','Date','Link','Venue']


    def splitArtists(row):
        return [x.strip() for x in re.split('Presents|:', row) if (x is not None) & (x != '')]

    ogden_events['FiltArtist'] = ogden_events['Artist'].map(splitArtists)

    return ogden_events

def first_bank_scrape():

    first_bank = requests.get('https://www.1stbankcenter.com/events', proxies = proxies, verify=False)
    bank_soup = BeautifulSoup(first_bank.text, 'html.parser')
    first_bank_events = list(zip(list(filter(None, [z.strip() for z in [y[0] for y in [x.contents for x in bank_soup.findAll('a', {'title':"More Info"})]]])),[x.contents[2].strip() for x in bank_soup.findAll('span', {'class':"date"})],[x['href'] for x in bank_soup.findAll('a',{'class':'btn-tickets accentBackground widgetBorderColor secondaryColor tickets status_1'})]))
    first_bank = pd.DataFrame(first_bank_events)
    first_bank['Venue'] = '1st Bank'
    first_bank.columns = ['Artist','Date','Link','Venue']

    def splitArtists(row):
        return [x.strip() for x in re.split('/| \d+', row) if (x is not None) & (x != '')]

    first_bank['FiltArtist'] = first_bank['Artist'].map(splitArtists)

    return first_bank



# def fox_scrape():



def cervantes_scrape():


    cookies = {
    '_fbp': 'fb.1.1625971576023.279520537',
    'deviceDetect_com.intellimark.util.DeviceDetector': 'false:::true:::1',
    'JSESSIONID': '5FC68327F8E62DFCF586DEDCBD5168A9',
    'BIGipServerwww.etix.com-HTTPS': '973738156.47873.0000',
    '_gid': 'GA1.2.1370894608.1626375973',
    '_ga_G4K0DX8L5Y': 'GS1.1.1626375970.7.1.1626376016.0',
    '_ga': 'GA1.2.893052237.1625971420',
    }

    headers = {
        'Connection': 'keep-alive',
        'sec-ch-ua': '" Not;A Brand";v="99", "Google Chrome";v="91", "Chromium";v="91"',
        'Accept': 'application/json, text/javascript, */*; q=0.01',
        'X-Requested-With': 'XMLHttpRequest',
        'sec-ch-ua-mobile': '?0',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36',
        'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
        'Origin': 'https://www.etix.com',
        'Sec-Fetch-Site': 'same-origin',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Dest': 'empty',
        'Referer': 'https://www.etix.com/ticket/online3/calendar.jsp?organization_id=6122',
        'Accept-Language': 'en-US,en;q=0.9',
    }

    data = {
      'queryString': 'language=en&country=US&organization_id=6122'
    }

    responses = []

    for x in range(1, 12):

        response = requests.post(f'https://www.etix.com/ticket/json/calendar/organization/6122/2021/{x}', headers=headers, cookies=cookies, data=data)
        responses.append(response.json())


    cervShows = []

    for x in responses:

        month = x['month']
        year = x['year']

        for event in x['dates']:

            showDate = str(month) + '/' + str(event['date']) +'/' + str(year)

            names = [x['name'] for x in event['activities']]
            links = [x['buyUrl'] for x in event['activities']]

            shows = [(i,j, showDate) for i, j in zip(names, links)]
            for show in shows:

                cervShows.append(show)

    cervFrame = pd.DataFrame(cervShows)

    cervFrame.columns = ['Artist','Link','Date']

    cervFrame['Venue'] = 'Cervantes'

    cervFrame['Date'] = pd.to_datetime(cervFrame['Date'])

    cervFrame = cervFrame[cervFrame['Date'] >= datetime.today().strftime('%Y-%m-%d')]

    cervParse = cervFrame

    def shift(row):

        if 'SHIFT Ft.' in row:
            return row.split('SHIFT Ft.')[1]
        else:
            return row

    cervParse['EventTitle'] = cervParse['Artist'].map(lambda x : ' , '.join(x.split(',')))
    cervParse['EventTitle'] = cervParse['Artist'].map(lambda x : ' ( '.join(x.split('(')))
    cervParse['EventTitle'] = cervParse['Artist'].map(lambda x : ' ) '.join(x.split(')')))
    cervParse['EventTitle'] = cervParse['Artist'].map(shift)



    def POStag(row):
        data = []
        tokens = [event for event in row.split()]
        # for every token in the event title, tag with a Part Of Speach label from the NLTK library
        tagged = nltk.pos_tag(tokens)

        return tagged


    cervParse['POS'] = cervParse.EventTitle.map(POStag)


    #     cervParse['POS'] = cervParse['labeled'].map(POStags)
    #     cervParse['POS'] = cervParse['POS'].map(lambda x : x[0])

    #     data = cervParse['POS'].tolist()

    def word2features(doc, i):

        # create features for training based on charchteristics of the word, and its surrounding words/ charachters

        word = doc[i][0]
        postag = doc[i][1]
        features = [
            'word.lower=' + word.lower(),
            'bias',
            'postag=' + postag,
            'word.isupper=%s' % word.isupper(),
            'word.istitle=%s' % word.istitle()
        ]

        if i > 0:
            word1 = doc[i-1][0]
            postag1 = doc[i-1][1]
            features.extend([
                '-1:word.lower=' + word1.lower(),
                '-1:postag=' + postag1,
                '-1:postag[:2]=' + postag1[:2],
                '-1:word.istitle=%s' % word1.istitle(),
                '-1:word.isupper=%s' % word1.isupper()

            ])

        else:
            features.append('BOS')

        if i < len(doc)-1:
            word1 = doc[i+1][0]
            postag1 = doc[i+1][1]
            features.extend([
                '+1:word.lower=' + word1.lower(),
                '+1:postag=' + postag1,
                '+1:postag[:2]=' + postag1[:2],
                '+1:word.istitle=%s' % word1.istitle(),
                '+1:word.isupper=%s' % word1.isupper()
            ])
        else:
            features.append('EOS')

        return features

    # A function for extracting features in documents
    def extract_features(doc):
        return [word2features(doc, i) for i in range(len(doc))]

    # A function fo generating the list of labels for each document
    def get_labels(doc):
        return [label for (token, postag, label) in doc]

    cervParse['features'] = cervParse['POS'].map(lambda x : extract_features(x))
    # extract features for every event title

    cervParse['preds'] = cervParse.features.map(lambda x : [tagger.tag(x)])
    # map trained model the features of each event title
    cervParse['toks'] = cervParse.POS.map(lambda x: [x[0] for x in x])
    # get prediction tags and word tokens into lists so they can be combined

    def zipper(row):
        return [(x,y) for x,y in list(zip(row.toks, row.preds[0])) if y in ['A','S']]

    cervParse['artistPreds'] = cervParse.apply(zipper, axis=1)

    def combine(row):
        results = [(x,y) for x,y in list(zip(row.toks, row.preds[0])) if y in ['A','S']]
        artist = []
        for x in results:
            if x[1] == 'A':
                artist.append(x[0])
            else:
                artist.append(',')
        return ', '.join([y for y in [x.strip() for x in ' '.join(artist).split(',')] if y != ''])

    cervParse['predictions'] = cervParse.apply(combine, axis=1)
    cervParse['predictions'] = cervParse['predictions'].map(lambda x : [x for x in x.split(',')])
    cervArtistFrame = cervParse[['Artist','predictions','Date','Venue','Link']]
    cervArtistFrame.columns = ['Artist','FiltArtist','Date','Venue','Link']
    cervArtistFrame = cervArtistFrame[cervArtistFrame['Venue'] != 'RED ROCKS AMPHITHEATRE']

    cervArtistFrame = cervArtistFrame[['Artist','Date','FiltArtist','Link','Venue']]

    return cervArtistFrame


def gothic_scrape():

    gothic = requests.get('https://www.gothictheatre.com/events', proxies = proxies, verify=False)
    gothic_soup = BeautifulSoup(gothic.text, 'html.parser')
    gothic_events = gothic_soup.findAll('body', {'id':"events_axs"})

    gothic_artists = []
    gothic_dates = []
    links = []

    for x in gothic_events[0].findAll('a',{'title':"More Info"}):
        gothic_artists.append(x.contents[0].strip())

    for x in gothic_events[0].findAll('span',{'class':"date"}):
        gothic_dates.append(x.contents[2].strip())

    for x in gothic_events[0].findAll('a',{'class':'btn-tickets accentBackground widgetBorderColor secondaryColor tickets status_1'}):
        links.append(x['href'])

    gothic_artists = list(filter(None, gothic_artists))

    gothic_frame = pd.DataFrame(list(zip(gothic_artists, gothic_dates,links)))
    gothic_frame['Venue'] = 'Gothic'
    gothic_frame.columns = ['Artist','Date','Link','Venue']

    def splitArtists(row):
        return [x.strip() for x in re.split('Feat.|\s/', row) if (x is not None) & (x != '')]

    gothic_frame['FiltArtist'] = gothic_frame['Artist'].map(splitArtists)


    return gothic_frame


def summitScrape():

    today = datetime.today().strftime('%Y-%m-%d')
    response = requests.get('https://www.summitdenver.com/api/EventCalendar/GetEvents?startDate=7/10/2021&endDate=7/1/2023&venueIds=246789&limit=20&offset=1&genre=&artist=&priceLevel=&offerType=STANDARD', proxies = proxies, verify=False)

    summitResponse = response.json()
    summitJson = json.loads(summitResponse)

    summitInfo = []
    for x in summitJson['result']:
        artists = x['title']
        dates = x['eventDate'].split(' ')[0]
        venue = x['venueName']
        link = x['ticketUrl']
        picLink = x['eventImageLocation']
        info = (artists, dates,link, venue,picLink)
        summitInfo.append(info)

    summitFrame = pd.DataFrame(summitInfo)
    summitFrame.columns = ['Artist','Date','Link','Venue','picLink']
    def splitArtists(row):
        return [x.strip() for x in re.split(',|:|\*|-|\+|featuring| x| X', row) if (x is not None) & (x != '')]
    summitFrame['FiltArtist'] = summitFrame['Artist'].map(splitArtists)

    return summitFrame

def bellyScrape():

    headers = {
        'authority': 'bellyupaspen.com',
        'cache-control': 'max-age=0',
        'sec-ch-ua': '" Not;A Brand";v="99", "Google Chrome";v="91", "Chromium";v="91"',
        'sec-ch-ua-mobile': '?0',
        'upgrade-insecure-requests': '1',
        'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36',
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'sec-fetch-site': 'none',
        'sec-fetch-mode': 'navigate',
        'sec-fetch-user': '?1',
        'sec-fetch-dest': 'document',
        'accept-language': 'en-US,en;q=0.9',
        'cookie': 'modal_cookie=yes',
    }

    bellyUp = requests.get('https://bellyupaspen.com/events/', headers=headers)

    bellySoup = BeautifulSoup(bellyUp.text, 'html.parser')

    data = [(event.find('h3',{'class':'event-name'}).text.strip(), event.find('span',{'class':'date'}).text.strip(), event.find('a', href=True)['href'])for event in bellySoup.findAll('div', {'class':'event-details'})]

    df = pd.DataFrame(data)
    df.columns = ['Artist','Date','Link']
    df['Venue'] = 'BellyUp Aspen'
    bellyFrame = df
    bellyFrame['FiltArtist'] = bellyFrame['Artist']

    def bellyList(row):

        return [row.strip()]

    bellyFrame['FiltArtist'] =  bellyFrame['FiltArtist'].map(bellyList)

    return bellyFrame


def redRocksScrape():

    red_rocks = requests.get('https://www.redrocksonline.com/wp-json/clique/v1/get_calendar_events_range?start=2021-06-27T00%3A00%3A00&end=2021-08-01T00%3A00%3A00&timeZone=America%2FDenver')

    redRocksJson = red_rocks.json()

    redFrame = pd.DataFrame([(x['title'],x['start'].split('T')[0],x['url']) for x in redRocksJson])

    redFrame.columns = ['Artist','Date','Link']

    redFrame['Venue'] = 'Red Rocks'

    def splitArtists(row):
        return [x.strip() for x in re.split(';|:|,|,with|/|special guest|with|-| \d+|presents', row) if x != '']

    redFrame['FiltArtist'] = redFrame['Artist'].map(splitArtists)

    return redFrame



# def larimer_scrape():

#     larimer = requests.get('https://www.larimerlounge.com/calendar/', proxies=proxies, verify=False)
#     larimer_soup = BeautifulSoup(larimer.text, 'html.parser')
#     lamimer_calendar = larimer_soup.findAll('td')

#     larimer_artists = []
#     for x in lamimer_calendar:
#         artist = "\n".join([img['alt'] for img in x.find_all('img', alt=True)])
#         larimer_artists.append(artist)

#     larimer_dates = []
#     for index, x in enumerate(lamimer_calendar):
#         date = x.findAll('span', {'class':"value-title"})
#         try:
#             larimer_dates.append((index, str(date).split('<span class="value-title" title="')[1].split('T')[0]))
#         except:
#             pass

#     artists = pd.DataFrame(larimer_artists).reset_index()
#     dates = pd.DataFrame(larimer_dates)
#     larimer_info = dates.merge(artists, left_on=0, right_on='index', how='inner')
#     larimer_info = larimer_info[[1,'0_y']]
#     larimer_info['Venue'] = 'Larimer Lounge'

#     larimer_frame = larimer_info[larimer_info['0_y'] != '']
#     larimer_frame.columns = ['Date','Artist','Venue']
#     larimer_frame = larimer_frame[['Artist','Date','Venue']]

#     def splitArtists(row):
#         return [x.strip() for x in re.split('\\+|\(ft.|\(|\)', row) if (x is not None) & (x != '')]

#     larimer_frame['FiltArtist'] = larimer_frame['Artist'].map(splitArtists)

#     larimer_frame['Link'] = 'No Link at this time, sorry!'
#     larimer_frame = larimer_frame[['Artist','Date','FiltArtist','Link','Venue']]

#     return larimer_frame

def missionScrape():

    mission = requests.get('https://missionballroom.com/data/events-index.json', proxies = proxies, verify = False)
    mission = mission.json()

    missionData = []
    for x in mission:
        date = x['date']
        artist1 = x['title']
        artist2 = x['subtitle']
        if artist2 == '':
            artist = artist1
        else:
            artist = artist1 + ',' + artist2

        venue = 'Mission Ballroom'
        ticketLink = x['tickets']
        info = (artist, date, ticketLink, venue)
        missionData.append(info)

    missionFrame = pd.DataFrame(missionData)
    missionFrame.columns = ['Artist','Date','Link','Venue']

    def splitArtists(row):
        return [x.strip() for x in re.split('&|WITH|,|/|with| x| X', row) if x not in ['',' ']]
    missionFrame['FiltArtist'] = missionFrame['Artist'].map(splitArtists)

    return missionFrame


# def nightOutScrape():
#
#     headers = {
#         'authority': 'nightout.com',
#         'sec-ch-ua': '" Not;A Brand";v="99", "Google Chrome";v="91", "Chromium";v="91"',
#         'accept': 'application/json',
#         'authorization': 'OAuth t8poqrlce5r2vrw35pw5gfgfur5fj14',
#         'sec-ch-ua-mobile': '?0',
#         'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36',
#         'origin': 'https://coclubs.com',
#         'sec-fetch-site': 'cross-site',
#         'sec-fetch-mode': 'cors',
#         'sec-fetch-dest': 'empty',
#         'referer': 'https://coclubs.com/',
#         'accept-language': 'en-US,en;q=0.9',
#     }
#
#     params = (
#         ('starting', '1627797600'),
#         ('ending', '1630907999'),
#         ('details', 'preview'),
#         ('organization_ids', '18858,17588,18860,18866,47457,52641,52730'),
#     )
#
#     response = requests.get('https://nightout.com/api/events/', headers=headers, params=params)
#
#     #NB. Original query string below. It seems impossible to parse and
#     #reproduce query strings 100% accurately so the one below is given
#     #in case the reproduced version is not "correct".
#     # response = requests.get('https://nightout.com/api/events/?starting=1627797600&ending=1630907999&details=preview&organization_ids=18858,17588,18860,18866', headers=headers)
#
#
#     nightOut = response.json()
#
#     nightOutShows = [(x['organization']['name'],x['title'],x['links']['public'],x['start_time']) for x in nightOut]
#
#     nightOutFrame = pd.DataFrame(nightOutShows)
#
#     nightOutFrame.columns = ['Venue','Artist','Link','Date']


def nightOutScrape():
        headers = {
            'authority': 'api.ticketsauce.com',
            'sec-ch-ua': '" Not;A Brand";v="99", "Google Chrome";v="97", "Chromium";v="97"',
            'accept': 'application/json',
            'sec-ch-ua-mobile': '?0',
            'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.99 Safari/537.36',
            'sec-ch-ua-platform': '"macOS"',
            'origin': 'https://coclubs.com',
            'sec-fetch-site': 'cross-site',
            'sec-fetch-mode': 'cors',
            'sec-fetch-dest': 'empty',
            'referer': 'https://coclubs.com/',
            'accept-language': 'en-US,en;q=0.9',
        }

        params = (
            ('access_token', '15c7b54a8f398e925302184edf1dba7b3bde298a'),
            ('active_only', 'true'),
            ('privacy_type', 'public'),
            ('start_after', ''),
        )

        response = requests.get('https://api.ticketsauce.com/v2/events', headers=headers, params=params)

        concerts = pd.DataFrame([x['Event'] for x in response.json()])
        concerts = concerts[['location', 'name','event_url', 'start_utc']]
        concerts.columns = ['Venue','Artist','Link','Date']


        def artistSplit(row):

            if row.Venue in ['The Black Box','The Lounge','Bar Standard']:

                return [x.strip() for x in re.split('&|(Master Class)|presents|,|:|;|\sand\s|ft.|b2b|\(|\)', row.Artist) if (x is not None) & (x != '')]

            elif row.Venue == 'Club Vinyl':

                # return [x.strip() for x in re.split('BASS OPS:|\\+|:|at|-|\(|\)|', row.Artist) if (x is not None) & (x != '')]
                return [x.strip() for x in re.split('BASS OPS:|\\+', row.Artist)  if (x is not None) & (x != '')]

            elif row.Venue == 'The Church Nightclub':

                return [x.strip() for x in re.split('\+|:|\(|\)', row.Artist) if (x is not None) & (x != '')]

            elif row.Venue in ['Milk', 'Milk Bar']:

                return [row.Artist]



        concerts['FiltArtist'] = concerts.apply(artistSplit, axis= 1)
        concerts['Date'] = concerts['Date'].map(lambda x : x.split('T')[0])

        return concerts


functions = ['cervantes_scrape()','bellyScrape()','redRocksScrape()','nightOutScrape()','missionScrape()','blue_bird_scrape()','ogden_scrape()','first_bank_scrape()','gothic_scrape()','summitScrape()']


result = []
rang = range(0,len(functions))


def sf_query(run):
            try:
                result.append(eval(functions[run]))
            except:
                web_hook = 'https://hooks.slack.com/services/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'
                slack_msg = {'text':f'There was an error scrapiing (web app) -- {functions[run]}'}
                requests.post(web_hook, data = json.dumps(slack_msg))
                pass
                # print('error', functions[run])
def main_2():
    with concurrent.futures.ThreadPoolExecutor(max_workers=20) as executor:
        results = [executor.submit(sf_query,run) for run in rang]


def scrapeVenues():
    execute = main_2()
    denver_concerts = pd.concat(result)
#     denver_concerts['Date'] = denver_concerts['Date'].map(lambda x : parse(x).date())

    return denver_concerts

concertDict = defaultdict(list)
def eventDict():
    denver_concerts = scrapeVenues()
    for artists in denver_concerts.values:
        if artists[4] is None:
            pass
        else:
            for artist in artists[4]:
                if artist.strip().upper() == '':
                    pass
                else:
                    concertDict[artist.strip().upper()].append(artists[0])
                    concertDict[artist.strip().upper()].append(artists[1])
                    concertDict[artist.strip().upper()].append(artists[3])
                    concertDict[artist.strip().upper()].append(artists[2])
    return denver_concerts



def findMatches(user):


    denver_concerts = eventDict()
    userLikes = mapFilters(user)

    matchResults = []
    for x in userLikes[0]:
        try:
            shows = concertDict[x]
            if len(shows) > 0:
                occurance = (int(len(shows))/4)
                for y in range(0, int(occurance)):
                    n = y*4
                    vals = [shows[n],shows[n+1], shows[n+2],x, shows[n+3]]
                    matchResults.append(vals)
        except:
            pass


    matches = pd.DataFrame(matchResults)
    matches.columns = ['Artist','Date','Venue','Caused_By','Link']
    matches = matches.drop_duplicates()
    matches['Date'] = pd.to_datetime(matches['Date'])
    matches = matches.groupby(['Artist', 'Date','Venue','Link']).agg({'Caused_By': lambda x: ', '.join(x)}).sort_values('Date').reset_index()

    def nameLink(row):
        if row.Link == 'No Link at this time, sorry!':
            return row.Artist
        else:
            return '<a href="{0}">{1}</a>'.format(row.Link, row.Artist)

    matches['NameLink'] = matches.apply(nameLink, axis=1)
    matches = matches[['NameLink','Date','Venue','Caused_By']]

    art = []
    for row in matches['Caused_By']:
        try:
            for artist in row.split(','):
                art.append(artist.strip())
        except:
            pass

    artMatches = list(set(art))
    countFrame = userLikes[1]
    countFrame = countFrame[countFrame['Artist'].isin(artMatches)]
    countFrame = countFrame.sort_values('like_count', ascending=False).drop_duplicates('Artist').sort_values('size', ascending=False)
    countFrame['song_url'] = countFrame['song_url'].apply(lambda x: '<a href="{0}">song_link</a>'.format(x))
    countFrame['like_count'] = countFrame['like_count'].map('{:,.0f}'.format)
    countFrame = countFrame.reset_index()
    countFrame = countFrame.reset_index()
    countFrame['index'] = countFrame['index'].map(lambda x : int(x)+1)
    countFrame['level_0'] = countFrame['level_0'].map(lambda x : int(x)+1)



    matches.columns = ['Event','Date','Venue','Liked Artists']
    matches.Date = matches.Date.map(lambda x: x.strftime('%m/%d/%Y') if pd.notnull(x) else '')
    matches = matches.reset_index()
    matches['index'] = matches['index'].map(lambda x : int(x)+1)

    matches.style.set_properties(subset=['Date'], **{'width': '100px'})

    return [matches, countFrame]
