#!/usr/bin/python

import sys
from twitter_location import get_location
from google_location import get_coordinates

# Open output file
outputfile = open(sys.argv[2], 'w')

# Read input file
with open(sys.argv[1], 'r') as csv:
    # Skip headers line
    next(csv)
    # Loop in lines
    for line in csv:
        # Extract userid
        print line
        permalink = line.split(',')[-1].strip()
        userid    = permalink.split('/')[3]
        # Get location as string if exists
        location = get_location(userid)
        if location is None:
            print 'user {} can not be reached or do not exposes any location.'.format(userid)
            continue
        else:
            # If location is ok, get coordinates
            coordinates = get_coordinates(location)
            print '{}: {}'.format(userid, coordinates)

            # Copy current input line and add coordinates at the end
            newline = '{},{}\n'.format(line.strip(), coordinates)
            # Write in output file
            outputfile.write(newline)
