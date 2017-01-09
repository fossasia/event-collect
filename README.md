# Event-Collect

[![Build Status](https://travis-ci.org/fossasia/event-collect.svg?branch=master)](https://travis-ci.org/fossasia/event-collect)

event website listing to Open Event format scraper and converter

#EventBrite Scraper
Given a query, scrapes EventBrite search results and downloads JSON files of each event using [Loklak's API](https://github.com/loklak/loklak_server/blob/development/docs/parsers.md#event-brite-crawler)

Usage: 
```python scrape_eventbrite.py [SEARCH QUERY]```

To install all python dependencies required:
```pip install -r requirements.txt```

Running that command will install:
```
requests==2.10.0
beautifulsoup4==4.5.1
```
