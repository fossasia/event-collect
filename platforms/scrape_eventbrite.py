import sys,json,requests
from bs4 import BeautifulSoup

def makeSoup(url):
	pass

def getEventsLinks(soup):
	pass

def scrapeEvents(urls):
	pass

if len(sys.argv)>1:
	query = sys.argv[1]
else:
	print("    No query specified.")
	print("    Usage: python scrape_eventbrite.py [query]")
