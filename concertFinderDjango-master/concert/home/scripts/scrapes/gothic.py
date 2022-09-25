import requests
import pandas as pd


def gothic_scrape():

    headers = {
        'Accept': 'application/json, text/javascript, */*; q=0.01',
        'Accept-Language': 'en-US,en;q=0.9',
        'Connection': 'keep-alive',
        'If-Modified-Since': 'Fri, 23 Sep 2022 17:50:13 GMT',
        'If-None-Match': '0x8DA9D8C110E48E9',
        'Origin': 'https://www.gothictheatre.com',
        'Referer': 'https://www.gothictheatre.com/',
        'Sec-Fetch-Dest': 'empty',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Site': 'cross-site',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.0.0 Safari/537.36',
        'sec-ch-ua': '"Google Chrome";v="105", "Not)A;Brand";v="8", "Chromium";v="105"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"macOS"',
    }
    
    response = requests.get(f'https://aegwebprod.blob.core.windows.net/json/events/37/events.json', headers=headers).json()
    data = response
    df = pd.DataFrame(data['events'])
    df[['presentedBy', 'presentedByText', 'headliners', 'headlinersText',
           'supporting', 'supportingText', 'tour', 'eventTitle', 'eventTitleText']] = pd.json_normalize(df.title).apply(pd.Series)

    df['img_url'] = pd.json_normalize(df.media)['17.file_name']
    
    df = df[['eventDateTime','headlinersText','supportingText','eventTitleText','eventRedirect','img_url']]
    df['link'] = pd.json_normalize(df.eventRedirect)['url']

    def artitsts(x):  
        return [x.headlinersText.split('-')[0], x.supportingText]

    df['venue'] = 'Gothic Theatre'
    df['filtArtists'] = df.apply(artitsts, axis=1)
    df = df[['headlinersText', 'eventDateTime','link','venue','filtArtists','img_url']]
    df.columns = ['Artist','Date','Link','Venue','FiltArtist','img_url']
    
    return df