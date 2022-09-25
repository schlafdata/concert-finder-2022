import time
from seleniumwire import webdriver
from selenium.webdriver.common.by import By
import requests
import pandas as pd
import re

def black_box_scrape():    
    options = webdriver.ChromeOptions()
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    # options.add_argument("--auto-open-devtools-for-tabs")
    options.add_argument(
        "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36")
    driver = webdriver.Chrome(options=options)
    driver.get('https://blackboxdenver.co/events/')

    time.sleep(3)

    elems = [elem for elem in driver.find_elements(By.CSS_SELECTOR, "a") if 'event-link mb-2 is-blackbox' in elem.get_attribute('class')]
    elems[0].click()

    time.sleep(3)

    lnks=driver.find_elements(By.TAG_NAME, "a")

    def try_href(x):
        try:
            if 'https://blackboxdenver.co/events/' in x[0]:
                return x[1]
        except:
            return

    elem = [(x[0],x[1]) for x in [(try_href(x),x[0]) for x in [(x.get_attribute('href'),x) for x in lnks]] if x[0] is not None]
    elem[1][0].click()

    time.sleep(5)

    # Access requests via the `requests` attribute
    for request in driver.requests:

        if 'https://blackboxdenver.co/api/events?access_token' in request.url:
            resp = requests.get(request.url)

    def try_event(x):
        try:
            return x['Event']
        except:
            pass
    
    df = pd.DataFrame([x['Event'] for x in resp.json()])
    df1 = pd.DataFrame([x['Logo'] for x in resp.json()])
    df['img_url'] = df1['url']
    
    df = df[['start','name','location','tickets_url','img_url']]

    def try_split(x):
        try:
            return x.strip()
        except:
            return

    def splitArtists(row):
        return [try_split(x) for x in re.split('All Night|presents|:|w/|-|&|\(|\)|\+|\*|\/', row) if x not in ['',' ']]
    df['FiltArtist'] = df['name'].map(splitArtists)

    df.columns = ['Date','Artist','Venue','Link','img_url','FiltArtist']

    df = df[['Artist','Date','Link','Venue','FiltArtist','img_url']]
    
    return df