get_ipython().system('pip install sounddevice==0.4.7')
get_ipython().system('pip install scipy==1.7.3')
get_ipython().system('pip install wavio==0.0.9')
get_ipython().system('pip install SpeechRecognition==3.9.0')
get_ipython().system('pip install simpleaudio==1.0.4')
get_ipython().system('pip install requests==2.31.0')
import simpleaudio as sa
import sounddevice as sd
from scipy.io.wavfile import write
import wavio as wv
import speech_recognition as sr
import webbrowser
hi = (["Привет","привет","Добрый вечер","Доброе утро","Доброй ночи","Здорово","Здарова","Здравстуй","Здравствуйте","Привет Джарвис","Джарвис Привет","Добрый вечер Джарвис","Доброе утро Джарвис","Доброй ночи Джарвис","Здорово Джарвис","Здарова Джарвис","Здравстуй Джарвис","Здравствуйте Джарвис"])
text = "пусто"
bt_st = False
st_st = False
poka = False
def voice():
    global poka
    if text in hi:
        zvuk = 'hi.wav'
        wave_obj = sa.WaveObject.from_wave_file(zvuk)
        play = wave_obj.play()
        play.wait_done()
        play.stop()
        pusk()
    elif "погода " in text:
        zvuk = 'open.wav'
        wave_obj = sa.WaveObject.from_wave_file(zvuk)
        play = wave_obj.play()
        play.wait_done()
        play.stop()
        pogoda_fact, city = text.split('погода ')
        webbrowser.open('https://yandex.ru/pogoda/search?request=' +city)
    elif "поиск" in text:
        zvuk = 'poisk.wav'
        wave_obj = sa.WaveObject.from_wave_file(zvuk)
        play = wave_obj.play()
        play.wait_done()
        play.stop()
        poisk_fact, poisk = text.split('поиск ')
        webbrowser.open('https://yandex.ru/search/?text=' +poisk)
    elif "Найди" in text:
        zvuk = 'poisk.wav'
        wave_obj = sa.WaveObject.from_wave_file(zvuk)
        play = wave_obj.play()
        play.wait_done()
        play.stop()
        poisk_fact, poisk = text.split('Найди ')
        webbrowser.open('https://yandex.ru/search/?text=' +poisk)
    elif "найти" in text:
        zvuk = 'poisk.wav'
        wave_obj = sa.WaveObject.from_wave_file(zvuk)
        play = wave_obj.play()
        play.wait_done()
        play.stop()
        poisk_fakt, poisk = text.split('найти ')
        webbrowser.open('https://yandex.ru/search/?text=' +poisk)
    elif "Включи " in text:
        zvuk = 'on.wav'
        wave_obj = sa.WaveObject.from_wave_file(zvuk)
        play = wave_obj.play()
        play.wait_done()
        play.stop()
        music_fact, music = text.split('Включи ')
        webbrowser.open('https://music.yandex.ru/search?text=' + music)
    elif "Включи песню" in text:
        zvuk = 'on.wav'
        wave_obj = sa.WaveObject.from_wave_file(zvuk)
        play = wave_obj.play()
        play.wait_done()
        play.stop()
        music_fact, music = text.split('Включи песню ')
        webbrowser.open('https://music.yandex.ru/search?text=' + music)
    elif "песня" in text:
        zvuk = 'on.wav'
        wave_obj = sa.WaveObject.from_wave_file(zvuk)
        play = wave_obj.play()
        play.wait_done()
        play.stop()
        music_fact, music = text.split('песня ')
        webbrowser.open('https://music.yandex.ru/search?text=' + music)
    elif "что выгоднее" in text:
        vvod_sravneniya = text
        sravneniye_fact, vvod_sravneniya = vvod_sravneniya.split('что выгоднее ')
        tovar1, tovar2 = vvod_sravneniya.split(' или ')
        t1t, t1p = tovar1.split(' за ')
        t2t, t2p = tovar2.split(' за ')
        t1t = int(t1t)
        t1p = int(t1p)
        t2t = int(t2t)
        t2p = int(t2p)
        t1result = t1p / t1t
        t2result = t2p / t2t
        if t1result < t2result:
            zvuk = 'perviy.wav'
            wave_obj = sa.WaveObject.from_wave_file(zvuk)
            play = wave_obj.play()
            play.wait_done()
            play.stop()
        elif t1result > t2result:
            zvuk = 'vtoroy.wav'
            wave_obj = sa.WaveObject.from_wave_file(zvuk)
            play = wave_obj.play()
            play.wait_done()
            play.stop()
        elif t1result == t2result:
            zvuk = 'ravni.wav'
            wave_obj = sa.WaveObject.from_wave_file(zvuk)
            play = wave_obj.play()
            play.wait_done()
            play.stop()
    elif text == "отмена":
        zvuk = 'ponial.wav'
        wave_obj = sa.WaveObject.from_wave_file(zvuk)
        play = wave_obj.play()
        play.wait_done()
        play.stop()
    elif "пока" in text:
        zvuk = 'godbie.wav'
        wave_obj = sa.WaveObject.from_wave_file(zvuk)
        play = wave_obj.play()
        play.wait_done()
        play.stop()
        poka = True
    else:
        zvuk = 'neponial.wav'
        wave_obj = sa.WaveObject.from_wave_file(zvuk)
        play = wave_obj.play()
        play.wait_done()
        play.stop()
        pusk()
def pusk():
    global text
    text = "пусто"
    slushayu_name = 'slushayu.wav'
    wave_obj = sa.WaveObject.from_wave_file(slushayu_name)
    play = wave_obj.play()
    play.wait_done()
    play.stop()
    recording = sd.rec(int(5 * 44100), samplerate=44100, channels=2)
    sd.wait(2)
    write("recording.wav", 44100, recording)
    wv.write("recording.wav", recording, 44100, sampwidth=2)
    r = sr.Recognizer()
    with sr.AudioFile("recording.wav") as source:
        audio = r.record(source)
    try:
        text = r.recognize_google(audio, language="ru-RU")
        print("Text: "+text)
    except Exception as e:
        print("Exception: "+str(e))
    voice()
def potok():
    global text
    global st_st
    global poka
    while text != "пока" and st_st == True:
        recording = sd.rec(int(5 * 44100), samplerate=44100, channels=2)
        sd.wait(0.7)
        write("recording.wav", 44100, recording)
        wv.write("recording.wav", recording, 44100, sampwidth=2)
        r = sr.Recognizer()
        with sr.AudioFile("recording.wav") as source:
            audio = r.record(source)
        try:
            text = r.recognize_google(audio, language="ru-RU")
            print("Text: "+text)
        except Exception as e:
            print("Exception: "+str(e))
        if text == "Джарвис" or text == "Джар" or text == "джар":
            text = "пусто"
            pusk()
            if poka == True:
                poka = False
                continue
            else:
                potok()
        else:
            text = "пусто"
            potok()
def status():
    global bt_st
    global st_st
    if bt_st == False:
        bt_st = True
        st_st = True
        potok()
        st_st = False
    else:
        bt_st = False
        st_st = True
        potok()