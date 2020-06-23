# Copyright 2020 Andy Prevalsky

# Permission is hereby granted, free of charge, to any person obtaining a copy of this 
# software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all copies or substantial 
# portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED 
# TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL 
# THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF 
# CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS 
# IN THE SOFTWARE.

import requests
import math
import threading
import time
url = "https://maps.googleapis.com/maps/api/geocode/json"

startLat = 44.977753
startLng = -93.265015
radiusInMiles = .1 #less than 1

GOOGLE_MAP_API_KEY = "" # PUT YOUR Google Maps API KEY HERE

def getDistanceFromLatLonInMi(lat1,lon1,lat2,lon2):
    R = 6371; # Radius of the earth in km
    dLat = deg2rad(lat2-lat1)  # deg2rad below
    dLon = deg2rad(lon2-lon1) 
    a = math.sin(dLat/2) * math.sin(dLat/2) + math.cos(deg2rad(lat1)) * math.cos(deg2rad(lat2)) * math.sin(dLon/2) * math.sin(dLon/2)
        
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a)) 
    d = R * c # Distance in km
    return d * .621371

def deg2rad(deg):
  return deg * (math.pi/180)


addressSet = set()

class getAddressInfo(threading.Thread):
    """ trys to but the stock passed in 
    constructor, and puts into tracking queue
    on success """

    def __init__(self, lat, lng):
        self.lat = lat
        self.lng = lng
        threading.Thread.__init__(self)
    
    def run(self):
        global addressSet
        querystring = {"latlng":str(self.lat)+','+str(self.lng),"key":GOOGLE_MAP_API_KEY}
        response = requests.request("GET", url, params=querystring)
        streetNumber = ''
        address = ''
        city = ''
        state = ''
        country = ''
        postalCode = ''
        try:
            for i in response.json()['results'][0]['address_components']:
                if i['types'][0] == 'street_number': streetNumber = i['long_name']
                if i['types'][0] == 'route': address = i['long_name']
                if i['types'][0] == 'locality': city = i['long_name']
                if i['types'][0] == 'administrative_area_level_1': state = i['short_name']
                if i['types'][0] == 'country': country = i['short_name']
                if i['types'][0] == 'postal_code': postalCode = i['long_name']
            addressSet.add(' '.join([streetNumber, address, city, state, postalCode, country]))
        except:
            print(response.json())

count = 0
totalCount = 0
for i in range(-177, 176):
    for j in range(-177, 176):
        latInc = j*.0001
        lngInc = i*.0001
        dist  = getDistanceFromLatLonInMi(startLat, startLng, startLat+latInc, startLng+lngInc)
        if (dist < radiusInMiles):
            getAddressInfo(startLat+latInc, startLng+lngInc).start()
            count += 1
            totalCount += 1
            if (count == 50):
                time.sleep(1)
                count = 0

for val in addressSet:
    print(val)

print(len(addressSet))