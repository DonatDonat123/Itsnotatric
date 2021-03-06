import random
import numpy as np
import logging
import os
import pyowm
from pyowm import timeutils
# Import for DistanceMatrix
from datetime import datetime
import googlemaps

key = 'AIzaSyDhjoU4gFGIJ5VTTaexR_4_tDoaMvbgCaA'
client = googlemaps.Client(key)
#####
owm = pyowm.OWM('08d83af8b06526025140d9752d6fb9b3')  # You MUST provide a valid API key

import nltk
from nltk.tag import StanfordNERTagger
from nltk.tokenize import word_tokenize

from strings.city_list import CITIES
from strings.responses import TRAVELMODE, INTRODUCTION, GENERAL_RESPONSES, GREETING_RESPONSES, GREETING_SET, RESPONSE_FOUND_1_CITY, \
                              RESPONSE_FOUND_2_CITIES, CONFIRMATIONS_SET, WHEATHER_SET, DISTANCE_SET, DESCRIBE_WHEATHER_1_CITY, \
                              DESCRIBE_WHEATHER_2_CITIES, DESCRIBE_TRAVELTIME_2_CITIES, WHEATHER_OR_DISTANCE, ASK_FOR_INSTRUCTIONS

STANFORD_JAR_FILE = './stanford-ner/stanford-ner.jar'
STANFORD_ENG_FILE = './stanford-ner/classifiers/english.all.3class.distsim.crf.ser.gz'

def random_answer():
    return random.choice(GENERAL_RESPONSES)

def check_for_greeting(sentence):
    return any(greeting in sentence for greeting in GREETING_SET)

def give_random_greeting():
    resp = random.choice(GREETING_RESPONSES)
    return resp

def _check_for_confirmation(sentence):
    return any(confirmation in sentence for confirmation in CONFIRMATIONS_SET)

def _check_for_wheather(sentence):
    return any(confirmation in sentence for confirmation in WHEATHER_SET)

def _check_for_distance(sentence):
    return any(confirmation in sentence for confirmation in DISTANCE_SET)

def words_in_city_list(tokenized_text):
    cities_found = []
    for word in tokenized_text:
        if word in CITIES:
            cities_found.append(word)
    return cities_found

def get_wheather(city):
    fc1 = owm.daily_forecast(city)
    tomorrow = pyowm.timeutils.tomorrow()
    sunny = fc1.will_be_sunny_at(tomorrow)
    weather1 = fc1.get_weather_at(tomorrow)
    temperature = np.round(weather1.get_temperature(unit='celsius')["day"]).astype(int)
    return sunny, temperature

def traveltime_between_cities(city1, city2, travel_mode):
    """Valid values for travel_mode are driving, walking, transit or bicycling"""
    client = googlemaps.Client(key)
    now = datetime.now()
    travel_information = client.distance_matrix(city1, city2, mode=travel_mode, language="en-AU",
                                                avoid="tolls",departure_time=now,
                                                units="imperial", traffic_model="optimistic")
    duration = travel_information['rows'][0]['elements'][0]['duration']['text']
    return duration

class NLP:
    def __init__(self):
        print("NLP class was created")
        self._reset_all_config_variables()
        self.tagger = StanfordNERTagger(STANFORD_ENG_FILE, STANFORD_JAR_FILE, encoding='utf-8')

    def _reset_all_config_variables(self,verbose = False):
        self.reset_config_variables(all_except_origin=True, origin=True, verbose=verbose)

    def reset_config_variables(self, all_except_origin = False, city1 = False, city2 = False, many_cities = False,
                               blindshot = False, confirmations = False, ask_for_origin = False, origin = False, verbose = False):
        if city1 or all_except_origin:
            self.city1 = None
        if city2 or all_except_origin:
            self.city2 = None
        if many_cities or all_except_origin:
            self.many_cities = None
        if blindshot or all_except_origin:
            self.blindshot = False
        if confirmations or all_except_origin:
            self.need_confirmation_1_city = False
            self.need_confirmation_2_cities = False
            self.need_confirmation_wheather_or_distance = False
        if ask_for_origin or all:
            self.ask_for_origin = False
        if origin:
            self.origin = None
        if verbose:
            return "Everything reset, what do you want to do now ?"

    def set_origin(self, text):
        cities = self._find_cities(text)
        if len(cities) == 0:
            return "I don't know this city, again please."
        elif len(cities) == 1:
            self.ask_for_origin = False
            self.origin = cities[0]
            return "origin set to {}, what do you want to know now ?".format(cities[0])
        elif len(cities) > 1:
            return self.found_many_cities(1)

    def ask_for_instructions(self):
        self.reset_config_variables(all_except_origin=True)
        return ASK_FOR_INSTRUCTIONS

    def introduction(self):
        return INTRODUCTION

    def _find_cities(self, text):
        tokenized_text = word_tokenize(text)
        tagged_text = np.array(self.tagger.tag(tokenized_text))
        print("tagged_text: {}".format(tagged_text))
        cities = set(tagged_text[tagged_text[:, 1] == 'LOCATION'][:, 0])
        cities2 = words_in_city_list(tokenized_text)
        cities.update(cities2)
        return list(cities)

    def check_for_cities(self, text):
        cities = self._find_cities(text)
        if len(cities) == 0:
            return False
        elif len(cities) == 1:
            self.city1 = cities[0]
            self.need_confirmation_1_city = True
            return True
        elif len(cities) == 2:
            self.city1 = cities[0]
            self.city2 = cities[1]
            self.need_confirmation_2_cities = True
            return True
        elif len(cities) > 2:
            self.many_cities = cities
            return True

    def found_1_city(self):
        self.need_confirmation_1_city = True
        return RESPONSE_FOUND_1_CITY.format(self.city1)

    def found_2_cities(self):
        self.need_confirmation_2_cities = True
        return RESPONSE_FOUND_2_CITIES.format(self.city1, self.city2)

    def found_many_cities(self, number_cities_wanted):
        response = "I detected: "
        response += "{}".format(self.many_cities[0])
        for city in self.many_cities[1:]:
            response += (", {}".format(city))
        response += (". Please decide for {} cities".format(number_cities_wanted))
        return response

    def describe_one_city(self):
        sunny1, temp1 = get_wheather(self.city1)
        return DESCRIBE_WHEATHER_1_CITY.format(self.city1, temp1)

    def compare_two_cities_wheather(self):
        sunny1, temp1 = get_wheather(self.city1)
        sunny2, temp2 = get_wheather(self.city2)
        return DESCRIBE_WHEATHER_2_CITIES.format(self.city1, temp1, self.city2, temp2)

    def compare_two_cities_traveltime(self):
        traveltime1 = traveltime_between_cities(self.origin, self.city1, TRAVELMODE)
        traveltime2 = traveltime_between_cities(self.origin, self.city2, TRAVELMODE)
        if traveltime1 > traveltime2:
            return DESCRIBE_TRAVELTIME_2_CITIES.format(self.origin, traveltime2, self.city2, traveltime1, self.city1)
        else:
            return DESCRIBE_TRAVELTIME_2_CITIES.format(self.origin, traveltime1, self.city1, traveltime2, self.city2)

    def ask_wheather_or_distance(self):
        self.need_confirmation_wheather_or_distance = True
        return WHEATHER_OR_DISTANCE

    def confirm_by_distance_or_wheather(self, sentence):
        if _check_for_wheather(sentence):
            self.need_confirmation_wheather_or_distance = False
            return self.compare_two_cities_wheather()
        if _check_for_distance(sentence):
            self.need_confirmation_wheather_or_distance = False
            return self.compare_two_cities_traveltime()
        else:
            return "I didn't get that. Again: distance or wheather ?"

    def confirm_city(self, number_cities, sentence):
        self.reset_config_variables(confirmations=True)
        if _check_for_confirmation(sentence):
            if number_cities == 1:
                return self.describe_one_city()
            elif number_cities == 2:
                return self.ask_wheather_or_distance()
            else: raise ValueError("can only confirm for 1 or 2 cities")
        else:
            return self.ask_for_instructions()

    def respond(self, sentence):
        print('input message = {}'.format(sentence))
        resp = None
        if any(sentence in s for s in ("start", "\start")):
            self._reset_all_config_variables(verbose=False)
            self.ask_for_origin = True
            response = self.introduction();
        elif any(sentence in s for s in ("reset", "cancel")):
            response = self._reset_all_config_variables(verbose=True)
        elif self.ask_for_origin:
            response = self.set_origin(sentence)
        elif self.need_confirmation_1_city:
            response = self.confirm_city(1, sentence)
        elif self.need_confirmation_2_cities:
            response = self.confirm_city(2, sentence)
        elif self.need_confirmation_wheather_or_distance:
            response = self.confirm_by_distance_or_wheather(sentence)
        elif check_for_greeting(sentence):
            response = give_random_greeting()
        elif self.check_for_cities(sentence):
            if self.many_cities is not None: response = self.found_many_cities(2)
            elif self.city1 and self.city2: response = self.found_2_cities()
            elif self.city1: response = self.found_1_city()
        else:
            response = random_answer();
        print ("response = {}".format(response))
        return response

if __name__ == "__main__":
    nlp = NLP()
    nlp.respond("start")
    nlp.respond("Berlin")
    nlp.respond("Tell me about Berlin and Karlsruhe")
    nlp.respond("yes")
    nlp.respond("distance")
