import requests
import pandas as pd
import re

proxies = {}

def missionScrape():

    mission = requests.get('https://missionballroom.com/data/events-index.json', proxies = proxies, verify = False)
    mission = mission.json()

    missionData = []
    for x in mission:
        
        date = x['date']
        artist1 = x['title']
        artist2 = x['subtitle']
        img_url = x['img318x187']
        
        if artist2 == '':
            artist = artist1
        else:
            artist = artist1 + ',' + artist2

        venue = 'Mission Ballroom'
        ticketLink = x['tickets']
        info = (artist, date, ticketLink, venue, img_url)
        missionData.append(info)

    missionFrame = pd.DataFrame(missionData)
    missionFrame.columns = ['Artist','Date','Link','Venue','img_url']

    def splitArtists(row):
        return [x.strip() for x in re.split('&|WITH|,|/|with| x| X', row) if x not in ['',' ']]
    missionFrame['FiltArtist'] = missionFrame['Artist'].map(splitArtists)
    
    missionFrame = missionFrame[['Artist','Date','Link','Venue','FiltArtist','img_url']]

    return missionFrame