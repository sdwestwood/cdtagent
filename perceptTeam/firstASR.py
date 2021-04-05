import speech_recognition as sr
import pyaudio
import pocketsphinx

r = sr.Recognizer()
mic = sr.Microphone()

with mic as source:
    r.adjust_for_ambient_noise(source, duration = 0.5)
    audio = r.listen(source,)

Output = r.recognize_sphinx(audio)
Speech = r.recognize_sphinx(audio, show_all = True)
print(Output)
#Conf = Speech['alternative'][0]['confidence']
#print(Conf)

#if Conf > 0.8:
#    print(Speech['alternative'][0]['transcript'])
#else:
#    print("Sorry, could you repeat that?")






