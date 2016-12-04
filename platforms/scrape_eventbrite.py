import sys,json,requests
from bs4 import BeautifulSoup

scrape_api = "http://loklak.org/api/eventbritecrawler.json?url="
search_url = "https://www.eventbrite.com/d/worldwide/query/?crt=regular&sort=best" 
#replace "query" with user's query 

def makeSoup(url):
	pass

def getEventsLinks(soup):
	pass

def scrapeEvents(urls):
	for url in urls:
		json_data = requests.get(scrape_api+url).json()
		writeOut(json_data)

def writeOut(data):
	with open('results.json', 'w') as f:
		json.dump(data, f)

if len(sys.argv)>1:
	query = sys.argv[1]
else:
	print("    No query specified.")
	print("    Usage: python scrape_eventbrite.py [query]")