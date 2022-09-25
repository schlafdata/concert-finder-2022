import requests
import pandas as pd
import re
from bs4 import BeautifulSoup

proxies = {}

def first_bank_scrape():

    first_bank = requests.get('https://www.1stbankcenter.com/events', proxies = proxies, verify=False)
    bank_soup = BeautifulSoup(first_bank.text, 'html.parser')
    first_bank_events = list(zip(list(filter(None, 
                                                [z.strip() for z in [y[0] for y in [x.contents for x in bank_soup.findAll('a', {'title':"More Info"})]]])),
                                                [x.contents[2].strip() for x in bank_soup.findAll('span', {'class':"date"})],
                                                [x['href'] for x in bank_soup.findAll('a',{'class':'btn-tickets accentBackground widgetBorderColor secondaryColor tickets status_1'})],
                                                [x['src'] for x in bank_soup.findAll('img') if 'https://images.discovery-prod.axs.com' in x['src']]
                                                ))
    first_bank = pd.DataFrame(first_bank_events)
    first_bank['Venue'] = '1st Bank'
    first_bank.columns = ['Artist','Date','Link','img_url','Venue']

    def splitArtists(row):
        return [x.strip() for x in re.split('/| \d+', row) if (x is not None) & (x != '')]

    first_bank['FiltArtist'] = first_bank['Artist'].map(splitArtists)
    first_bank = first_bank[['Artist','Date','Link','Venue','FiltArtist','img_url']]


    return first_bank