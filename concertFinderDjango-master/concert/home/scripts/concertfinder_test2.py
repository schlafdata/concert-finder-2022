import pandas as pd
import requests
# import numpy as np
from dateutil.parser import parse
import json
import warnings
warnings.filterwarnings("ignore")
import concurrent.futures
from collections import defaultdict
import dateutil.parser

# from soundcloud.soundcloud import *
# from scrapes.blackbox import *
# from scrapes.blue_bird import *
# from scrapes.meow import *
# from scrapes.ogden import *
# from scrapes.first_bank import *
# from scrapes.gothic import *
# from scrapes.belly_up import *
# from scrapes.larimer import * 
# from scrapes.mish import *
# from scrapes.mission import *
# from scrapes.summit import *
# from scrapes.fillmore import *
# from scrapes.marquis import *
# from scrapes.temple import *
# from scrapes.night_out import *
# from scrapes.red_rocks import * 
# from scrapes.cervantes import *

from home.scripts.soundcloud.soundcloud import *
from home.scripts.scrapes.blackbox import *
from home.scripts.scrapes.blue_bird import *
from home.scripts.scrapes.meow import *
from home.scripts.scrapes.ogden import *
from home.scripts.scrapes.first_bank import *
from home.scripts.scrapes.gothic import *
from home.scripts.scrapes.belly_up import *
from home.scripts.scrapes.larimer import * 
from home.scripts.scrapes.mish import *
from home.scripts.scrapes.mission import *
from home.scripts.scrapes.summit import *
from home.scripts.scrapes.fillmore import *
from home.scripts.scrapes.marquis import *
from home.scripts.scrapes.temple import *
from home.scripts.scrapes.night_out import *
from home.scripts.scrapes.red_rocks import * 
from home.scripts.scrapes.cervantes import *


functions = ['meow_scrape()','black_box_scrape()','temple_scrape()','mish_scrape()','larimer_scrape()','marquisScrape()','fillmoreScrape()','cervantes_scrape()','bellyScrape()','redRocksScrape()','nightOutScrape()','missionScrape()','blue_bird_scrape()','ogden_scrape()','first_bank_scrape()','gothic_scrape()','summitScrape()']


result = []
rang = range(0,len(functions))


def sf_query(run):
            try:
                result.append(eval(functions[run]))
            except:
                print('error', functions[run])
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
    # denver_raw_concerts = denver_concerts
    for artists in denver_concerts.values:
        try:
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
                        concertDict[artist.strip().upper()].append(artists[5])
        except:
            pass
    return denver_concerts



def findMatches(user, source):


    denver_concerts = eventDict()
    # denver_raw_concerts = eventDict()[1]
    
    userLikes = mapFilters(user)

    like_urls = userLikes[1].sort_values('like_count', ascending=False).drop_duplicates('Artist').sort_values('size', ascending=False)
    liked_song_url_dict = dict(zip(like_urls['Artist'].tolist(), like_urls['song_url'].tolist()))

    matchResults = []
    for x in userLikes[0]:
        try:
            shows = concertDict[x]
            if len(shows) > 0:
                
                try:
                    song_url = liked_song_url_dict[x]
                except:
                    song_url = 'no url'
                
                occurance = (int(len(shows))/5)
                for y in range(0, int(occurance)):
                    n = y*5
                    vals = [shows[n],shows[n+1], shows[n+2],x, shows[n+3], shows[n+4], song_url]
                    matchResults.append(vals)
        except:
            pass


    pd.set_option('display.max_columns', 30)
    matches = pd.DataFrame(matchResults)

    matches.columns = ['Artist','Date','Venue','Caused_By','Link','img_url','song_url']

    matches = matches.drop_duplicates(['Artist','Date','Link'])

    
    matches['Date'] = matches['Date'].map(lambda x : dateutil.parser.parse(str(x)))
    matches.Date = matches.Date.map(lambda x : str(x).split("+")[0])
    
    matches['Date'] = pd.to_datetime(matches['Date'])
    matches = matches.groupby(['Artist', 'Date','Venue','Link','img_url']).agg({'Caused_By': lambda x: ', '.join(x),'song_url': lambda x : list(x)}).sort_values('Date').reset_index()

    if source == 'host':
    
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
        matches.Date = matches['Date'].map(lambda x : dateutil.parser.parse(str(x)))
        matches = matches.reset_index()
        matches['index'] = matches['index'].map(lambda x : int(x)+1)
        # matches.loc[matches['Date'] > pd.Timestamp(datetime.now()), 'Date']

        matches.style.set_properties(subset=['Date'], **{'width': '100px'})

        return [matches, countFrame]
    
    elif source == 'api':
            matches = matches[['Artist','Date','Venue','Link','img_url','Caused_By','song_url']]
            matches.columns = ['Event','Date','Venue','ticketLink','img_url','LikedArtists','song_url']
            matches.Date = matches['Date'].map(lambda x : dateutil.parser.parse(str(x)))
            matches.Date = pd.to_datetime(matches.Date)
            matches.columns = ['Event','Date','Venue','Link','img_url','LikedArtists','song_url']
            jsonMatches = matches.to_dict('records')
            return [jsonMatches]
