from nltk.tokenize import word_tokenize
from nltk import pos_tag
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from random import choice
import pyttsx3
import pickle
import socket
import sys
from _thread import *
from subprocess import call


stop_words = set(stopwords.words('english'))
lemmatizer = WordNetLemmatizer()
engine = pyttsx3.init() 


try:
    with open('devices.pkl','rb+') as file:
        devices = pickle.load(file)
except:
    devices = {
        "n_devices":0,#0 index for off, 1 index for on, 2 index for pin number
    }


def remove_stop_words(example_sent):
    word_tokens = word_tokenize(example_sent) 
    filtered_sentence = [w for w in word_tokens if not w in stop_words] 
    return filtered_sentence

def lemmatize_words(example_sent):
    word_tokens = word_tokenize(example_sent) 
    filtered_sentence = [lemmatizer.lemmatize(w) for w in word_tokens] 
    return filtered_sentence

def turn_on_off_device(sent):
    for key in devices.keys():
        if not set(str(key+' on').split()).issubset(set(sent)):
            pass
        else:
            if devices[key][1] is 1:
                return device_status_response(2,key)
            else:
                #code to turn on device
                devices[key][1] = 1
                with open('./devices.pkl','wb+') as file:
                    pickle.dump(devices,file)
                return device_status_response(0,key)
            break
    for key in devices.keys():
        if not set(str(key+' off').split()).issubset(set(sent)):
            pass
        else:
            if devices[key][1] is 0:
                return device_status_response(3,key)
            else:
                #code to turn off device
                devices[key][1] = 0
                with open('./devices.pkl','wb+') as file:
                    pickle.dump(devices,file)
                return device_status_response(0,key)
            break
    return "I couldn't understand. Can you please repeat what you said?"



def device_status_response(status_type,device_name=None):
    '''
    0 - turned on
    1 - turned off
    2 - already on
    3 - already 0ff
    4 - good night
    5 - bye
    '''
    if status_type == 0:
        return choice([f"Okay. {device_name} has been turned on",f"Alright! Turning on the {device_name}", f"{device_name} has been turned on sir"])
    elif status_type == 1:
        return choice([f"Okay. {device_name} has been turned off", " Alright! It has been turned off",f"{device_name} has been turned off sir"])
    elif status_type == 2:
        return choice([f"{device_name} is already on sir", "It is already on sir"])
    elif status_type == 3:
        return choice([f"{device_name} is already off sir", "It is already off sir"])
    elif status_type == 4:
        return choice(["Good night sir", "Sleep well sir", "See you tomorrow sir"])
    elif status_type == 5:
        return choice(["Good bye sir", "See you sir"])



# while True:
#     text = input('Enter a command- ')
#     sent = lemmatize_words(text)
#     print(turn_on_off_device(sent))
#     engine.say(turn_on_off_device(sent))
#     engine.runAndWait()
#     engine.stop()
#     break


# # In[5]:


def init_socket():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        s.bind((socket.gethostname(), 1234))
    except socket.error as e:
        print(str(e))

    s.listen(5)
    print('Waiting for a connection at ',end='')
    print(socket.gethostbyname(socket.gethostname()))
    return s


def threaded_client(conn):
    while True:
        try:
            data = conn.recv(1024)
            sent = lemmatize_words(str(data.decode()))
            reply = turn_on_off_device(sent)
            if not data:
                print(123)
                engine.stop()
                break
            
            conn.send(str.encode(reply))
            print("recieved",data)
            phrase = str(reply)
            call(["python", "speak.py", phrase])
            # engine.say(str(reply))
            # engine.runAndWait()
            # engine.stop()
            
            # engine.iterate()
        except Exception as e: print(e)

    conn.close()



s =  socket.socket(socket.AF_INET, socket.SOCK_STREAM)
port = 12345   
s.bind(('', port))
s.listen()
while True:
    conn, addr = s.accept()
    print('connected to: '+addr[0]+':'+str(addr[1]))
    conn.sendall("hi\n".encode('utf-8'))
    engine.say(str('connected to: '+addr[0]+':'+str(addr[1])))
    engine.runAndWait()
    start_new_thread(threaded_client,(conn,))

