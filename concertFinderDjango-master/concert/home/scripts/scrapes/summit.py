import requests
import pandas as pd

def summitScrape():
        cookies = {
            'mt.v': '2.1008697111.1663964971406',
            'mt.pc': '2.1',
            '_gcl_au': '1.1.648872158.1663964971',
            'mt.g.2f013145': '2.1008697111.1663964971406',
            'QueueITAccepted-SDFrts345E-V3_livenation': 'EventId%3Dlivenation%26QueueId%3D00000000-0000-0000-0000-000000000000%26RedirectType%3Ddisabled%26IssueTime%3D1663964971%26Hash%3D92f145d6eb9bb8936d6fe4faff9c10ab44030480ccc03400ff9a92ed863bb2c9',
            '_ga': 'GA1.2.1685932708.1663964972',
            '_gid': 'GA1.2.1178063605.1663964972',
            'seerses': 'e',
            '_fbp': 'fb.1.1663964971923.327460204',
            'seerid': '501ba304-019b-4a9b-9d2a-4c9a6dcef0a0',
            '_scid': 'f95187c5-3865-4095-b16d-6be31db64700',
            'TM_PIXEL': '{"_dvs":"0:l8exs5o6:ZfYW8FLrjjefI1XVBYuKuC_EGft7Kek~","_dvp":"0:l8exs5o6:Kp~ctdS0kVJrMjeOE6FKeIvkPEUj~PeL"}',
            '_dvs': '0:l8exs5o6:ZfYW8FLrjjefI1XVBYuKuC_EGft7Kek~',
            '_dvp': '0:l8exs5o6:Kp~ctdS0kVJrMjeOE6FKeIvkPEUj~PeL',
            '__gads': 'ID=ed7ca468e23f162c:T=1663964971:S=ALNI_MZHBrhTyNp3_6hre2WJ1wn9zT57-g',
            '__gpi': 'UID=000008c7c3c7fe86:T=1663964971:RT=1663964971:S=ALNI_MYluCJUkNSfNs_YcdfbKuBTn5THuw',
            '_tt_enable_cookie': '1',
            '_ttp': '64209cc8-8e39-463c-98b3-15ac31d0e559',
            'qcSxc': '1663964976280',
            '__qca': 'P0-920545329-1663964976277',
            '_sctr': '1|1663912800000',
            '_dd_s': 'logs=0&expire=1663966330634',
        }

        headers = {
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'en-US,en;q=0.9',
            'Connection': 'keep-alive',
            # Requests sorts cookies= alphabetically
            # 'Cookie': 'mt.v=2.1008697111.1663964971406; mt.pc=2.1; _gcl_au=1.1.648872158.1663964971; mt.g.2f013145=2.1008697111.1663964971406; QueueITAccepted-SDFrts345E-V3_livenation=EventId%3Dlivenation%26QueueId%3D00000000-0000-0000-0000-000000000000%26RedirectType%3Ddisabled%26IssueTime%3D1663964971%26Hash%3D92f145d6eb9bb8936d6fe4faff9c10ab44030480ccc03400ff9a92ed863bb2c9; _ga=GA1.2.1685932708.1663964972; _gid=GA1.2.1178063605.1663964972; seerses=e; _fbp=fb.1.1663964971923.327460204; seerid=501ba304-019b-4a9b-9d2a-4c9a6dcef0a0; _scid=f95187c5-3865-4095-b16d-6be31db64700; TM_PIXEL={"_dvs":"0:l8exs5o6:ZfYW8FLrjjefI1XVBYuKuC_EGft7Kek~","_dvp":"0:l8exs5o6:Kp~ctdS0kVJrMjeOE6FKeIvkPEUj~PeL"}; _dvs=0:l8exs5o6:ZfYW8FLrjjefI1XVBYuKuC_EGft7Kek~; _dvp=0:l8exs5o6:Kp~ctdS0kVJrMjeOE6FKeIvkPEUj~PeL; __gads=ID=ed7ca468e23f162c:T=1663964971:S=ALNI_MZHBrhTyNp3_6hre2WJ1wn9zT57-g; __gpi=UID=000008c7c3c7fe86:T=1663964971:RT=1663964971:S=ALNI_MYluCJUkNSfNs_YcdfbKuBTn5THuw; _tt_enable_cookie=1; _ttp=64209cc8-8e39-463c-98b3-15ac31d0e559; qcSxc=1663964976280; __qca=P0-920545329-1663964976277; _sctr=1|1663912800000; _dd_s=logs=0&expire=1663966330634',
            'Referer': 'https://www.livenation.com/venue/KovZpZAFFt1A/summit-events',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-origin',
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.0.0 Safari/537.36',
            'sec-ch-ua': '"Google Chrome";v="105", "Not)A;Brand";v="8", "Chromium";v="105"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"macOS"',
        }


        dfs = []
        x=1

        while True:
            try:
                params = {
                        'discovery_id': 'KovZpZAFFt1A',
                        'slug': 'summit',
                        'pg': f'{x}',
                        }

                response = requests.get('https://www.livenation.com/_next/data/PAh682KIcCv6rz8ymDFCV/venue/KovZpZAFFt1A/summit-events.json', params=params, cookies=cookies, headers=headers)
                df = pd.DataFrame(response.json()['pageProps']['queryResults']['page']['data']['getEvents'])
                df['venueName'] = pd.json_normalize(df['venue'])['name']
                df['artist_name'] = pd.json_normalize(pd.json_normalize(df['artists'])[0])['name']
                df['img_url'] = pd.json_normalize(pd.json_normalize(df.images)[0])['image_url']
                df = df[['name','artist_name','venueName','url','event_date_timestamp_utc','img_url']]

                dfs.append(df)
                x+=1
            except:
                break


        df = pd.concat(dfs)
        df = df.drop_duplicates()
        df['filtArtists'] = df['artist_name'].map(lambda x : [x])
        df = df[['artist_name','event_date_timestamp_utc','url','venueName','filtArtists','img_url']]
        df.columns = ['Artist','Date','Link','Venue','FiltArtist','img_url']
        
        return df