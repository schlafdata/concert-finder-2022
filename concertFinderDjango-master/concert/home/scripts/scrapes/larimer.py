import requests
import pandas as pd
import re
from bs4 import BeautifulSoup


def larimer_scrape():
    cookies = {
        '_ga': 'GA1.2.604996994.1663967311',
        '_gid': 'GA1.2.28816408.1663967311',
    }

    headers = {
        'authority': 'larimerlounge.com',
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'accept-language': 'en-US,en;q=0.9',
        # Requests sorts cookies= alphabetically
        # 'cookie': '_ga=GA1.2.604996994.1663967311; _gid=GA1.2.28816408.1663967311',
        'referer': 'https://larimerlounge.com/events/?view=month',
        'sec-ch-ua': '"Google Chrome";v="105", "Not)A;Brand";v="8", "Chromium";v="105"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"macOS"',
        'sec-fetch-dest': 'document',
        'sec-fetch-mode': 'navigate',
        'sec-fetch-site': 'same-origin',
        'sec-fetch-user': '?1',
        'upgrade-insecure-requests': '1',
        'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.0.0 Safari/537.36',
    }

    params = {
        'view': 'list',
    }

    response = requests.get('https://larimerlounge.com/events/', params=params, cookies=cookies, headers=headers)
    larimer_soup = BeautifulSoup(response.text, 'html.parser')


    mydivs = larimer_soup.find_all("div", {"class": "col-12 eventWrapper rhpSingleEvent py-4 px-0"})

    eventLinks = []
    for div in mydivs:
        eventLink = div.find("a", {"class": "url"})
        eventLinks.append(eventLink['href'])

    eventDates = larimer_soup.find_all("div", {"id": "eventDate"})
    eventDates = [x.text.strip('\n') for x in eventDates]

    eventTitle =larimer_soup.find_all("a", {"id": "eventTitle"}) 
    eventTitles = [x.text.strip('\n').strip() for x in eventTitle]
    
    img_url = [x['src'] for x in larimer_soup.findAll('img', {"class":"eventListImage wp-post-image"})]


    df = pd.DataFrame(list(zip(eventDates, eventTitles, eventLinks, img_url)))
    df.columns = ['Date','Artist','Link','img_url']

    df['Venue'] = 'Larimer Lounge'

    def splitArtists(row):
        return [x.strip() for x in re.split('\\+|\(ft.|\(|\)|w/', row) if (x is not None) & (x != '')]

    df['FiltArtist'] = df['Artist'].map(splitArtists)
    
    df = df[['Artist','Date','Link','Venue','FiltArtist','img_url']]

    return df