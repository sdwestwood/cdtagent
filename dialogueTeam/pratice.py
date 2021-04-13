# -*- coding: utf-8 -*-
# -*- coding: utf-8 -*-
"""
Created on Fri Feb 26 15:25:33 2021

@author: gordo
"""
import requests
import sys
import time
import json
import random 

CDT_responses = ["We're a groupd of students who work at the intersection of AI and society",
				 "It's a PHD program cross-discipline between computer science, psychology, neuroscience and a bunch of other things",
				 "It's a group of students that are researching future technologies"]

destinations = {
	"toilet": "the toilet is on the ground floor just next to the coffee stand behind me.",
	"office": "the office is on the second floor take a left when you get to the top of the stairs."
	}

students = {
	"gordon": "studies computational paralinguistics",
	"serena": "studying brains in VR"
	}


def generateDirections(destination):
	directions = ""
	try:
		place = destination[0]["value"]
		keys = destinations.keys()
		for key in keys:
			if key == place:
				directions = "I think you want to go to {DESTINATION}, {DIRECTIONS}".format(DESTINATION=place, DIRECTIONS=destinations[place])
		if directions == "":
			directions = "I'm sorry, I don't know where the {FUCKING_THING} is".format(FUCKING_THING=place)
			
	except:
		directions = "I'm not sure where you want to go. (give examples???)"
	
	return directions


def generateCDTtrivia(entities):
	response = "Hello world"
	#try:
	Type = entities[0]["entity"]
	if Type == "name":
		response = ""
		keys = students.keys()
		for key in keys:
			if entities[0]["value"] == key:
				name = entities[0]["value"]
				description = students[name]
				response = "{NAME}, is {DESC}".format(NAME=name, DESC=description)
	if response == "":
		response = "I'm sorry I don't know {NAME}, perhaps you could try rephrasing that".format(NAME=name)
	#except:
	#	response = random.choice(CDT_responses)
	return response


def getReply(utterance, sender):
	payload = {"text": utterance}
	content = requests.post(url='http://localhost:5005/model/parse', json=payload)
	dataReturned = content.json()
	entities = dataReturned["entities"]
	intent = dataReturned["intent"]["name"]
	
	"""
	Only use the below request if you want the actual reply that rasa gives
	payload = {"sender": sender, "message": utterance}
	response = requests.post(url='http://localhost:5005/webhooks/rest/webhook', json=payload)
	response = response.json()[0]["text"]
	"""
	
	if intent == "cdtTrivia":
		response = generateCDTtrivia(entities)
	elif intent == "directions":
		response = generateDirections(entities)
	return response

def runConversation():
	sender = input("What's your name? ")
	while True:
		utterance = input("What would you like to say? ")
		reply = getReply(utterance, sender)
		print(reply)
		#print(entities)



runConversation()