import requests
import pandas as pd
import re
from bs4 import BeautifulSoup
from seleniumwire import webdriver

def nightOutScrape():
    
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')

        # Create a new instance of the chrome web driver
        driver = webdriver.Chrome(options=chrome_options)
        driver.get("https://coclubs.com/events")


        # Access requests via the `requests` attribute
        for request in driver.requests:
            if "https://api.ticketsauce.com/v2/oauth/token" in request.url:
            # here you need to filter the name of the url request you want
            # if "name_of_the_url_in_header" in request.url
                token = requests.get(request.url).json()['access_token']
                
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
            ('access_token', f'{token}'),
            ('active_only', 'true'),
            ('privacy_type', 'public'),
            ('start_after', ''),
        )

        response = requests.get('https://api.ticketsauce.com/v2/events', headers=headers, params=params)

        concerts = pd.DataFrame([x['Event'] for x in response.json()])
        concerts2 = pd.DataFrame([x['Logo'] for x in response.json()])
        concerts['img_url'] = concerts2['url']
        
        concerts = concerts[['location', 'name','event_url', 'start_utc','img_url']]
        concerts.columns = ['Venue','Artist','Link','Date','img_url']


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
        
        concerts = concerts[['Artist','Date','Link','Venue','FiltArtist','img_url']]

        return concerts