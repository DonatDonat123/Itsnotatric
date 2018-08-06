from __future__ import print_function, unicode_literals
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

os.environ['NLTK_DATA'] = os.getcwd() + '/nltk_data'

from config import FILTER_WORDS
# Set up spaCy
#from spacy.lang.en import English
import en_core_web_sm as eng
parser = eng.load()
#parser = English()

logging.basicConfig()
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

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

	def random_answer(self):
		GENERAL_RESPONSES = ("We will see", "Ok, but that's not really true", "You wanna think about it again ?",
							 "...Rom wasn't build in a day",
							 "I din't catch that to be honest", "That's interesting, but let's talk CITIES :)",
							 "Even a broken watch is two times right per day...")
		return random.choice(GENERAL_RESPONSES)

	def check_for_greeting(self, sentence):
		phrase = ''.join(token.string for token in sentence)
		GREETING_SET = (
			"hello", "hi", "yo", "how are you", "hi man", "hey", "what's up", "good morning", "good evening",
			"good afternoon")
		GREETING_RESPONSES = (
			"hello back !", "hi, how are you ?", "What's up", "Nice to hear from you, how can I serve ?", "Good Day")
		print("checking for greating")
		resp = None
		if any(phrase in s for s in GREETING_SET):
			resp = random.choice(GREETING_RESPONSES)
		if not resp:
			for word in sentence:
				if word.lower_ in GREETING_SET:
					resp = random.choice(GREETING_RESPONSES)
		return resp

	def check_for_geo_keywords(self, sent):
		blindshot = False
		city1 = False
		city2 = False
		for token in sent:
			print(token.orth_, token.ent_type_)
			if token.ent_type_ == 'GPE':  # This is a verb
				if not city1: city1 = token.orth_
				if (token.orth_ != city1):
					city2 = token.orth_
					break
		if not city1:
			KEY_WORDS = (
				"where", "holidays", "holiday", "place", "sunny", "city", "town", "country", "destination", "warm",
				"nice", "sun", "beach", "sea", "ocean")
			for word in sent:
				if word.lower_ in KEY_WORDS: blindshot = True
		else:
			blindshot = False
		return city1, city2, blindshot

	def dback(self, sentence):
		logger.info("Dback: respond to %s", sentence)
		resp = self.respond(sentence)
		return resp

	def preprocess_text(self, sentence):
		"""Handle some weird edge cases in parsing, like 'i' needing to be capitalized
		to be correctly identified as a pronoun"""
		cleaned = []
		words = sentence.split(' ')
		for w in words:
			if w == 'i':
				w = 'I'
		if w == "i'm":
			w = "I'm"
		if w == "cya":
			w = "See you"
		cleaned.append(w)

		return ' '.join(cleaned)

	def find_pronoun(self, sent):
		"""Given a sentence, find a preferred pronoun to respond with. Returns None if no candidate
		pronoun is found in the input"""
		pronoun = None
		print("FIND_PRONOUN...")
		for token in sent:
			# Disambiguate pronouns
			if token.pos_ == 'PRON' and token.lower_ == 'you':
				pronoun = 'I'
			elif token.pos_ == 'PRON' and token.orth_ == 'I':
				# If the user mentioned themselves, then they will definitely be the pronoun
				pronoun = 'You'
			elif token.pos_ == 'PRON':
				pronoun = token.orth_
		return pronoun

	# end

	def find_verb(self, sent):
		# Pick a candidate verb for the sentence
		verb = None
		for token in sent:
			if token.pos_ == 'VERB':  # This is a verb
				verb = token.lemma_
		return verb

	def find_noun(self, sent):
		# Given a sentence, find the best candidate noun
		noun = None

		if not noun:
			for token in sent:
				if token.pos_ == 'NOUN':  # This is a noun
					noun = token.orth_
					break
		if noun:
			logger.info("Found noun: %s", noun)

		return noun

	def find_adjective(self, sent):
		"""Given a sentence, find the best candidate adjective."""
		adj = None
		for token in sent:
			if token.pos_ == 'ADJ':  # This is an adjective
				adj = token.orth_
				break
		return adj

	def comments_about_bot(self, pronoun, adjective):
		# if the input uses "YOU" than he talks about the bot.
		if (pronoun == "I" and adjective):
			resp = "I am indeed {adjective}".format(**{'adjective': adjective})
			return resp

	def comments_about_self(self, pronoun, adjective):
		# if the input uses "YOU" than he talks about the bot.
		if (pronoun == "You" and adjective):
			resp = "You aren't really {adjective}".format(**{'adjective': adjective})
			return resp

	def ask2cities(self, city1, city2):
		# if the input uses "YOU" than he talks about the bot.
		resp = "So you want to compare {city1} with {city2}.".format(**{'city1': city1, 'city2': city2})
		resp += " Do you want to decide by distance (how long it takes you), or by weather ?"
		self.askdist = True
		self.docity12 = True
		return resp

	def ask1city(self, city1):
		# if the input uses "YOU" than he talks about the bot.
		resp = "So you want to know more about {city1}, let me see what I can do.".format(**{'city1': city1})
		self.docity1 = True
		return resp

	def askblindshot(self):
		# if the input uses "YOU" than he talks about the bot.
		resp = "Then I give my personal suggestion, let's see..."
		self.blindshot = True
		return resp

	def give2cities(self, city1, city2, bydistance, origin):
		# Will it be sunny tomorrow at this time in Milan (Italy) ?
		if (bydistance):
			now = datetime.now()
			print ('origin: {}, city1: {} city2: {}'.format(self.origin, self.city1, self.city2))
			duration_now1 = client.distance_matrix(origin, city1, mode="driving")
			#, language="en-AU", units="imperial", departure_time=now, traffic_model="optimistic")
			duration_now2 = client.distance_matrix(origin, city2, mode="driving", language="en-AU", units="imperial",
												   departure_time=now, traffic_model="optimistic")
			print ('duration_now1:')
			print (duration_now1)

			zeit1 = duration_now1['rows'][0]['elements'][0]['duration']['text']
			zeit2 = duration_now2['rows'][0]['elements'][0]['duration']['text']
			resp = "It takes {zeit1} to {city1}, and {zeit2} to {city2}".format(
				**{'zeit1': zeit1, 'zeit2': zeit2, 'city1': city1, 'city2': city2})
		else:
			fc1 = owm.daily_forecast(city1)
			fc2 = owm.daily_forecast(city2)
			tomorrow = pyowm.timeutils.tomorrow()
			sunny1 = fc1.will_be_sunny_at(tomorrow)
			sunny2 = fc2.will_be_sunny_at(tomorrow)
			weather1 = fc1.get_weather_at(tomorrow)
			weather2 = fc2.get_weather_at(tomorrow)
			temp1 = weather1.get_temperature(unit='celsius')["day"]
			temp2 = weather2.get_temperature(unit='celsius')["day"]
			if sunny1 and sunny2:
				if temp1 > temp2:
					temp_max = temp1;
					city_max = city1
				else:
					temp_max = temp2;
					city_max = city2
				resp = "Well, it's gonna be sunny in both places, but it will be warmer in {} ({}C) !".format(city_max, temp_max)
			elif sunny1 and not sunny2:
				city_sun = city1
			elif sunny2 and not sunny1:
				city_sun = city2
			if city_sun:
				if temp1 > temp2:
					city_max = city1
				else:
					city_max = city2
				resp = "Hmm, difficult choice: In {} it will be sunny and in {} it will be warmer, you decide ...".format(city_sun, city_max)
			else: resp = "Better stay at home, it's going to be rainy anyways in both places"
		self.city1 = None
		self.city2 = None
		self.directions = True
		return resp

	def give1city(self, city1):
		fc = owm.daily_forecast(city1)
		tomorrow = pyowm.timeutils.tomorrow()
		sunny = fc.will_be_sunny_at(tomorrow)
		weather = fc.get_weather_at(tomorrow)
		temp = weather.get_temperature(unit='celsius')["day"]
		status = weather.get_status()
		resp = "in {} it will be {} tomorrow and {} degree.".format(city1, status, temp)
		if sunny: resp += " At least you can catch some sun, right ?"
		self.city1 = None
		return resp

	def giveblindshot(self):
		# if the input uses "YOU" than he talks about the bot.
		CITIES = ("Barcelona", "Madrid", "Rome", "Granada, Spain", "Florence", "Lisbon")
		city = random.choice(CITIES)
		fc = owm.daily_forecast(city)
		tomorrow = pyowm.timeutils.tomorrow()
		sunny = fc.will_be_sunny_at(tomorrow)
		weather = fc.get_weather_at(tomorrow)
		temp = weather.get_temperature(unit='celsius')["day"]
		status = weather.get_status()
		resp = "Why don't you try {city}. It will be {} tomorrow and {} degree. Vamos :) ".format(city, status, temp)
		self.blindshot = None
		return resp

	def introduction(self):
		resp = "Hello. I am LASTMINUTE-HELPER. If you want to go for a city trip and you haven't decided yet where to,\
then I'm your man...amm bot. I can help you to decide between 2 cities, give you more information about 1 city or even \
give you my personal suggestion of the day if you don't have any plan. But first things first: What's your origin ?"
		self.askorigin = True
		print ('set askorigin to true, right ? ')
		print (self.askorigin)
		return resp

	def set_origin(self, sent):
		for token in sent:
			print ("Token.orth_ and token.ent_type_")
			print (token.orth_, token.ent_type_)
			if token.ent_type_ == 'GPE':
				self.origin = token.orth_
				break
		if self.origin:
			resp = "your origin is now set to {origin}, What can I do for you now ?".format(**{'origin': self.origin})
			self.askorigin = False
		else:
			resp = "Sorry, I don't know that city, let's try again with something more known"
		return resp

	# That's the main function that returns our response
	def respond(self, sentence):
		print ('input message = {}'.format(sentence))
		"""Parse the user's inbound sentence and find candidate terms that make up a best-fit response"""
		parsed = parser(sentence)
		resp = None
		phrase = ''.join(token.lower_ for token in parsed)
		print("askorigin = ");
		print(self.askorigin)
		print("askdist = ");
		print(self.askdist)
		print('docity12');
		print(self.docity12)
		print('docity1');
		print(self.docity1)
		if self.askorigin:
			resp = self.set_origin(parsed)
		elif self.askdist:
			if any(phrase in s for s in ("distance", "dist", "time")):
				self.bydistance = True; self.askdist = False
			elif any(phrase in s for s in ("weather", "clima", "climate")):
				self.bydistance = False; self.askdist = False
			else:
				resp = "I didn't get that. Again: By weather or distance ?"
		if any(phrase in s for s in ("start", "\start")):
			resp = self.introduction(); print("Intro2");
		elif self.docity12 and not resp:
			print("DOCTIY12")
			resp = self.give2cities(self.city1, self.city2, self.bydistance, self.origin)
			self.docity12 = False
		elif self.docity1 and not resp:
			resp = self.give1city(self.city1)
			self.docity1 = False
		elif self.blindshot and not resp:
			resp = self.giveblindshot()
		if not resp:
			resp = self.check_for_greeting(parsed)
		if not resp:
			(self.city1, self.city2, self.blindshot) = self.check_for_geo_keywords(parsed)
			print ('Checked for GeoKeywords, city1, city2, blindshot:')
			print (self.city1, self.city2, self.blindshot)
			if (self.city1 and self.city2):
				resp = self.ask2cities(self.city1, self.city2)
			elif self.city1:
				resp = self.ask1city(self.city1);
			elif self.blindshot:
				resp = self.askblindshot()
		if not resp:
			(pronoun, noun, adjective, verb) = self.find_candidate_parts_of_speech(parsed)
			resp = self.comments_about_bot(pronoun, adjective)
			if not resp: resp = self.comments_about_self(pronoun, adjective)
		if not resp:

			if (verb or (noun and verb)):
				resp = []
				if (noun):
					resp.append(noun)
				if (verb):
					resp.append(verb + "ing" + " is a dangerous game mon frere")
				return " ".join(resp)
		if not resp:
			resp = self.random_answer()
		print ('resp = {}'.format(resp))
		return resp, self.city1, self.city2, self.origin, self.blindshot, self.docity1, self.docity12, self.askorigin, self.bydistance, self.askdist

	def find_candidate_parts_of_speech(self, parsed):
		# Given a parsed input, find the best pronoun, direct noun, adjective, and verb to match their input.
		# Returns a tuple of pronoun, noun, adjective, verb any of which may be None if there was no good match"""
		pronoun = None
		noun = None
		adjective = None
		verb = None
		print(parsed.sents)
		for sent in parsed.sents:
			print(sent)
			pronoun = self.find_pronoun(sent)
			noun = self.find_noun(sent)
			adjective = self.find_adjective(sent)
			verb = self.find_verb(sent)
		logger.info("Pronoun=%s, noun=%s, adjective=%s, verb=%s", pronoun, noun, adjective, verb)
		return pronoun, noun, adjective, verb


def main():
	import sys
	nlp = NLP()
	# Usage:
	# python Dbot.py "hello"
	if (len(sys.argv) > 0):
		saying = sys.argv[1]
	else:
		saying = "How are you, brobot?"
	print(nlp.dback(saying))

if __name__ == '__main__':
	#main()
	print("HAAALOO")
