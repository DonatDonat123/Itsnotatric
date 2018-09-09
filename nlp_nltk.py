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


STANFORD_JAR_FILE = './stanford-ner/stanford-ner.jar'
STANFORD_ENG_FILE = './stanford-ner/classifiers/english.all.3class.distsim.crf.ser.gz'

INTRODUCTION = "Hello. I am LASTMINUTE-HELPER. If you want to go for a city trip and you haven't decided yet where to," \
               "then I'm your man...amm bot. I can help you to decide between 2 cities, give you more information about 1 city or even" \
               "give you my personal suggestion of the day if you don't have any plan. But first things first: What's your origin ?"

GENERAL_RESPONSES = ("We will see", "Ok, but that's not really true", "You wanna think about it again ?",
                     "...Rom wasn't build in a day", "I know, Mordor is the real problem",
                     "Sometimes it's better to stay home",
                     "I din't catch that to be honest", "That's interesting, but let's talk CITIES :)",
                     "Even a broken watch is two times right per day...")

GREETING_RESPONSES = ("hello back !", "hi, how are you ?", "What's up", "Nice to hear from you, how can I serve ?", "Good Day")

GREETING_SET = ("hello", "hi", "yo", "how are you", "hi man", "hey", "what's up", "good morning", "good evening","good afternoon")

RESPONSE_FOUND_1_CITY = "You want to know more about {}, is this correct ?"
RESPONSE_FOUND_2_CITIES = "You want to compare {} with {}, correct ?"


def random_answer():
    return random.choice(GENERAL_RESPONSES)

def check_for_greeting(sentence):
    return any(s in sentence for s in GREETING_SET)

def give_random_greeting():
    resp = random.choice(GREETING_RESPONSES)
    return resp

class NLP:
    def __init__(self):
        print("NLP class was created")
        self.city1 = None
        self.city2 = None
        self.many_cities = None
        self.origin = None
        self.blindshot = False
        self.tagger = StanfordNERTagger(STANFORD_ENG_FILE, STANFORD_JAR_FILE, encoding='utf-8')

    def introduction(self):
        return INTRODUCTION

    def check_for_cities(self, text):
        tokenized_text = word_tokenize(text)
        tagged_text = np.array(self.tagger.tag(tokenized_text))
        print ("tagged_text: {}".format(tagged_text))
        cities = tagged_text[tagged_text[:, 1] == 'LOCATION'][:, 0]
        if len(cities) == 0:
            return False
        elif len(cities) == 1:
            self.city1 = cities[0]
            return True
        elif len(cities) == 2:
            self.city1 = cities[0]
            self.city2 = cities[1]
            return True
        elif len(cities) > 2:
            self.many_cities = cities

    def found_1_city(self):
        return RESPONSE_FOUND_1_CITY.format(self.city1)

    def found_2_cities(self):
        return RESPONSE_FOUND_2_CITIES.format(self.city1, self.city2)

    def found_many_cities(self):
        response = "I detected: "
        for city in self.many_cities:
            response.append("{}, ".format(city))
        response.append(". Please decide for 2 cities")
        return response

    def respond(self, sentence):
        print('input message = {}'.format(sentence))
        resp = None
        if any(sentence in s for s in ("start", "\start")):
            return self.introduction();
        elif check_for_greeting(sentence):
            return give_random_greeting()
        elif self.check_for_cities(sentence):
            if self.many_cities: resp = self.found_many_cities()
            elif self.city1 and self.city2: resp = self.found_2_cities()
            elif self.city1: resp = self.found_1_city()
        else:
            resp = random_answer();
        return resp
