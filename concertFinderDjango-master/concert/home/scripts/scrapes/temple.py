import requests
import pandas as pd
import re

def temple_scrape():
    
    import datetime
    
    def temple_date_fmt(date):

        if int(date) <10:
            return '0' + str(date)
        else:
            return date

    from dateutil.relativedelta import relativedelta
    today = datetime.datetime.today()
    month_count = 0

    all_dfs = []
    while month_count < 6:
        try:
            day = today + relativedelta(months=month_count)
            m_d = str(day.year)[2:] + str(temple_date_fmt(day.month)) + '01'
            resp = requests.get(f'https://uvtix.com/api/v3/ve187917rm0fd{m_d}/calevents.json')
            month_count += 1
            shows = []
            for json in resp.json()['weeks']:
                shows1 = json[-1]
                shows.append(shows1)
                shows2 = json[-2]
                shows.append(shows2)

            li = [x['events'] for x in shows]

            dfs = []
            for item in li:
                try:
                    dfs.append(pd.DataFrame(item))
                except:
                    pass

            df2 = pd.concat(dfs)
            all_dfs.append(df2)
        except:
            break


    df = pd.concat(all_dfs)
    df['img_url'] = [x.lstrip('//') for x in pd.json_normalize(pd.json_normalize(df.flyers)[0])['raw_url']]
    df = df[['name','date','ticketsurl','img_url']]

    def splitArtists(row):
        return [x.strip() for x in re.split('Presented by|at|Afterparty|with|&', row) if x not in ['',' ']]
    df['FiltArtist'] = df['name'].map(splitArtists)

    df.columns = ['Artist','Date','Link','img_url','FiltArtist']
    df['Venue'] = 'Temple'
    df = df[['Artist','Date','Link','Venue','FiltArtist','img_url']]
    
    return df
