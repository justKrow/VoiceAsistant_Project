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
from signal import signal, SIGTERM, SIGHUP, pause
from rpi_lcd import LCD

lcd = LCD()
def safe_exit(signum, frame):
    exit(1)

signal(SIGTERM, safe_exit)
signal(SIGHUP, safe_exit)

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
    speak(time)


def date():
    year = int(datetime.datetime.now().year)
    month = int(datetime.datetime.now().month)
    date = int(datetime.datetime.now().day)
    speak(f"the current date is {date} {month} {year}")
    print(f"the current date is {date} {month} {year}")

def wishMe():
    hour = int(datetime.datetime.now().hour)
    if hour>= 0 and hour<12:
        speak("Good Morning Sir!") 
        print("Good Morning Sir!")
    elif hour>= 12 and hour<18:
        speak("Good Afternoon Sir!")    
        print("Good Afternoon Sir!") 
    else:
        speak("Good Evening Sir!")
        print("Good Evening Sir!")

def weather():
    myweather = Weather()
    forecast = myweather.forecast
    print(forecast)
    speak(forecast)


def joke():
    funny = pyjokes.get_joke()
    lcd.text(funny,1)
    print(funny)
    speak(funny)


def facts():
    fact = randfacts.get_fact()
    print(fact)
    speak(fact)


def takeCommand():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        lcd.clear()
        lcd.text("Listening....")
        print("Listening....")
        r.adjust_for_ambient_noise(source)
        r.pause_threshold = 1
        audio = r.listen(source, phrase_time_limit=5)
    try:
            lcd.clear()
            lcd.text("Recognising...")
            print("Recognising...")
            query = r.recognize_google(audio)
            print(f"You said: {query}")
            lcd.text(f"You said: {query}")
    except Exception as e:
        print(e)
        lcd.clear()
        print("Invalid Attempt")
        lcd.text("Invalid Attempt",1)

        return "None"
    return query


if __name__ == "__main__":

    wishMe()

    while True:
        WAKE = "google"
        query = takeCommand().lower()
        if query.count(WAKE) > 0:
            query = query.replace('google ', '')           
            if "tell me the time" in query:
                time()
            elif "what is the date" in query:
                date()
            elif "play" in query:
                song = query.replace('play ', '')
                speak('playing ' + song)
                pywhatkit.playonyt(song)
            elif 'close youtube' in query or 'turn off the music' in query:
                speak("closing youtube")
                os.system("TASKKILL /F /IM opera.exe")
            elif "search" in query:
                try:
                    query = query.replace("search ", "")
                    speak(f'searching {query}')
                    result = wikipedia.summary(query, sentences=2)
                    print(result)
                    speak(result)
                except:
                    print('sorry i could not find')
                    speak('sorry i could not find')
            elif "find" in query:
                client = wolframalpha.Client("LU8K3W-J4T4GPAQPK")
                res = client.query(query)
                try:
                    print(next(res.results).text)
                    speak(next(res.results).text)
                except StopIteration:
                    print("No results")
                    speak("No results")
            elif 'what is the weather like' in query or 'give me the forecast' in query or 'what is the weather' in query:
                try:
                    weather()
                except:
                    print("No results")
                    speak("No results")
            elif "offline" in query:
                speak("going offline")
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
                speak(message)
                weather()
            elif 'tell me a joke' in query or 'make me laugh' in query:
                joke()
            elif 'change language to english' in query:
                language = "en"
                print('changing language complete')
                speak('changing language complete')
            elif 'change language to myanmar' in query:
                language = "my"
                print('changing language complete')
                speak('changing language complete')
            elif 'change language to thai' in query:
                language = "th"
                print('changing language complete')
                speak('changing language complete')
            elif 'change language to korean' in query:
                language = "ko"
                print('changing language complete')
                speak('changing language complete')
            elif 'change language to japanese' in query:
                language = "ja"
                print('changing language complete')
                speak('changing language complete')
            elif 'change language to chinese' in query:
                language = "zh-CN"
                print('changing language complete')
                speak('changing language complete')
            elif 'tell me a fact' in query or 'tell me something' in query:
                facts()
            elif 'what is love' in query:
                speak("It is 7th sense that destroy all other senses")
            elif "calculate" in query:
                app_id = "LU8K3W-J4T4GPAQPK"
                client = wolframalpha.Client(app_id)
                indx = query.lower().split().index('calculate')
                query = query.split()[indx + 1:]
                res = client.query(' '.join(query))
                answer = next(res.results).text
                print("The answer is " + answer)
                speak("The answer is " + answer)
            elif "who made you" in query or "who created you" in query:
                print("I have been created by the group named raspbian from gusto.")
                speak("I have been created by the group named raspbian from gusto.")
            else:
                try:
                    message = query
                    ints = predict_class(message)
                    res = get_response(ints, intents)
                    print(res)
                    speak(res)
                except:
                    print('sorry i did not understand please try a different command')
                    speak('sorry i did not understand please try a different command')
