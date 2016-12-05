import sys,json,requests
from bs4 import BeautifulSoup

scrape_api = "http://loklak.org/api/eventbritecrawler.json?url="
search_url = "https://www.eventbrite.com/d/worldwide/query/?crt=regular&sort=best" 
#replace "query" with user's query 

def makeSoup(url):
	raw_html = requests.get(url).text
	return BeautifulSoup(raw_html)

def getEvents(soup):
	events = []
	results = clearSoup(soup)
	for event in results.findAll('a'):
		href = event['href']
		if 'https://' in href:
			events.append(href)
	return events

def clearSoup(soup):
	results = soup.find('div', class_='js-event-list-container l-mar-stack l-mar-top-2')
	return results

def scrapeEvents(events):
	for url in events:
		json_data = requests.get(scrape_api+url).json()
		title = getEventTitle(url)
		print(title)
		writeOut(json_data, title)

def getEventTitle(event_url):
	title = event_url[29:-30].replace('/','')
	return title

def writeOut(data, event_name):
	with open(event_name+'.json', 'w+') as f:
		json.dump(data, f)

if len(sys.argv)>1:
	query = sys.argv[1]
	url = search_url.replace('query', query)
	soup = makeSoup(url)
	events = getEvents(soup)
	scrapeEvents(events)
else:
	print("    No query specified.")
	print("    Usage: python scrape_eventbrite.py [query]")