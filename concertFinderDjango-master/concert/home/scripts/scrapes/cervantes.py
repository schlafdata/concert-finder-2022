import requests
import pandas as pd
import nltk
import pycrfsuite
from datetime import datetime

tagger = pycrfsuite.Tagger()
# tagger.open('/Users/john.schlafly/Documents/concert-finder-v2/concert-finder-2022/concertFinderDjango-master/concert/home/scripts/crf.model')
tagger.open('/home/ubuntu/concert-finder-2022/concertFinderDjango-master/concert/home/scripts/crf.model')


def cervantes_scrape():

    cookies = {
    '_fbp': 'fb.1.1625971576023.279520537',
    'deviceDetect_com.intellimark.util.DeviceDetector': 'false:::true:::1',
    'JSESSIONID': '5FC68327F8E62DFCF586DEDCBD5168A9',
    'BIGipServerwww.etix.com-HTTPS': '973738156.47873.0000',
    '_gid': 'GA1.2.1370894608.1626375973',
    '_ga_G4K0DX8L5Y': 'GS1.1.1626375970.7.1.1626376016.0',
    '_ga': 'GA1.2.893052237.1625971420',
    }

    headers = {
        'Connection': 'keep-alive',
        'sec-ch-ua': '" Not;A Brand";v="99", "Google Chrome";v="91", "Chromium";v="91"',
        'Accept': 'application/json, text/javascript, */*; q=0.01',
        'X-Requested-With': 'XMLHttpRequest',
        'sec-ch-ua-mobile': '?0',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36',
        'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
        'Origin': 'https://www.etix.com',
        'Sec-Fetch-Site': 'same-origin',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Dest': 'empty',
        'Referer': 'https://www.etix.com/ticket/online3/calendar.jsp?organization_id=6122',
        'Accept-Language': 'en-US,en;q=0.9',
    }

    data = {
      'queryString': 'language=en&country=US&organization_id=6122'
    }

    responses = []

    for x in range(1, 12):

        response = requests.post(f'https://www.etix.com/ticket/json/calendar/organization/6122/2022/{x}', headers=headers, cookies=cookies, data=data)
        responses.append(response.json())


    cervShows = []

    for x in responses:

        month = x['month']
        year = x['year']

        for event in x['dates']:

            showDate = str(month) + '/' + str(event['date']) +'/' + str(year)

            names = [x['name'] for x in event['activities']]
            links = [x['buyUrl'] for x in event['activities']]

            shows = [(i,j, showDate) for i, j in zip(names, links)]
            for show in shows:

                cervShows.append(show)

    cervFrame = pd.DataFrame(cervShows)

    cervFrame.columns = ['Artist','Link','Date']

    cervFrame['Venue'] = 'Cervantes'

    cervFrame['Date'] = pd.to_datetime(cervFrame['Date'])

    cervFrame = cervFrame[cervFrame['Date'] >= datetime.today().strftime('%Y-%m-%d')]

    cervParse = cervFrame

    def shift(row):

        if 'SHIFT Ft.' in row:
            return row.split('SHIFT Ft.')[1]
        else:
            return row

    cervParse['EventTitle'] = cervParse['Artist'].map(lambda x : ' , '.join(x.split(',')))
    cervParse['EventTitle'] = cervParse['Artist'].map(lambda x : ' ( '.join(x.split('(')))
    cervParse['EventTitle'] = cervParse['Artist'].map(lambda x : ' ) '.join(x.split(')')))
    cervParse['EventTitle'] = cervParse['Artist'].map(shift)



    def POStag(row):
        data = []
        tokens = [event for event in row.split()]
        # for every token in the event title, tag with a Part Of Speach label from the NLTK library
        tagged = nltk.pos_tag(tokens)

        return tagged


    cervParse['POS'] = cervParse.EventTitle.map(POStag)


    #     cervParse['POS'] = cervParse['labeled'].map(POStags)
    #     cervParse['POS'] = cervParse['POS'].map(lambda x : x[0])

    #     data = cervParse['POS'].tolist()

    def word2features(doc, i):

        # create features for training based on charchteristics of the word, and its surrounding words/ charachters

        word = doc[i][0]
        postag = doc[i][1]
        features = [
            'word.lower=' + word.lower(),
            'bias',
            'postag=' + postag,
            'word.isupper=%s' % word.isupper(),
            'word.istitle=%s' % word.istitle()
        ]

        if i > 0:
            word1 = doc[i-1][0]
            postag1 = doc[i-1][1]
            features.extend([
                '-1:word.lower=' + word1.lower(),
                '-1:postag=' + postag1,
                '-1:postag[:2]=' + postag1[:2],
                '-1:word.istitle=%s' % word1.istitle(),
                '-1:word.isupper=%s' % word1.isupper()

            ])

        else:
            features.append('BOS')

        if i < len(doc)-1:
            word1 = doc[i+1][0]
            postag1 = doc[i+1][1]
            features.extend([
                '+1:word.lower=' + word1.lower(),
                '+1:postag=' + postag1,
                '+1:postag[:2]=' + postag1[:2],
                '+1:word.istitle=%s' % word1.istitle(),
                '+1:word.isupper=%s' % word1.isupper()
            ])
        else:
            features.append('EOS')

        return features

    # A function for extracting features in documents
    def extract_features(doc):
        return [word2features(doc, i) for i in range(len(doc))]

    # A function fo generating the list of labels for each document
    def get_labels(doc):
        return [label for (token, postag, label) in doc]

    cervParse['features'] = cervParse['POS'].map(lambda x : extract_features(x))
    # extract features for every event title

    cervParse['preds'] = cervParse.features.map(lambda x : [tagger.tag(x)])
    # map trained model the features of each event title
    cervParse['toks'] = cervParse.POS.map(lambda x: [x[0] for x in x])
    # get prediction tags and word tokens into lists so they can be combined

    def zipper(row):
        return [(x,y) for x,y in list(zip(row.toks, row.preds[0])) if y in ['A','S']]

    cervParse['artistPreds'] = cervParse.apply(zipper, axis=1)

    def combine(row):
        results = [(x,y) for x,y in list(zip(row.toks, row.preds[0])) if y in ['A','S']]
        artist = []
        for x in results:
            if x[1] == 'A':
                artist.append(x[0])
            else:
                artist.append(',')
        return ', '.join([y for y in [x.strip() for x in ' '.join(artist).split(',')] if y != ''])

    cervParse['predictions'] = cervParse.apply(combine, axis=1)
    cervParse['predictions'] = cervParse['predictions'].map(lambda x : [x for x in x.split(',')])
    cervArtistFrame = cervParse[['Artist','predictions','Date','Venue','Link']]
    cervArtistFrame.columns = ['Artist','FiltArtist','Date','Venue','Link']
    cervArtistFrame = cervArtistFrame[cervArtistFrame['Venue'] != 'RED ROCKS AMPHITHEATRE']

    cervArtistFrame = cervArtistFrame[['Artist','Date','Link','Venue','FiltArtist']]
    cervArtistFrame['img_url'] = 'sorry no image for this event yet'

    cervArtistFrame= cervArtistFrame[['Artist','Date','Link','Venue','FiltArtist','img_url']]

    return cervArtistFrame
