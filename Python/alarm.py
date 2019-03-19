# ------------------------------------------------------------------------------$
# MICHAŁ RAFAŁOWSKI
# ZDALNY ALARM OPARTY NA RASPBERRY PI 3B+
# ------------------------------------------------------------------------------$


# ------------------------------------------------------------------------------$
# IMPORT POTRZEBNYCH BIBLIOTEK / WYŁĄCZENIE BŁĘDÓW / PRZYGOTOWANIE APLIKACJI
# ------------------------------------------------------------------------------$

from flask import *
import RPi.GPIO as GPIO
import os
from time import *
from functools import wraps
from datetime import *
import threading

app = Flask(__name__)
GPIO.setwarnings(False)
app.secret_key = 'losoweznaki'

# ------------------------------------------------------------------------------$
# DEKLARACJA PINÓW I ZMIENNEJ "state"
# ------------------------------------------------------------------------------$

global state
state = False  # False = rozbrojony / True = uzbrojony

sensor = 17
blue = 4
red = 2
buzz = 21

# ------------------------------------------------------------------------------$
# USTAWIENIE KIERUNKÓW PORTÓW ORAZ SPOSOBU NUMERACJI PINÓW
# ------------------------------------------------------------------------------$

GPIO.setmode(GPIO.BCM)
GPIO.setup(sensor, GPIO.IN)
GPIO.setup(blue, GPIO.OUT)
GPIO.setup(red, GPIO.OUT)
GPIO.setup(buzz, GPIO.OUT)


# ------------------------------------------------------------------------------$
# DEKORATOR LOGOWANIA
# ------------------------------------------------------------------------------$

def check(function):
    @wraps(function)
    def deco(*args, **kwargs):
        if 'logged_in' in session:                # Jeśli użytkownik jest zalogowany
            return function(*args, **kwargs)      # zwróć następną funkcję
        else:
            return render_template('login.html')  # albo zwróć ekran logowania

    return deco


# ------------------------------------------------------------------------------$
# FUNKCJA ODPOWIEDZIALNA ZA ARCHIWIZACJĘ STANÓW SYSTEMU
# ------------------------------------------------------------------------------$

def write(file):
    now = datetime.today()

    d = now.strftime("%d")
    m = now.strftime("%m")
    y = now.strftime("%Y")
    t = now.strftime("%X")

    msg = d + "/" + m + "/" + y + " | " + t + "\n"

    f = open(file, "a")
    f.write(msg)
    f.close()


# ------------------------------------------------------------------------------$
# GŁÓWNY ALGORYTM
# ------------------------------------------------------------------------------$

def alert():
    #   wyłączenie detekcji
    GPIO.remove_event_detect(sensor)

    #   niebieski LED wyłączony / Czerwony LED włączony / Brzęczyk włączony
    GPIO.output(blue, 0)
    GPIO.output(red, 1)
    GPIO.output(buzz, 1)

    #   wysłanie wiadomości o alarmie + archiwizacja
    os.system("curl https://notify.run/NhdTZ0gAJ1nW3IiD -d 'WYKRYTO RUCH'")
    write("detect.txt")

    #   czekanie 60 sekund na reakcje (rozbrojenie)
    for i in range(60):
        sleep(1)
        if state == False:
            return

    #   wysłanie wiadomości o wznowieniu + archiwizacja
    os.system("curl https://notify.run/NhdTZ0gAJ1nW3IiD -d 'WZNOWIONO PRACĘ'")
    write("continue.txt")

    #   niebieski LED włączony / Czerwony LED wyłączony / Brzęczyk wyyłączony
    GPIO.output(blue, 1)
    GPIO.output(red, 0)
    GPIO.output(buzz, 0)

    #   ponowne uruchomienie detekcji
    GPIO.add_event_detect(sensor, GPIO.RISING, callback=trigger)


def trigger(sensor):
    threading.Thread(target=alert).start()


# ------------------------------------------------------------------------------$
# ŚCIEŻKA ODPOWIADAJĄCA ZA LOGOWANIE
# ------------------------------------------------------------------------------$

@app.route('/LOGIN', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        if request.form['password'] != '1994':
            return render_template('login.html')
        else:
            session['logged_in'] = True
            return render_template('home.html')


# ------------------------------------------------------------------------------$
# ŚCIEŻKA ODPOWIADAJĄCA ZA STRONĘ TYTUŁOWĄ
# ------------------------------------------------------------------------------$

@app.route('/')
@check
def main():
    GPIO.remove_event_detect(sensor)
    if state == False:
        return render_template('home.html')
    else:
        return render_template('home_disarm.html')


# ------------------------------------------------------------------------------$
# ŚCIEŻKA ODPOWIADAJĄCA ZA UZBROJENIE ALARMU
# ------------------------------------------------------------------------------$

@app.route('/ARM')
@check
def ARM():
    GPIO.remove_event_detect(sensor)
    global state
    state = True
    GPIO.output(blue, 1)

    #   detektor zdarzenia - zbocze narastające na sensorze ruchu
    GPIO.add_event_detect(sensor, GPIO.RISING, callback=trigger)

    return render_template('home_disarm.html')


# ------------------------------------------------------------------------------$
# ŚCIEŻKA ODPOWIADAJĄCA ZA ROZBROJENIE ALARMU
# ------------------------------------------------------------------------------$

@app.route('/DISARM')
@check
def DISARM():
    GPIO.remove_event_detect(sensor)
    global state
    state = False

    #   niebieski LED włączony / Czerwony LED wyłączony / Brzęczyk wyyłączony
    GPIO.output(blue, 0)
    GPIO.output(red, 0)
    GPIO.output(buzz, 0)

    return render_template('home.html')


# ------------------------------------------------------------------------------$
# ŚCIEŻKA ODPOWIADAJĄCA ZA POTWIERDZENIE WYŁĄCZENIA URZĄDZENIA
# ------------------------------------------------------------------------------$

@app.route('/SURE')
@check
def sure():
    return render_template('sure.html')


# ------------------------------------------------------------------------------$
# ŚCIEŻKA ODPOWIADAJĄCA ZA WYŁĄCZENIE URZĄDZENIA
# ------------------------------------------------------------------------------$

@app.route('/OFF')
@check
def OFF():
    os.system("sudo shutdown now")


# ------------------------------------------------------------------------------$
# ŚCIEŻKI ODPOWIADAJĄCE ZA POKAZYWANIE ARCHIWÓW STANÓW SYSTEMU
# ------------------------------------------------------------------------------$

@app.route('/DETECT')
@check
def file_detect():
    file = open("detect.txt", "r")
    archive = file.read()
    file.close()
    return render_template("archive.html", text=archive)


@app.route('/CONTINUE')
@check
def file_continue():
    file = open("continue.txt", "r")
    archive = file.read()
    file.close()
    return render_template("archive.html", text=archive)


# ------------------------------------------------------------------------------$
# URUCHOMIENIE APLIKACJI WEBOWEJ
# ------------------------------------------------------------------------------$

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=5000)

# ------------------------------------------------------------------------------$
#                                   KONIEC
# ------------------------------------------------------------------------------$
