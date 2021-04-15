#!/usr/bin/env python3

import argparse
import os
import queue
import sounddevice as sd
import vosk
import sys
import re
import requests
import time
import json
import random 


CDT_responses = {
	"one": ["We're a groupd of students who work at the intersection of AI and society", ["Talking2", "HeadNodLong", "Idle"]],
	 "Two": ["It's a PHD program cross-discipline between computer science, psychology, neuroscience and a bunch of other things", ["Talking2", "HeadNodLong", "Idle"]],
	 "Three":["It's a group of students that are researching future technologies", ["Talking2", "HeadNodLong", "Idle"]]
	 }

destinations = {
	"toilet": ["the toilet is on the ground floor just next to the coffee stand behind me.", ["HeadNodYes", "PointUp", "Talking"]],
	"office": ["the office is on the second floor take a left when you get to the top of the stairs.", ["HeadNodYes", "PointUp", "PointLeft"]]
	}

students = {
	"gordon": ["studying computational paralinguistics", ["Talking1", "HeadNodLong"]],
	"serena": ["studying brains in VR", ["Talking2", "HeadNodLong", "Idle"]]
	}

unsure = ["Idle", "Talking1", "Talking 2"]

def generateDirections(destination):
	directions = ""
	try:
		place = destination[0]["value"]
		keys = destinations.keys()
		for key in keys:
			if key == place:
				directions = "I think you want to go to {DESTINATION}, {DIRECTIONS}".format(DESTINATION=place, DIRECTIONS=destinations[place][0])
				behaviour = destinations[place][1]
				payload = [directions, behaviour]
		if directions == "":
			directions = "I'm sorry, I don't know where the {FUCKING_THING} is".format(FUCKING_THING=place)
			behaviour = unsure
			payload = [directions, behaviour]
	except:
		directions = "I'm not sure where you want to go."
		behaviour = unsure
		payload = [directions, behaviour]
	
	return payload


def generateCDTtrivia(entities):
	response = "Hello world"
	try:
		Type = entities[0]["entity"]
		name = entities[0]["value"]
	except:
		name = "who you are asking about"
		Type = ""
	if Type == "name":
		response = ""
		keys = students.keys()
		for key in keys:
			if entities[0]["value"] == key:
				
				description = students[name]
				response = "{NAME}, is {DESC}".format(NAME=name, DESC=description[0])
				behaviour = description[1]
				payload = [response, behaviour]
	if response == "":
		response = "I'm sorry I don't know {NAME}, perhaps you could try rephrasing that".format(NAME=name)
		behaviour = unsure
		payload = [response, behaviour]
	#except:
	#	response = random.choice(CDT_responses)
	return payload


def getReply(utterance, sender):
	response = ""
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
	elif response == "":
		payload = {"sender": sender, "message": utterance}
		response = requests.post(url='http://localhost:5005/webhooks/rest/webhook', json=payload)
		response = response.json()[0]["text"]
		behaviour = ["Talking1", "Talking2", "Idle"]
		response = [response, behaviour]
	return response


q = queue.Queue()

def int_or_str(text):
    """Helper function for argument parsing."""
    try:
        return int(text)
    except ValueError:
        return text

def callback(indata, frames, time, status):
    """This is called (from a separate thread) for each audio block."""
    if status:
        print(status, file=sys.stderr)
    q.put(bytes(indata))
    
def getChunk(fulltxt):
    """Function to return the isolated chunk of text from rec.Result()"""
    result, text = fulltxt.split(']')
    chunk = text[14:-3]
    return chunk

def getConf(fulltxt):
    conf_idx = [a.end() for a in re.finditer('f" : ', fulltxt)]
    conf = [fulltxt[i:(i+6)] for i in conf_idx]
    return conf

parser = argparse.ArgumentParser(add_help=False)
parser.add_argument(
    '-l', '--list-devices', action='store_true',
    help='show list of audio devices and exit')
args, remaining = parser.parse_known_args()
if args.list_devices:
    print(sd.query_devices())
    parser.exit(0)
parser = argparse.ArgumentParser(
    description=__doc__,
    formatter_class=argparse.RawDescriptionHelpFormatter,
    parents=[parser])
parser.add_argument(
    '-f', '--filename', type=str, metavar='FILENAME',
    help='audio file to store recording to')
parser.add_argument(
    '-m', '--model', type=str, metavar='MODEL_PATH',
    help='Path to the model')
parser.add_argument(
    '-d', '--device', type=int_or_str,
    help='input device (numeric ID or substring)')
parser.add_argument(
    '-r', '--samplerate', type=int, help='sampling rate')
args = parser.parse_args(remaining)


try:
    if args.model is None:
        args.model = "model"
    if not os.path.exists(args.model):
        print ("Please download a model for your language from https://alphacephei.com/vosk/models")
        print ("and unpack as 'model' in the current folder.")
        parser.exit(0)
    if args.samplerate is None:
        device_info = sd.query_devices(args.device, 'input')
        # soundfile expects an int, sounddevice provides a float:
        args.samplerate = int(device_info['default_samplerate'])

    model = vosk.Model(args.model)

    if args.filename:
        dump_fn = open(args.filename, "wb")
    else:
        dump_fn = None

    with sd.RawInputStream(samplerate=args.samplerate, blocksize = 8000, device=args.device, dtype='int16',
                            channels=1, callback=callback):
            print('#' * 80)
            print('Press Ctrl+C to stop the recording')
            print('#' * 80)

            rec = vosk.KaldiRecognizer(model, args.samplerate)
            
            chunks = [];
            conf = [];
            while True:
                data = q.get()
                if rec.AcceptWaveform(data):
                    sender = ""
                    fulltxt = rec.Result()
                    tmp_chunk = getChunk(fulltxt)
                    tmp_conf = getConf(fulltxt)
                    tmp_dict = {tmp_chunk: tmp_conf}
                    reply = getReply(tmp_chunk, sender)
                    chunks.append(tmp_chunk)
                    conf.append(tmp_conf)

                    print(fulltxt)         

                    print(fulltxt)     
                    print(reply)

                    
                else:
                    pass
                if dump_fn is not None:
                    dump_fn.write(data)
                    
    
except KeyboardInterrupt:
    print('\nDone')
    parser.exit(0)
except Exception as e:
    parser.exit(type(e).__name__ + ': ' + str(e))
