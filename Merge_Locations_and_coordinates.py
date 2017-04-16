#import sys
#import string
import os
import urllib
import simplejson
from twython import Twython
import pandas as pd
import numpy as np
import time

# Global Variable
filename = "trump_2016_test" # Specify filename or filepath here (without writing .csv extension)

#==============================================================================
#                  For Preprocessing of input CSV file
#==============================================================================
def preprocessing():
    suitable_num_cols = 0 
    df = pd.DataFrame()
    len_dict = {}
    with open(filename+'.csv', 'r', encoding = "utf-8", errors='ignore') as f:
        for line in f:
            list_cols = line.split(',')
            if len(list_cols) not in len_dict:
                len_dict[len(list_cols)] = 1
            else:
                len_dict[len(list_cols)] = len_dict[len(list_cols)] + 1
            
        
        x = sorted(len_dict)
        suitable_num_cols = min(len_dict)
        print(suitable_num_cols)
    x = 0
    w = 0
    f1  = open(filename+"_preprocessed.csv", 'w', encoding = "utf-8", errors='ignore')
    with open(filename+'.csv', 'r', encoding="utf-8", errors='ignore') as f:
        index = 0 # Stores index of 'text' column 
        for line in f:
            w = w + 1
            print("Line "+str(w)+" of input file processed")
            if x == 0:
                f1.write(line)
                col_names = line.split(',')
                for y in range(0,len(col_names)):
                    if col_names[y] == 'text':
                        index = y
                        x = 1
                        break
            else:    
                list_cols = line.split(',')
                if len(list_cols)>suitable_num_cols:
                    diff = len(list_cols)-suitable_num_cols
                    #print(list_cols)
                    #print(len(list_cols))
                    for i in range(0,diff):
                        list_cols[index] = list_cols[index]+"|"+list_cols[i+index+1]
                        #print(i)    
                    for k in range(index+1,len(list_cols)-diff):
                        list_cols[k] = list_cols[diff+k]
                        #print(list_cols[i])
                        #print(i)
                    #break
                    len_list = len(list_cols)  
                    for j in range(0,diff):
                        del list_cols[len_list-1-j]
                    list_cols[-1] = list_cols[-1].replace('\n','')    
                    for x in range(0,len(list_cols)):
                        if x == len(list_cols)-1:
                            f1.write(list_cols[x]+"\n")
                        else:
                            f1.write(list_cols[x]+",")
                    #print(new_line)
                else:
                    f1.write(line)

    f1.close() 


# Url of google maps
googleGeocodeUrl = 'http://maps.googleapis.com/maps/api/geocode/json?'

#==============================================================================
#          Finding the latitude and longitude of a location
#==============================================================================
def get_coordinates(query, from_sensor=False):
    params = {
        'address': query,
        'sensor': "true" if from_sensor else "false"
    }
    url = googleGeocodeUrl + urllib.parse.urlencode(params)
    json_response = urllib.request.urlopen(url)
    response = simplejson.loads(json_response.read())
    if response['results']:
        location = response['results'][0]['geometry']['location']
        latitude, longitude = location['lat'], location['lng']
        #print(query, latitude, longitude)
    else:
        latitude, longitude = None, None
        #print(query, "<no results>")
    return latitude, longitude

#==============================================================================
#                  Finding location from twitter profile
#==============================================================================

def get_Location():
    #FOR OAUTH AUTHENTICATION -- NEEDED TO ACCESS THE TWITTER API
    #REPLACE 'APP_KEY' WITH YOUR APP KEY, ETC., IN THE NEXT 4 LINES
    # CHANGE IT ACCORDINGLY
    t = Twython(app_key='lBaNqgwPDyOCuUOTBhvoicdsl', 
        app_secret='KmnqNaexMKTnkh2ELlB7me3v5KrKUHmQVLqeWInZwnBwMTpGXd',
        oauth_token='87985053-yVVsNuoqD9IsNoCC8xoJXlKqkI4IwpD5m6frXFMfn',
        oauth_token_secret='sTg9lKAQFfZ7pWyXBxEN0NxGx5aejgARc1jlSSFPKRXkK')

    df = pd.read_csv(filename+"_preprocessed.csv", encoding = "utf-8",low_memory=False)
       
    q = 0

    x = list(df.username.unique())

    # Number of unique usernames in the username list (x)
    #num_unique_usernames_in_csv = len(x)
    #print("Unique Usernames : " + str(num_unique_usernames_in_csv))

    user_loc = {}

    for username in x: 
        try:
            user = t.lookup_user(screen_name = username)
            print(q)
            for entry in user:
                location = entry['location']
                user_loc[username] = location
            q = q + 1
        except:
            print(q)
            user_loc[username] = '-'
            q = q + 1
    np.save('user_loc.npy', user_loc)

#==============================================================================
#                     Assign Locations from npy file
#==============================================================================
def assign_locations_from_npy_file():
    pd.options.mode.chained_assignment = None
    saved_user_loc = np.load('user_loc.npy').item() # This is a saved dictionary
    df = pd.read_csv(filename+"_preprocessed.csv", encoding = "utf-8",low_memory=False)

    for index, row in df.iterrows():
        location = saved_user_loc[df['username'][index]]
        if location == '':
            location = '-'
        df.set_value(index, 'Location', location)
        print(index) # For debugging purpose
    df.to_csv(filename+'_with_assigned_locations_.csv', sep=',',encoding = "utf-8", index=False)      
        

#==============================================================================
#               Finding Geo coordinates of the locations
#==============================================================================    
def find_geo_coordinates():
    pd.options.mode.chained_assignment = None
    df = pd.read_csv(filename+'_with_assigned_locations_.csv', encoding = "utf-8",low_memory=False)

    # Storing unique places geocoordinates in a list
    lat = {}
    long = {}    
    x = list(df.Location.unique())
    total_usernames = len(df.username)
    unique_usernames = len(list(df.username.unique()))
    q = 0
    for loc in x:
        print(loc) # For debugging purpose
        q = q+1
        print(str(q)) # For debugging purpose
        locat = str(loc)
        if locat != 'nan' and locat != '':
            location = ''
            # Check for undesired Characters
            for i in range(len(locat)):
                if i==0 and not locat[i].isalpha() and not ((ord(locat[i])>=97 and ord(locat[i])<=122) or (ord(locat[i])>=65 and ord(locat[i])<=90)):
                    continue
                elif (locat[i].isalpha() and ((ord(locat[i])>=97 and ord(locat[i])<=122) or (ord(locat[i])>=65 and ord(locat[i])<=90))) or locat[i] == ' ' or locat[i] == '\'' or locat[i] == '\\' or locat[i] == '&' or locat[i] == ',':
                    location = location + locat[i]
                else:
                    break
            
            # Get coordinates only when location has a valid value    
            if location != 'nan' and location != '':
                if location[0].isalpha() and ((ord(locat[0])>=97 and ord(locat[0])<=122) or (ord(locat[0])>=65 and ord(locat[0])<=90)):
                    x, y = get_coordinates(str(location))
                    print(location, x, y) # For debugging purpose
                    lat[location] = str(x)
                    long[location] = str(y)

    df['Latitude'] = ''
    df['Longitude'] = ''
    
    ###############    Usernames count variables    ############
    num_known_username_loc = 0 # Stores number of usernames whose geolocation is known
    num_unknown_username_loc = 0 # # Stores number of usernames whose geolocation is unknown

    
    # Adding Latitude and Longitude columns to df
    for index, row in df.iterrows():
        locat = str(df['Location'][index])
        if locat != 'nan' and locat != '':
            location = ''
            for i in range(len(locat)):
                if i==0 and not locat[i].isalpha() and not ((ord(locat[i])>=97 and ord(locat[i])<=122) or (ord(locat[i])>=65 and ord(locat[i])<=90)):
                    continue
                elif (locat[i].isalpha() and ((ord(locat[i])>=97 and ord(locat[i])<=122) or (ord(locat[i])>=65 and ord(locat[i])<=90))) or locat[i] == ' ' or locat[i] == '\'' or locat[i] == '\\' or locat[i] == '&' or locat[i] == ',':
                    location = location + locat[i]
                else:
                    break
            
            if location != 'nan' and location != '':
                if location[0].isalpha() and ((ord(locat[0])>=97 and ord(locat[0])<=122) or (ord(locat[0])>=65 and ord(locat[0])<=90)):
                    if lat[location] == 'None' and long[location] == 'None':
                        lat[location] = 'Unknown'
                        long[location] = 'Unknown'
                        df['Latitude'][index] = lat[location]
                        df['Longitude'][index] = long[location]
                    else:
                        df['Latitude'][index] = lat[location]
                        df['Longitude'][index] = long[location]
                        
                else:
                    df['Latitude'][index] = 'Unknown'
                    df['Longitude'][index] = 'Unknown'
                    
            else:
                df['Latitude'][index] = 'Unknown'
                df['Longitude'][index] = 'Unknown'
        else:
             df['Latitude'][index] = 'Unknown'
             df['Longitude'][index] = 'Unknown'
             

    df.to_csv(filename+"_with_geo_coordinates.csv", sep=',',encoding = "utf-8", index=False)

    df = pd.read_csv(filename+"_with_geo_coordinates.csv", encoding = "utf-8",low_memory=False)
    for index, row in df.iterrows():
        if row['Latitude'] == 'Unknown' and row['Longitude'] == 'Unknown':
            num_unknown_username_loc = num_unknown_username_loc + 1
        else:
            num_known_username_loc = num_known_username_loc + 1
            
    df1 = pd.DataFrame()
    df1['Total Input Usernames'] = ''
    df1['Total Known GeoLocations'] = ''
    df1['Total Unknown Geolocations'] = ''
    df1['Total Unique Usernames'] = ''
    
    df1.set_value(0, 'Total Input Usernames', total_usernames)
    df1.set_value(0, 'Total Known GeoLocations', num_known_username_loc)
    df1.set_value(0, 'Total Unknown Geolocations', num_unknown_username_loc)
    df1.set_value(0, 'Total Unique Usernames', unique_usernames)
    df1.to_csv(filename+"_with_stats_temp.csv", sep=',',encoding = "utf-8", index=False)



start_time = time.time()



##########    Function Calls    #########
preprocessing() # Only needs to be called once per dataset
print("Preprocessing finished")
get_Location()  # only needs to be run once per dataset
print("get_Location task completed")
assign_locations_from_npy_file()
print("Assigned locations from npy file completed")
find_geo_coordinates()
print("Script successfully executed")
# Calculating the time taken to execute the code
time_taken = time.time() - start_time

df = pd.read_csv(filename+"_with_stats_temp.csv", encoding = "utf-8",low_memory=False)
df['Total Time Taken(in seconds)'] = ''
df.set_value(0, 'Total Time Taken(in seconds)', time_taken)
df.to_csv(filename+"_with_stats.csv", sep=',',encoding = "utf-8", index=False)
os.remove(filename+"_with_stats_temp.csv")

#print("Time taken : "+str(time_taken) + " seconds")
