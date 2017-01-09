import requests
import os
import datetime

''' Collects data from the main page. Since some fields may not always exist,
try-except/if-else statements were included in order to prevent errors.
'''
def addHome (data, soup, url):
    data[0]['ticket_url'] = '{}{}'.format(url, 'dates')
    data[0]['name'] = soup.select('h1 span')[0].getText().strip()
    ''' Getting the start and end dates is a bit more complicated and depends
    on the page structure, thus there's another function for it
    '''
    getEventDates(data, soup)
    try:
        data[0]['location_name'] = soup.select('.venue span')[1].getText()
    except Exception:
        data[0]['location_name'] = ''
    if len(soup.select('.all-dates-in-past')):
        data[0]['state'] = 'Finished'
    else:
        data[0]['state'] = 'Unfinished'

def getEventDates (data, soup):
    # The event takes place over a single day
    date_info = soup.select('.mobile-only .date-range-date')
    if len(date_info) == 1:
        start_date = end_date = date_info[0].getText()
        start_time = soup.select('.date-range-time-start')[0].getText()
        end_time = soup.select('.date-range-time-end')[0].getText()
    else:
        start_date = date_info[0].getText()
        end_date = date_info[1].getText()
        start_time = soup.select('.date-range-start .date-range-time')[0].getText()
        end_time = soup.select('.date-range-end .date-range-time')[0].getText()
    start = '{} {}'.format(start_date, start_time)
    end = '{} {}'.format(end_date, end_time)
    start = datetime.datetime.strptime(start, '%a, %b %d %Y %I:%M %p').strftime('%Y-%m-%dT%H:%M:%S')
    end = datetime.datetime.strptime(end, '%a, %b %d %Y %I:%M %p').strftime('%Y-%m-%dT%H:%M:%S')
    data[0]['start_time'] = start
    data[0]['end_time'] = end

def addImage (data, soup, path):
    # Creates 'img' folder
    image_dir = '{}{}/'.format(path, 'img')
    if not os.path.exists(image_dir):
        os.mkdir(image_dir)
    image_file = '{}{}'.format(image_dir, 'background.jpg')
    # The background image URL is stored in a meta tag
    backgroundURL = soup.select('meta')[9]['content']
    # The image is downloaded using the requests library
    response = requests.get(backgroundURL)
    with open(image_file, "wb") as output_file:
        output_file.write(response.content)
    # Its path is added to the json structure
    data[0]['background_image'] = 'img/background.jpg'

def addOrganizer (data, soup, url):
    organizer = {}
    organizer['organizer_contact_info'] = '{}{}'.format(url, 'contact')
    end_index = url.index('.com') + 4
    organizer['organizer_link'] = url[:end_index]
    organizer['organizer_profile_link'] = ''
    org_name = soup.select('.top h3')[0].getText()
    # Gets the organizer name from string 'By org_name (other events)'
    data[0]['organizer_name'] = organizer['organizer_name'] = org_name[3:len(org_name)-15]
    data.append(organizer)

# Adds the event descriptions and the social media links
def addAbout (data, soup):
    data[0]['description'] = soup.select('.event-description')[0].getText().strip()
    data[0]['social_links'] = []
    social_links = soup.select('.social a')
    if len(social_links) < 1:
        return
    index = 0
    for site in social_links:
        index += 1
        social_media = {}
        social_media['id'] = index
        social_media['name'] = site.select('p')[0].getText()
        ''' The email link is a relative one, so the 'organizer_contact_info' (absolute)
        link is used instead, since they coincide
        '''
        if social_media['name'] == 'Email Us':
            social_media['link'] = data[1]['organizer_contact_info']
        else:
            social_media['link'] = site['href']
        data[0]['social_links'].append(social_media)

# Latitude and longitude of the event location are kept in meta tags
def addLocation (data, soup):
    data[0]['latitude'] = soup.select('meta')[10]['content']
    data[0]['longitude'] = soup.select('meta')[11]['content']

# There is no event data matching the below fields, so they are left empty
def addEmpty (data):
    data[0]['type'] = data[0]['topic'] = ''
    data.append({'microlocations': []})
    data.append({'customForms': []})
    data.append({'sessionTypes': []})
    data.append({'sessions': []})
    data.append({'sponsors': []})
    data.append({'speakers': []})
    data.append({'tracks': []})
