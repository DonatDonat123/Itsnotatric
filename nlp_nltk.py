import random
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

#import nltk
#nltk.download('popular')


def random_answer():
    GENERAL_RESPONSES = ("We will see", "Ok, but that's not really true", "You wanna think about it again ?",
                         "...Rom wasn't build in a day",
                         "I din't catch that to be honest", "That's interesting, but let's talk CITIES :)",
                         "Even a broken watch is two times right per day...")
    return random.choice(GENERAL_RESPONSES)


def check_for_greeting(sentence):
    GREETING_SET = (
        "hello", "hi", "yo", "how are you", "hi man", "hey", "what's up", "good morning", "good evening",
        "good afternoon")
    return any(sentence in s for s in GREETING_SET)


def give_random_greeting():
    GREETING_RESPONSES = (
        "hello back !", "hi, how are you ?", "What's up", "Nice to hear from you, how can I serve ?", "Good Day")
    resp = random.choice(GREETING_RESPONSES)
    return resp


class NLP:
    def __init__(self, city1, city2, origin, blindshot, docity1, docity12, askorigin, bydistance, askdist):
        print("NLP class was created")
        self.city1 = city1
        self.city2 = city2
        self.origin = origin
        self.blindshot = blindshot
        self.docity1 = docity1
        self.docity12 = docity12
        self.askorigin = askorigin
        self.bydistance = bydistance  # by default we take weather as important parameter
        self.askdist = askdist

    def introduction(self):
        resp = "Hello. I am LASTMINUTE-HELPER. If you want to go for a city trip and you haven't decided yet where to,\
    then I'm your man...amm bot. I can help you to decide between 2 cities, give you more information about 1 city or even \
    give you my personal suggestion of the day if you don't have any plan. But first things first: What's your origin ?"
        self.askorigin = True
        print('set askorigin to true, right ? ')
        print(self.askorigin)
        return resp

    # That's the main function that returns our response
    def respond(self, sentence):
        print('input message = {}'.format(sentence))
        resp = None
        if any(sentence in s for s in ("start", "\start")):
            resp = self.introduction();
        elif check_for_greeting(sentence):
            resp = give_random_greeting()
        else:
            resp = random_answer();

        return resp, self.city1, self.city2, self.origin, self.blindshot, self.docity1, self.docity12, self.askorigin, self.bydistance, self.askdist
