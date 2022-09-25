import requests
import pandas as pd
import re
from bs4 import BeautifulSoup

proxies = {}

def blue_bird_scrape():

    blue_bird = requests.get('https://www.bluebirdtheater.net/events', proxies = proxies, verify=False)
    bird_soup = BeautifulSoup(blue_bird.text, 'html.parser')
    blue_bird_events = list(zip(list(filter
                                     (None, 
                                      [z.strip() for z in [y[0] for y in [x.contents for x in bird_soup.findAll('a', {'title':"More Info"})]]])),
                                      [x.contents[2].strip() for x in bird_soup.findAll('span', {'class':"date"})],
                                      [x['href'] for x in bird_soup.findAll('a',{'class':'btn-tickets accentBackground widgetBorderColor secondaryColor tickets status_1'})],
                                      [x['src'] for x in bird_soup.findAll('img') if 'https://images.discovery-prod.axs.com' in x['src']]))
    blue_bird_events = pd.DataFrame(blue_bird_events)
    blue_bird_events['Venue'] = 'Blue Bird'
    blue_bird_events.columns = ['Artist','Date','Link','img_url','Venue']

    def splitArtists(row):
        return [x.strip() for x in re.split('/', row) if (x is not None) & (x != '')]

    blue_bird_events['FiltArtist'] = blue_bird_events['Artist'].map(splitArtists)
    blue_bird_events = blue_bird_events[['Artist','Date','Link','Venue','FiltArtist','img_url']]
    

    return blue_bird_events