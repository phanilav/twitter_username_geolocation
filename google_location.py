import urllib
import urllib2
import simplejson

googleGeocodeUrl = 'http://maps.googleapis.com/maps/api/geocode/json?'

def get_coordinates(query, from_sensor=False):
    '''
    Get coordinates (lat, long) from location as string.
    '''

    params = {
        'address': query,
        'sensor': "true" if from_sensor else "false"
    }
    url = googleGeocodeUrl + urllib.urlencode(params)
    json_response = urllib2.urlopen(url)
    response = simplejson.loads(json_response.read())
    if response['results']:
        location = response['results'][0]['geometry']['location']
        latitude, longitude = location['lat'], location['lng']
        #print(query, latitude, longitude)
    else:
        latitude, longitude = None, None
        #print(query, "<no results>")
    return latitude, longitude

