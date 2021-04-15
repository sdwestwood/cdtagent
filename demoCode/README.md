Start up

navigate to this directory in terminal and run
rasa run --enable-api

Then new terminal navigate to:
cdtagent\demoCode\vosk-api\python\example
and run
cdt_mic.py

This will start listening to your mic stream. Anything you say will then be sent to RASA.
Replies are now the actual strings, tagged with behaviours.

Things to say:
Tell me about Gordon
Hello
Where is the toilet
Where is the train station (will return a 'i don't know' statement)
