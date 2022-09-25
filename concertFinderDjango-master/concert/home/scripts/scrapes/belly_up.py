import requests
import pandas as pd
import re
from bs4 import BeautifulSoup


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

    data = [(event.find('h3',{'class':'event-name'}).text.strip(),
             event.find('span',{'class':'date'}).text.strip(), 
             event.find('a', href=True)['href']) for event in bellySoup.findAll('div', {'class':'event-details'})
           ]
    
    data2 = [(x['src'],) for x in bellySoup.findAll('img', {"class":"attachment-full size-full"})]
    
    data = [x+y for x,y in list(zip(data,data2))]
    

    df = pd.DataFrame(data)
    df.columns = ['Artist','Date','Link','img_url']
    df['Venue'] = 'BellyUp Aspen'
    bellyFrame = df
    bellyFrame['FiltArtist'] = bellyFrame['Artist']

    def bellyList(row):
        return [row.strip()]

    bellyFrame['FiltArtist'] =  bellyFrame['FiltArtist'].map(bellyList)
    bellyFrame = bellyFrame[['Artist','Date','Link','Venue','FiltArtist','img_url']]

    return bellyFrame