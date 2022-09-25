
import requests
import pandas as pd
import re



def redRocksScrape():

    red_rocks = requests.get('https://www.redrocksonline.com/wp-json/clique/v1/get_calendar_events_range?start=2022-09-01T00%3A00%3A00&end=2023-08-01T00%3A00%3A00&timeZone=America%2FDenver')

    redRocksJson = red_rocks.json()

    redFrame = pd.DataFrame([(x['title'],x['start'].split('T')[0],x['url']) for x in redRocksJson])

    redFrame.columns = ['Artist','Date','Link']

    redFrame['Venue'] = 'Red Rocks'

    def splitArtists(row):
        return [x.strip() for x in re.split(';|:|,|,with|/|special guest|with|-| \d+|presents', row) if x != '']

    redFrame['FiltArtist'] = redFrame['Artist'].map(splitArtists)

    redFrame['img_url'] = 'sorry, no image for this event.'

    redFrame = redFrame[['Artist','Date','Link','Venue','FiltArtist','img_url']]

    return redFrame