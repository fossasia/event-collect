import sys
import requests
import os
import json
import json_converter
import unicodedata
from bs4 import BeautifulSoup

files = ['event.json', 'organizers.json', 'microlocations.json', 'forms.json',
         'session_types.json', 'sessions.json', 'sponsors.json', 'speakers.json', 'tracks.json']

# Prints the collected data into the corresponding files
def writeToJson (path, data):
    for index in range (9):
        json_data = json.dumps(data[index], indent=4)
        output_file = open('{}/{}'.format(path, files[index]), 'w')
        output_file.write(json_data)
        output_file.close()

# Returns a BeautifulSoup object containing the search results
def getSoup (scrape_url):
    raw_html = requests.get(scrape_url)
    try:
        raw_html.raise_for_status()
    except Exception as exc:
        print ('{} {}'.format('Houston, we have a problem:', exc))
        sys.exit()
    normalized_data = unicodedata.normalize('NFKD', raw_html.text).replace('\n', '')
    normalized_data = normalized_data.replace('\u201c', '"').replace('\u201d', '"').replace('\u2019', "'")
    normalized_data = normalized_data.replace('\u2013', '').replace('\u2014', ' ')
    return BeautifulSoup(normalized_data, 'lxml')

# Picks the links to each event's description and stores them into an array
def getEventsArray (soup):
    links = soup.select('.event h3 a')
    if len (links) < 1:
        print ('Sorry, no events matching your query!')
        sys.exit()
    print ('Yay! We found events!')
    events = []
    for event in links:
        events.append(event['href'])
    return events

def getEventsData (query, events):
    for url in events:
        ''' Uses the URL of the event page to get the event title, which will later
        name the folder containing the data
        '''
        start_index = url.index('.com') + 5
        event_title = url[start_index:]
        # Creates folder for each search result
        path = '{}/{}'.format(query, event_title)
        if not os.path.exists(path):
           os.mkdir(path)
        print('{} {}'.format('Writing event data to', path))
        data = createJson(url, path)
        writeToJson(path, data)

def createJson (url, path):
    collectedData = [{'creator': {'id': '1', 'email': ''}, 'privacy': 'public'}]
    # The event details are distributed across more pages, so the data is extracted from all of them
    # Collects data from the main page
    soup = getSoup(url)
    json_converter.addHome(collectedData, soup, url)
    json_converter.addOrganizer(collectedData, soup, url)
    json_converter.addImage(collectedData, soup, path)
    # Collects data from the details page (event description, social links)
    soup = getSoup('{}{}'.format(url, 'details'))
    json_converter.addAbout(collectedData, soup)
    # Collects location data
    soup = getSoup('{}{}'.format(url, 'get-there'))
    json_converter.addLocation(collectedData, soup)
    # Adds the empty fields to match the Open Event format
    json_converter.addEmpty(collectedData)
    return collectedData

def collect (query):
    # There are less than 5000 events, so setting the page size to 5000 will collect all search results
    scrape_url = '{}{}'.format('https://ticketleap.com/events/?page_size=5000&q=', query)
    # Gets search page content
    soup = getSoup(scrape_url)
    # Gets events links
    events = getEventsArray(soup)
    # Gets events information and prints it into folders to match the Open Event format
    getEventsData(query, events)
    print ('Done! :-)')

if __name__ == '__main__':
    if len(sys.argv) > 1:
        # Query words are separated by '+' in the search results URL
        query = '+'.join(sys.argv[1:])
        if not os.path.exists(query):
            os.mkdir(query)
        collect(query)
    else:
        print ('Please specify a query: python scrape_ticketleap.py [query]')
