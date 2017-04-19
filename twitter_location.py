#!/usr/env/bin python

import urllib2
from bs4 import BeautifulSoup

def get_location(userid):
    '''
    Get location as string ('Paris', 'New york', ..) by scraping twitter profils page.
    Returns None if location can not be scrapped
    '''

    page_url = 'http://twitter.com/{0}'.format(userid)

    try:
        page = urllib2.urlopen(page_url)
    except urllib2.HTTPError:
        print 'ERROR: user {} not found'.format(userid)
        return None

    content = page.read()
    html = BeautifulSoup(content)
    location = html.select('.ProfileHeaderCard-locationText')[0].text.strip()

    if location.strip() == '':
        return None
    return location.strip()
