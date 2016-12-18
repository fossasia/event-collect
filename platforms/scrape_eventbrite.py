import os,sys,json,requests
from bs4 import BeautifulSoup

LOKLAK_API_ENDPOINT = "http://loklak.org/api/eventbritecrawler.json"
SEARCH_URL = "https://www.eventbrite.com/d/worldwide/%s/?crt=regular&sort=best" 


def makeSoup(url):
        '''
        Utility function to create a BeautifulSoup object of the HTML content of passed web page URL.

        :param url: URL of web page
        ''' 
        raw_html = requests.get(url).text
        return BeautifulSoup(raw_html)


def clearSoup(soup):
        '''
        Utility function to find results div object and return the same

        :param soup: BeautifulSoup object of the web page
        '''
        results = soup.find('div', class_='js-event-list-container l-mar-stack l-mar-top-2')
        return results


def getEvents(soup):
        '''
        Generate list of event URLs

        :param soup: BeautifulSoup object of search result page from eventbrite.com
        '''
        events = []

        # find the results div object
        results = clearSoup(soup)

        # save all event URLs to events list
        for event in results.findAll('a'):
                href = event['href']
                if href.startswith('https'):
                        events.append(href)
                        
        return events


def scrapeEvents(events, query):
        '''
        Get event data using LOKLAK API and save the event as a JSON file
        in a directory having same name as the query

        :param events: List of event URLs
        '''
        
        # creating folder by the query name (If doesnt exist)
        if not os.path.exists(query):
                os.mkdir(query)

        # setting the directory name
        dir_name = query

        print("Following events were found:")
        # generating json data and saving it for each event    
        for url in events:
                json_data = requests.get(LOKLAK_API_ENDPOINT, params = {'url':url}).json()['data']
                event_path = dir_name + '/' + getEventTitle(url)
                # creating folder by event name
                if not os.path.exists(event_path):
                        os.mkdir(event_path)
                print(event_path)
                writeOut(json_data, event_path)


def getEventTitle(event_url):
        '''
        Utility function to generate title from event URL

        :param event_url: URL of the event
        '''
        title = event_url.split('/')[-1].split('?')[0].split('-tickets')[0]
        return title


def writeOut(data, event_path):
        '''
        Utility function to write data to given file path

        :param data: data to be written to the file
        :param event_path: path to the event directory
        '''
        file_names = ['/event.json', '/organizers.json', '/microlocations.json', '/forms.json',
                      '/session_types.json', '/sessions.json', '/sponsors.json', '/speakers.json', '/tracks.json']

        for x in range(len(file_names)):
                with open(event_path + file_names[x], 'w+') as f:
                        json.dump(data[x], f, indent = 4)


def eventCollector(query):
        '''
        Main function which calls other sub-functions to collect and save events

        :param query: event query
        '''
        # generate Event Brite(EB) URL for given search query
        EB_URL = SEARCH_URL%query
        # create BeautifulSoup object for EB results page
        soup = makeSoup(EB_URL)
        # get a list of event URLs
        events = getEvents(soup)
        # get event data and save it as JSON file
        scrapeEvents(events, query)
        

if __name__ == "__main__":
        if len(sys.argv) > 1:
                query = sys.argv[1]
                eventCollector(query)
        else:
                print("    No query specified.")
                print("    Usage: python scrape_eventbrite.py [query]")
