import requests
import pandas as pd
import re
from bs4 import BeautifulSoup

def mish_scrape():
    
    cookies = {
        '_ga': 'GA1.2.1960140136.1663969719',
        '_gid': 'GA1.2.1496379620.1663969719',
        '_gat_gtag_UA_168961935_1': '1',
        '_gat': '1',
    }

    headers = {
        'authority': 'www.themishawaka.com',
        'accept': '*/*',
        'accept-language': 'en-US,en;q=0.9',
        'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
        # Requests sorts cookies= alphabetically
        # 'cookie': '_ga=GA1.2.1960140136.1663969719; _gid=GA1.2.1496379620.1663969719; _gat_gtag_UA_168961935_1=1; _gat=1',
        'origin': 'https://www.themishawaka.com',
        'referer': 'https://www.themishawaka.com/events/?view=month',
        'sec-ch-ua': '"Google Chrome";v="105", "Not)A;Brand";v="8", "Chromium";v="105"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"macOS"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-origin',
        'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.0.0 Safari/537.36',
        'x-requested-with': 'XMLHttpRequest',
    }

    data = {
        'data[limit]': '500',
        'data[display]': 'false',
        'data[displayName]': '',
        'data[genre]': '',
        'data[venue]': '',
        'data[month]': '',
        'data[justAnnounced]': '',
        'action': 'loadEtixMonthViewEventPageFn',
    }

    response = requests.post('https://www.themishawaka.com/wp-admin/admin-ajax.php', cookies=cookies, headers=headers, data=data)

    df = pd.DataFrame(response.json()['data'])

    def get_title(row):

        row_soup = BeautifulSoup(row, 'html.parser')
        return row_soup.find("div", {"class":"showtitle"}).text

    df['show_title'] = df['title'].map(get_title)

    df = df[['eventdate','show_title','url','imageurl']]

    df.columns = ['Date','Artist','Link','img_url']
    df['Venue'] = 'Mishawakkkaaa'

    def splitArtists(row):
        return [x.strip() for x in re.split('w/|with|,|special guests', row) if x != ' ']
    df['FiltArtist'] = df['Artist'].map(splitArtists)
    
    df = df[['Artist','Date','Link','Venue','FiltArtist','img_url']]
    
    return df