import speech_recognition as sr

r = sr.Recognizer()
mic = sr.Microphone()

with mic as source:
    r.adjust_for_ambient_noise(source, duration = 0.5)
    audio = r.listen(source,)
# print(r.recognize_google(audio))
# print(r.recognize_google(audio, show_all = True))

Output = r.recognize_google(audio)
Speech = r.recognize_google(audio, show_all = True)
Conf = Speech['alternative'][0]['confidence']
print(Conf)

if Conf > 0.8:
    print(Speech['alternative'][0]['transcript'])
else:
    print("Sorry, could you repeat that?")
print()    
# print (Output)




