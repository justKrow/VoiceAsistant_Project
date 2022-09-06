from keras.models import load_model
from nltk.stem import WordNetLemmatizer
import nltk
import random
import json
import googletrans
import wolframalpha
import os
import pickle
import numpy as np
import gtts
import playsound
import datetime
import pyjokes
from randfacts import randfacts
import pywhatkit
import wikipedia
from weatherTestAPI import Weather
import speech_recognition as sr
import drivers
from time import sleep

display = drivers.Lcd()
def long_string(display, text='', num_line=1, num_cols=16):
		if len(text) > num_cols:
			display.lcd_display_string(text[:num_cols], num_line)
			sleep(1)
			for i in range(len(text) - num_cols + 1):
				text_to_print = text[i:i+num_cols]
				display.lcd_display_string(text_to_print, num_line)
				sleep(0.2)
			sleep(1)
		else:
			display.lcd_display_string(text, num_line)


lemmatizer = WordNetLemmatizer()
intents = json.loads(open('intents.json').read())

words = pickle.load(open('words.pkl', 'rb'))
classes = pickle.load(open('classes.pkl', 'rb'))
model = load_model('chatbotModel.h5')


def clean_up_sentence(sentence):
    sentence_words = nltk.word_tokenize(sentence)
    sentence_words = [lemmatizer.lemmatize(word) for word in sentence_words]
    return sentence_words


def bag_of_words(sentence):
    sentence_words = clean_up_sentence(sentence)
    bag = [0] * len(words)
    for w in sentence_words:
        for i, word in enumerate(words):
            if word == w:
                bag[i] = 1
    return np.array(bag)


def predict_class(sentence):
    bow = bag_of_words(sentence)
    res = model.predict(np.array([bow]))[0]
    ERROR_THRESHOLD = 0.6
    results = [[i, r] for i, r in enumerate(res) if r > ERROR_THRESHOLD]

    results.sort(key=lambda x: x[1], reverse=True)
    return_list = []
    for r in results:
        return_list.append({'intents': classes[r[0]], 'probabily': str(r[1])})
    return return_list


def get_response(intents_list, intents_json):
    tag = intents_list[0]['intents']
    list_of_intents = intents_json['intents']
    for i in list_of_intents:
        if i['tag'] == tag:
            result = random.choice(i['responses'])
            break
    return result

language = "en"
def speak(audio):
    translator = googletrans.Translator()
    translated = translator.translate(text=audio, dest=language)
    converted_audio = gtts.gTTS(translated.text, lang=language)
    converted_audio.save('voice.mp3')
    playsound.playsound('voice.mp3')
    os.remove('voice.mp3')

def time():
    time = datetime.datetime.now().strftime("%H:%M:%S")
    print(time)
    display.lcd_clear()
    long_string(display,time,1)
    speak(time)


def date():
    year = int(datetime.datetime.now().year)
    month = int(datetime.datetime.now().month)
    date = int(datetime.datetime.now().day)
    display.lcd_clear()
    long_string(display,f"the current date is {date} {month} {year}",1)
    speak(f"the current date is {date} {month} {year}")
    print(f"the current date is {date} {month} {year}")

def wishMe():
    hour = int(datetime.datetime.now().hour)
    if hour>= 0 and hour<12:
        display.lcd_clear()
        speak("Good Morning Sir!") 
        long_string(display,"Good Morning Sir!",1)
        print("Good Morning Sir!") 
    elif hour>= 12 and hour<18:
        display.lcd_clear()
        speak("Good Afternoon Sir!")  
        long_string(display,"Good Afternoon Sir!",1)  
        print("Good Afternoon Sir!") 
    else:
        display.lcd_clear()
        speak("Good Evening Sir!")
        long_string(display,"Good Evening Sir!",1)
        print("Good Evening Sir!")

def weather():
    myweather = Weather()
    forecast = myweather.forecast
    display.lcd_clear()
    speak(forecast)
    print(forecast)

def weatherLCD():
    myweather = Weather()
    temperature = myweather.temperature
    humidity = myweather.humidity
    pressure = myweather.pressure
    status = myweather.status
    display.lcd_clear()
    display.lcd_display_string(temperature, 1)
    display.lcd_display_string(humidity, 2)
    display.lcd_clear()
    display.lcd_display_string(pressure, 1)
    display.lcd_display_string(status, 2)

def joke():
    funny = pyjokes.get_joke()
    display.lcd_clear()
    print(funny)
    speak(funny)
    long_string(display,funny,1)

def facts():
    fact = randfacts.get_fact()
    display.lcd_clear()
    print(fact)
    speak(fact)
    long_string(display,fact,1)


def takeCommand():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        print("Listening....")
        display.lcd_clear()
        long_string(display,"Listening....",1)
        r.adjust_for_ambient_noise(source)
        r.pause_threshold = 1
        audio = r.listen(source, phrase_time_limit=5)
    try:
            print("Recognising...")
            display.lcd_clear()
            long_string(display,"Recognising...",1)
            query = r.recognize_google(audio)
            print(f"You: {query}")
            long_string(display,f"You: {query}",1) 
    except Exception as e:
        display.lcd_clear()
        long_string(display,"Invalid Attempt",1)
        print("Invalid Attempt")
        print(e)

        return "None"
    return query


if __name__ == "__main__":

    wishMe()

    while True:
        WAKE = "amigo"
        query = takeCommand().lower()
        if query.count(WAKE) > 0:
            query = query.replace('amigo ', '')  
            display.lcd_clear()        
            if "tell me the time" in query:
                time()
            elif "what is the date" in query:
                date()
            elif "play" in query:
                song = query.replace('play ', '')
                display.lcd_clear()    
                speak('playing ' + song)
                long_string(display,'playing ' + song,1) 
                pywhatkit.playonyt(song)
            elif 'close youtube' in query or 'turn off the music' in query:
                display.lcd_clear()
                speak("closing youtube")
                long_string(display,"closing youtube",1)  
                os.system("kill -9 chromium.exe")
            elif "search" in query:
                try:
                    query = query.replace("search ", "")
                    display.lcd_clear() 
                    speak(f'searching {query}')
                    long_string(display,f'searching {query}',1) 
                    result = wikipedia.summary(query, sentences=2)
                    print(result)
                    display.lcd_clear() 
                    speak(result)
                    long_string(display,result,1) 
                except:
                    print('sorry i could not find')
                    display.lcd_clear()
                    speak('sorry i could not find')
                    long_string(display,'sorry i could not find',1)  
            elif "find" in query:
                client = wolframalpha.Client("LU8K3W-J4T4GPAQPK")
                res = client.query(query)
                try:
                    display.lcd_clear() 
                    print(next(res.results).text)
                    speak(next(res.results).text)
                    long_string(display,next(res.results).text,1) 
                except StopIteration:
                    print("No results")
                    display.lcd_clear()
                    speak("No results")
                    long_string(display,"No results",1)  
            elif 'what is the weather like' in query or 'give me the forecast' in query or 'what is the weather+' in query:
                try:
                    weather()
                    weatherLCD()
                except:
                    print("No results")
                    display.lcd_clear()
                    speak("No results")
                    long_string(display,"No results",1)  
            elif "offline" in query:
                display.lcd_clear()
                speak("going offline")
                long_string(display,"going offline",1)  
                quit()
            elif 'good morning' in query or 'good afternoon' in query or 'good evening' in query or 'good night' in query:
                now = datetime.datetime.now()
                hr = now.hour
                if hr <= 0 <= 12:
                    message = "Morning"
                if hr >= 12 <= 17:
                    message = "Afternoon"
                if hr >= 17 <= 21:
                    message = "Evening"
                if hr > 21:
                    message = "Night"

                message = "Good " + message
                display.lcd_clear()
                speak(message)
                long_string(display,message,1) 
                weather()
            elif 'tell me a joke' in query or 'make me laugh' in query:
                joke()
            elif 'change language to english' in query:
                language = "en"
                print('changing language complete')
                display.lcd_clear()
                long_string(display,'changing language complete',1) 
                speak('changing language complete')
            elif 'change language to myanmar' in query:
                language = "my"
                print('changing language complete')
                display.lcd_clear()
                long_string(display,'changing language complete',1) 
                speak('changing language complete')
            elif 'change language to thai' in query:
                language = "th"
                print('changing language complete')
                display.lcd_clear()
                long_string(display,'changing language complete',1) 
                speak('changing language complete')
            elif 'change language to korean' in query:
                language = "ko"
                print('changing language complete')
                display.lcd_clear()
                long_string(display,'changing language complete',1) 
                speak('changing language complete')
            elif 'change language to japanese' in query:
                language = "ja"
                print('changing language complete')
                display.lcd_clear()
                long_string(display,'changing language complete',1) 
                speak('changing language complete')
            elif 'change language to chinese' in query:
                language = "zh-CN"
                print('changing language complete')
                display.lcd_clear()
                long_string(display,'changing language complete',1) 
                speak('changing language complete')
            elif 'tell me a fact' in query or 'tell me something' in query:
                facts()
            elif 'what is love' in query:
                display.lcd_clear()
                long_string(display,"It is 7th sense that destroy all other senses",1) 
                speak("It is 7th sense that destroy all other senses")
            elif "calculate" in query:
                app_id = "LU8K3W-J4T4GPAQPK"
                client = wolframalpha.Client(app_id)
                indx = query.lower().split().index('calculate')
                query = query.split()[indx + 1:]
                res = client.query(' '.join(query))
                answer = next(res.results).text
                print("The answer is " + answer)
                display.lcd_clear()
                long_string(display,"The answer is " + answer,1) 
                speak("The answer is " + answer)
            elif "who made you" in query or "who created you" in query:
                print("I have been created by the group named raspbian from gusto.")
                display.lcd_clear()
                long_string(display,"I have been created by the group named raspbian from gusto.",1) 
                speak("I have been created by the group named raspbian from gusto.")
            else:
                try:
                    message = query
                    ints = predict_class(message)
                    res = get_response(ints, intents)
                    print(res)
                    display.lcd_clear()
                    long_string(display,res,1)
                    speak(res)
                except:
                    print('sorry i did not understand please try a different command')
                    display.lcd_clear()
                    speak('sorry i did not understand please try a different command')
                    long_string(display,'sorry i did not understand please try a different command',1)
