#!/usr/env/bin python

import urllib2
from bs4 import BeautifulSoup

with open('00_Trump_05_May_2016.csv', 'r') as csv:
    next(csv)
    for line in csv:
        line = line.strip()

        permalink = line.split(',')[-1].strip()
        username  = line.split(',')[0]
        userid    = permalink.split('/')[3]

        page_url = 'http://twitter.com/{0}'.format(userid)

        try:
            page = urllib2.urlopen(page_url)
        except urllib2.HTTPError:
            print 'ERROR: username {} not found'.format(username)
        content = page.read()
        html = BeautifulSoup(content)
        location = html.select('.ProfileHeaderCard-locationText')[0].text.strip()

        print 'username {0} ({1}) located in {2}'.format(username, userid, location)

