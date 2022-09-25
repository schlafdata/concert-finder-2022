
import requests
import pandas as pd

def meow_scrape():
    cookies = {
        'ajs_anonymous_id': '3192e4ec-2cbe-465e-b680-e2e524713e0a',
        '_gcl_au': '1.1.1487863936.1664075966',
        '_fbp': 'fb.1.1664075965650.1283557068',
        '_gid': 'GA1.2.1742054515.1664075966',
        '_scid': '3613940c-7a88-46ed-818b-052948e5e45c',
        '_tt_enable_cookie': '1',
        '_ttp': '578b9715-ea70-4480-9cfa-74db6fe5cf96',
        '__stripe_mid': 'da0ceb1d-0a6c-4771-8354-9e1fdc98b51b3ecd44',
        '__stripe_sid': 'bbe0865d-e6cb-430b-9293-a1346c8d53d6d8043e',
        '__hstc': '183241081.2675588f18c7db5d97d2732e318ab3ba.1664075965821.1664075965821.1664075965821.1',
        'hubspotutk': '2675588f18c7db5d97d2732e318ab3ba',
        '__hssrc': '1',
        '_sctr': '1|1663999200000',
        '_gat_UA-29796014-1': '1',
        '_ga_9505BR5S4S': 'GS1.1.1664075965.1.1.1664076095.0.0.0',
        '_ga': 'GA1.1.671179185.1664075966',
        '_ga_YYTSRDQY6E': 'GS1.1.1664075965.1.1.1664076095.51.0.0',
        '_uetsid': 'db94a2603c8011edb4dd854eca41a367',
        '_uetvid': 'db94e0103c8011edab15479653cf1f7f',
        '__hssc': '183241081.3.1664075965822',
    }

    headers = {
        'authority': 'tickets.meowwolf.com',
        'accept': '*/*',
        'accept-language': 'en-US,en;q=0.9',
        # Already added when you pass json=
        # 'content-type': 'application/json',
        # Requests sorts cookies= alphabetically
        # 'cookie': 'ajs_anonymous_id=3192e4ec-2cbe-465e-b680-e2e524713e0a; _gcl_au=1.1.1487863936.1664075966; _fbp=fb.1.1664075965650.1283557068; _gid=GA1.2.1742054515.1664075966; _scid=3613940c-7a88-46ed-818b-052948e5e45c; _tt_enable_cookie=1; _ttp=578b9715-ea70-4480-9cfa-74db6fe5cf96; __stripe_mid=da0ceb1d-0a6c-4771-8354-9e1fdc98b51b3ecd44; __stripe_sid=bbe0865d-e6cb-430b-9293-a1346c8d53d6d8043e; __hstc=183241081.2675588f18c7db5d97d2732e318ab3ba.1664075965821.1664075965821.1664075965821.1; hubspotutk=2675588f18c7db5d97d2732e318ab3ba; __hssrc=1; _sctr=1|1663999200000; _gat_UA-29796014-1=1; _ga_9505BR5S4S=GS1.1.1664075965.1.1.1664076095.0.0.0; _ga=GA1.1.671179185.1664075966; _ga_YYTSRDQY6E=GS1.1.1664075965.1.1.1664076095.51.0.0; _uetsid=db94a2603c8011edb4dd854eca41a367; _uetvid=db94e0103c8011edab15479653cf1f7f; __hssc=183241081.3.1664075965822',
        'origin': 'https://tickets.meowwolf.com',
        'referer': 'https://tickets.meowwolf.com/events/denver/sacha-robotti/',
        'sec-ch-ua': '"Google Chrome";v="105", "Not)A;Brand";v="8", "Chromium";v="105"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"macOS"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-origin',
        'sid': '580a434a-d7eb-4b65-accf-f902b8a5f16e',
        'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.0.0 Safari/537.36',
    }

    json_data = {
        'operationName': 'GetNonRecurringEvents',
        'variables': {
            'categories': [
                'Music',
            ],
            'embed': [
                'meta',
                'venue_meta',
                'event_session',
                'venue',
                'ticket_group',
                'ticket_type',
                'seller',
            ],
            'sellerId': '017a7f54-e443-a261-3c55-46ef4d921efb',
        },
        'query': 'query GetNonRecurringEvents($eventId: ID, $eventSlug: String, $sellerId: ID!, $categories: [EventCategory!] = [Music, Community, Workshops], $embed: [EventEmbed] = [meta, venue_meta, event_session, venue, ticket_group, ticket_type, seller]) {\n  nonRecurringEvents(\n    eventId: $eventId\n    eventSlug: $eventSlug\n    categories: $categories\n    sellerId: $sellerId\n    embed: $embed\n  ) {\n    __typename\n    ...SellerAndVenue\n    events {\n      __typename\n      id\n      venueId\n      sellerId\n      title\n      slug\n      category\n      description\n      summary\n      subtitle\n      ...MetaDataDetails\n      ...TimeslotsDetails\n      ...TicketCategoriesDetails\n    }\n  }\n}\n\nfragment SellerAndVenue on NonRecurringEvents {\n  __typename\n  seller {\n    __typename\n    id\n    name\n    timezone\n    meta {\n      __typename\n      metakey\n      value\n    }\n  }\n  venues {\n    __typename\n    id\n    title\n    description\n    address\n    meta {\n      __typename\n      metakey\n      value\n    }\n  }\n}\n\nfragment TicketCategoriesDetails on EventWithTimeslotsAndMeta {\n  __typename\n  ticketCategories {\n    __typename\n    id\n    eventId\n    title\n    maxPerOrder\n    capacity\n    salesWindow {\n      __typename\n      startOffset\n      endOffset\n    }\n    tiers {\n      __typename\n      id\n      categoryId\n      title\n      subtitle\n      price\n      displayOrder\n    }\n  }\n}\n\nfragment MetaDataDetails on EventWithTimeslotsAndMeta {\n  __typename\n  meta {\n    __typename\n    value\n    metakey\n  }\n}\n\nfragment TimeslotsDetails on EventWithTimeslotsAndMeta {\n  __typename\n  timeslots {\n    __typename\n    ...TimeslotDetails\n  }\n}\n\nfragment TimeslotDetails on Timeslot {\n  __typename\n  id\n  startTime\n  soldOut\n  endTime\n  capacity {\n    __typename\n    total\n    oversell\n    remaining\n  }\n}',
    }

    response = requests.post('https://tickets.meowwolf.com/api/graphql/', cookies=cookies, headers=headers, json=json_data)
    df = pd.DataFrame(response.json()['data']['nonRecurringEvents']['events'])
    
    df['Date'] = pd.json_normalize(pd.json_normalize(df.timeslots)[0])['startTime']
    df['Link'] = df.slug.map(lambda x : f"https://tickets.meowwolf.com/events/denver/{x}/")
    df['Venue'] = 'Meow Wolf Denver'
    
    def img_url(row):
        for x in row:
            try:
                if x['metakey'] == 'imageProfile':
                    return x['value']
            except:
                pass
        
    df['img_url'] = df.meta.map(img_url)
    df = df[['title','Date','Link','Venue','img_url']]
    df.columns = ['Artist','Date','Link','Venue','img_url']
    df['FiltArtist'] = df.Artist.map(lambda x : [x])
    
    df = df[['Artist','Date','Link','Venue','FiltArtist','img_url']]
    
    return df