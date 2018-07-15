from datetime import datetime
import time
import json
import googlemaps # Use the wrapper
import re
import numpy as np
from db_setup import Dealers

# Connect to GoogleMaps
key = 'AIzaSyDhjoU4gFGIJ5VTTaexR_4_tDoaMvbgCaA'
client = googlemaps.Client(key)

carnovo = client.places(query = 'carnovo')
base = carnovo['results'][0]['geometry']['location'] # carnovo coordinates

NAMES = []
PCODES = []

def address2pCode(address):
    pCode = re.compile('[0-9]{5}') # Match a number that has 5 digits (like a postal code)
    return pCode.findall(address)
def output2NamePCode(output):
    results = output['results']
    addresses = map(lambda x: x['formatted_address'], results)
    pCodes = map(address2pCode,addresses)
    names = map(lambda x: x['name'], results)
    return names, pCodes
def searchAndExtend(query, NAMES, PCODES):
    around = client.places(query = query, location = base, radius = 100000,
                           language = 'En')
    token = around['next_page_token']
    names, pCodes = output2NamePCode(around)
    NAMES.extend(names)
    PCODES.extend(pCodes)

    time.sleep(3) # otherwise nextpage_token invalid

    around = client.places(query = query, location = base, radius = 100000,
                               language = 'En', page_token=token)
    names, pCodes = output2NamePCode(around)
    NAMES.extend(names)
    PCODES.extend(pCodes)

# Search for 'Concesionario and more'
searchAndExtend('Concesionario', NAMES, PCODES)
#searchAndExtend('Car Dealer', NAMES, PCODES)
#searchAndExtend('Audi OR BMW OR Citro\xc3\xabn OR DS OR Dacia OR Fiat OR Ford', NAMES, PCODES)
#searchAndExtend('Honda OR Hyundai OR Jeep OR Kia OR Land Rover OR MINI OR Mazda', NAMES, PCODES)
#searchAndExtend('Mercedes-Benz OR Nissan OR Opel OR Peugeot OR Renault OR SEAT', NAMES, PCODES)
#searchAndExtend('Skoda OR SsangYong OR Subaru OR Suzuki OR Toyota OR Volkswagen OR Volvo', NAMES, PCODES)

# Sorting out the unique ones (No Overlap wanted)
pcodes = map(lambda x: x[0], PCODES)
entries = zip(NAMES, map(lambda x: x[0], PCODES))
RESULT = list(set(entries))

# Connect to DB

from flask import Flask, redirect, render_template, request, url_for
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Integer, Float, Column, ForeignKey, String

app = Flask(__name__)

SQLALCHEMY_DATABASE_URI = "mysql+mysqlconnector://{username}:{password}@{hostname}/{databasename}".format(
    username="DennisDemenis",
    password="advanced",
    hostname="DennisDemenis.mysql.pythonanywhere-services.com",
    databasename="DennisDemenis$cardealers",
)
app.config["SQLALCHEMY_DATABASE_URI"] = SQLALCHEMY_DATABASE_URI
app.config["SQLALCHEMY_POOL_RECYCLE"] = 299
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)

# Now save the results in a Database
for result in RESULT:
    dealer = Dealers(name = result[0], pcode=result[1])
    db.session.add(dealer)
db.session.commit()

