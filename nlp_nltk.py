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

STANFORD_JAR_FILE = './stanford-ner/stanford-ner.jar'
STANFORD_ENG_FILE = './stanford-ner/classifiers/english.all.3class.distsim.crf.ser.gz'

INTRODUCTION = "Hello. I am LASTMINUTE-HELPER. If you want to go for a city trip and you haven't decided yet where to," \
               "then I'm your man...amm bot. I can help you to decide between 2 cities, give you more information about 1 city or even" \
               "give you my personal suggestion of the day if you don't have any plan. But first things first: What's your origin ?"

GENERAL_RESPONSES = ["We will see", "Ok, but that's not really true", "You wanna think about it again ?",
                     "...Rom wasn't build in a day", "I know, Mordor is the real problem",
                     "Sometimes it's better to stay home",
                     "I din't catch that to be honest", "That's interesting, but let's talk CITIES :)",
                     "Even a broken watch is two times right per day..."]

GREETING_RESPONSES = ["hello back !", "hi, how are you ?", "What's up", "Nice to hear from you, how can I serve ?", "Good Day"]

GREETING_SET = {"hello", "hi", "yo", "how are you", "hi man", "hey", "what's up", "good morning", "good evening","good afternoon"}

RESPONSE_FOUND_1_CITY = "You want to know more about {}, is this correct ?"
RESPONSE_FOUND_2_CITIES = "You want to compare {} with {}, correct ?"

CONFIRMATIONS_SET = {"yes", "y", "yep", "ok", "correct"}

DESCRIBE_WHEATHER_1_CITY = "First of all, let's talk about the weather in {}. The temperature will be {} °C tomorrow"
DESCRIBE_WHEATHER_2_CITIES = "In {} it will be {} °C and in {} {} °C tomorrow"

ASK_FOR_INSTRUCTIONS = "Sorry for that. Please ask me again in other words."

def random_answer():
    return random.choice(GENERAL_RESPONSES)

def check_for_greeting(sentence):
    return any(greeting in sentence for greeting in GREETING_SET)

def give_random_greeting():
    resp = random.choice(GREETING_RESPONSES)
    return resp

def _check_for_confirmation(sentence):
    return any(confirmation in sentence for confirmation in CONFIRMATIONS_SET)

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
            return "origin set to {}".format(cities[0])
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

    def compare_two_cities(self):
        sunny1, temp1 = get_wheather(self.city1)
        sunny2, temp2 = get_wheather(self.city2)
        return DESCRIBE_WHEATHER_2_CITIES.format(self.city1, temp1, self.city2, temp2)


    def confirm_city(self, number_cities, sentence):
        self.reset_config_variables(confirmations=True)
        if _check_for_confirmation(sentence):
            if number_cities == 1:
                return self.describe_one_city()
            elif number_cities == 2:
                return self.compare_two_cities()
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
