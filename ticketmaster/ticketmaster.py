import requests
from tqdm import tqdm
import json
import grequests
import os
import sys


def get_events(api_key, query=None):
    base_url = 'https://app.ticketmaster.com/discovery/v2/events.json?apikey={}&size=500&page={}'.format(api_key, '{}')
    if query:
        base_url += '&keyword=' + query
    print('Collecting events from TicketMaster...')
    page = requests.get(base_url.format(1)).json()
    rs = (grequests.get(base_url.format(i+1)) for i in tqdm(range(1, page['page']['totalPages'])))
    mapped = list(map(lambda x: x.json(), grequests.map(rs)))
    result = list(map(lambda x: x['_embedded']['events'] if '_embedded' in x else [], mapped))
    events = [item for sublist in result for item in sublist]
    events = list({x['id']: x for x in events}.values())
    return events

def generate_open_event(i, event):
    result = {
        'id': i,
        'name': "",
        "latitude": "",
        "longitude": "",
        "location_name": "",
        "start_time": "",
        "end_time": "",
        "timezone": "",
        "description": "",
        "background_image": "",
        "logo": "",
        "organizer_name": "",
        "organizer_description": "",
        "social_links": [],
        "ticket_url": "",
        "privacy": "public",
        "type": "",
        "topic": "",
        "sub_topic": None,
        "code_of_conduct": "",
        "copyright": {
            "holder": None,
            "holder_url": None,
            "licence": None,
            "licence_url": None,
            "logo": None,
            "year": None
        },
        "call_for_papers": None,
        "creator": {
            "email": ""
        },
        "email": None,
        "has_session_speakers": False,
        "schedule_published_on": None,
        "searchable_location_name": None,
        "state": "Completed",
        "version": {
            "event_ver": 0,
            "microlocations_ver": 0,
            "sessions_ver": 0,
            "speakers_ver": 0,
            "sponsors_ver": 0,
            "tracks_ver": 0
        }
    }
    if 'name' in event:
        result['name'] = event['name']
    if '_embedded' in event and 'venues' in event['_embedded'] and event['_embedded']['venues']:
        venue = event['_embedded']['venues'][0]
        if 'location' in venue:
            result.update(venue['location'])
        address = []
        if 'address' in venue and 'line1' in venue['address']:
            address.append(venue['address']['line1'])
        if 'city' in venue and 'name' in venue['city']:
            address.append(venue['city']['name'])
        if 'country' in venue and 'name' in venue['country']:
            address.append(venue['country']['name'])
        result['location_name'] = ','.join(address)
    if 'dates' in event:
        dates = event['dates']
        if 'start' in dates and 'dateTime' in dates['start']:
            result['start_time'] = dates['start']['dateTime'][:-1]
        if 'end' in dates and 'dateTime' in dates['end']:
            result['end_time'] = dates['end']['dateTime'][:-1]
        if 'timezone' in dates:
            result['timezone'] = dates['timezone']
    if 'info' in event:
        result['description'] = event['info']
    if 'images' in event and event['images']:
        image = max(events[0]['images'], key=lambda x: x['width'])['url']
        result['background_image'] = image
        result['logo'] = image
    if 'classifications' in event:
        classifications = event['classifications'][0]
        if 'genre' in classifications:
            if classifications['genre']['name'] != 'Undefined':
                result['type'] = classifications['genre']['name']
                if classifications['subGenre']['name'] != 'Undefined':
                    result['type'] += ' ({})'.format(classifications['subGenre']['name'])
        if 'segment' in classifications:
            if classifications['segment']['name'] != 'Undefined':
                result['topic'] = classifications['segment']['name']
    if 'url' in event:
        result['ticket_url'] = event['url']
    return result

if __name__ == '__main__':
    if len(sys.argv) == 1:
        exit('Please specify API_KEY')
    API_KEY = sys.argv[1]
    query = None
    if len(sys.argv) > 2:
        query = sys.argv[2]
    events = get_events(API_KEY, query)
    print('Converting to Open Event format...')
    directory = 'tickets/'
    if not os.path.exists(directory):
        os.makedirs(directory)
    for i, event in tqdm(enumerate(events), total=len(events)):
        generated = generate_open_event(i, event)
        json.dump(generated, open(directory + '{}.json'.format(i), 'w'))
