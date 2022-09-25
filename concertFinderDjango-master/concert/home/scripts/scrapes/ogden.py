import requests
import pandas as pd
import re
from bs4 import BeautifulSoup

proxies = {}

def ogden_scrape():

    ogden = requests.get('https://www.ogdentheatre.com/events', proxies = proxies, verify=False)
    ogden_soup = BeautifulSoup(ogden.text, 'html.parser')
    ogden_events = list(zip(list(filter(None, 
                                        [z.strip() for z in [y[0] for y in [x.contents for x in ogden_soup.findAll('a', {'title':"More Info"})]]])),
                                        [x.contents[2].strip() for x in ogden_soup.findAll('span', {'class':"date"})],
                                        [x['href'] for x in ogden_soup.findAll('a',{'class':'btn-tickets accentBackground widgetBorderColor secondaryColor tickets status_1'})],
                                        [x['src'] for x in ogden_soup.findAll('img') if 'https://images.discovery-prod.axs.com' in x['src']]))
    ogden_events = pd.DataFrame(ogden_events)
    ogden_events['Venue'] = 'Ogden'
    ogden_events.columns = ['Artist','Date','Link','img_url','Venue']


    def splitArtists(row):
        return [x.strip() for x in re.split('Presents|:', row) if (x is not None) & (x != '')]

    ogden_events['FiltArtist'] = ogden_events['Artist'].map(splitArtists)
    ogden_events = ogden_events[['Artist','Date','Link','Venue','FiltArtist','img_url']]

    return ogden_events