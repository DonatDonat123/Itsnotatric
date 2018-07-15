"""Tests for the distance matrix module."""

from datetime import datetime
import time
import json

import googlemaps


key = 'AIzaSyDhjoU4gFGIJ5VTTaexR_4_tDoaMvbgCaA'
client = googlemaps.Client(key)
origin = "Perth, Australia"
destination = "Sydney, Australia"
now = datetime.now()
duration = client.distance_matrix(origin,destination)
duration_now = client.distance_matrix(origin, destination,
                                            mode="driving",
                                            language="en-AU",
                                            avoid="tolls",
                                            units="imperial",
                                            departure_time=now,
                                            traffic_model="optimistic")
duration_bike = client.distance_matrix(origin, destination, mode="bicycling")

distance = duration['rows'][0]['elements'][0]['distance']['text']
zeit = duration['rows'][0]['elements'][0]['duration']['text']

print duration