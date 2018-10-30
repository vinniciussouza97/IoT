import sys
import time
import signal
import RPi.GPIO as GPIO
import requests
import Adafruit_DHT

GPIO.setmode(GPIO.BCM)

def clean():
    GPIO.cleanup()

def sigint_handler(signum, instant):
    clean()
    sys.exit()

signal.signal(signal.SIGINT, sigint_handler)

#Definições de variáveis
sensor = Adafruit_DHT.DHT11

pino_sensor = 5

TRIG = 23
ECHO = 24

TRIG2 = 17
ECHO2 = 27

LED = 21

porta = 1
porta2 = 1
pessoas = 0

#Definições dos sensores ultrassônicos
sampling_rate = 20.0
speed_of_sound = 349.10
max_distance = 4.0
max_delta_t = max_distance / speed_of_sound

#Setup do GPIO
GPIO.setup(TRIG, GPIO.OUT)
GPIO.setup(ECHO, GPIO.IN)
GPIO.setup(TRIG2, GPIO.OUT)
GPIO.setup(ECHO2, GPIO.IN)
GPIO.setup(LED, GPIO.OUT)
GPIO.output(TRIG, False)
GPIO.output(TRIG2, False)
time.sleep(1)

print ("Sampling Rate:", sampling_rate, "Hz")
print ("Distances (cm)")

#Variáveis para "debouncing" dos sensores
dist_ant = 0
dist_ant2 = 0

#Definições para post e get HTTP
TOKEN = "A1E-nkLIQeYE47RzHQ0ymL0jlDxBJWjwZk"  # Put your TOKEN here
DEVICE_LABEL = "raspberry"  # Put your device label here 
VARIABLE_LABEL_1 = "pessoas"  # Put your first variable label here
VARIABLE = "led"
VARIABLE_TEMP = "temperatura"
VARIABLE_UMI = "umidade"

#Função que faz GET HTTP
def get_var(device, variable):
    try:
        url = "http://things.ubidots.com/"
        url = url + \
            "api/v1.6/devices/{0}/{1}/".format(device, variable)
        headers = {"X-Auth-Token": TOKEN, "Content-Type": "application/json"}
        req = requests.get(url=url, headers=headers)
        return req.json()['last_value']['value']
    except:
        pass

#Construção do json para POST
def build_payload(variable_1, value_1, variable_2, value_2, variable_3, value_3):
    payload = {variable_1: value_1,
               variable_2: value_2,
               variable_3: value_3}
    return payload

#Envia o POST para o HTTP
def post_request(payload):
    # Creates the headers for the HTTP requests
    url = "http://things.ubidots.com"
    url = "{}/api/v1.6/devices/{}".format(url, DEVICE_LABEL)
    headers = {"X-Auth-Token": TOKEN, "Content-Type": "application/json"}

    # Makes the HTTP requests
    status = 400
    attempts = 0
    while status >= 400 and attempts <= 5:
        req = requests.post(url=url, headers=headers, json=payload)
        status = req.status_code
        attempts += 1
        time.sleep(1)

    # Processes results
    if status >= 400:
        print("[ERROR] Could not send data after 5 attempts, please check \
            your token credentials and internet connection")
        return False
    print("Enviado")
    return True

#Definições de PWM
pwm = GPIO.PWM(21,100)
pwm.start(0)

#Loop principal
while True:

    #Inicio da leitura do primeiro sensor ultrassônico
    GPIO.output(TRIG, True)
    time.sleep(0.00001)
    GPIO.output(TRIG, False)


    while GPIO.input(ECHO) == 0:
      start_t = time.time()


    while GPIO.input(ECHO) == 1 and time.time() - start_t < max_delta_t:
      end_t = time.time()


    if end_t - start_t < max_delta_t:
        delta_t = end_t - start_t
        distance = 100*(0.5 * delta_t * speed_of_sound)
        dist_ant = distance
    else:
        distance = dist_ant
    #Fim da leitura do primeiro sensor ultrassônico
    print (round(distance, 2))

    #Função de "debouncing" da medição de distância
    if distance < 28:
        porta = 1
    elif porta == 1:
        porta = 0
        pessoas += 1
        
        #Medição do sensor de temperatura/umidade
        umid, temp = Adafruit_DHT.read_retry(sensor, pino_sensor)
        if umid is not None and temp is not None:
            #Post das variáveis
            payload = build_payload(VARIABLE_LABEL_1, pessoas, VARIABLE_TEMP, temp, VARIABLE_UMI, umid)
            post_request(payload)

    #Inicio da leitura do segundo sensor ultrassônico
    GPIO.output(TRIG2, True)
    time.sleep(0.00001)
    GPIO.output(TRIG2, False)


    while GPIO.input(ECHO2) == 0:
      start_t = time.time()


    while GPIO.input(ECHO2) == 1 and time.time() - start_t < max_delta_t:
      end_t = time.time()


    if end_t - start_t < max_delta_t:
        delta_t = end_t - start_t
        distance2 = 100*(0.5 * delta_t * speed_of_sound)
        dist_ant2 = distance2
    else:
        distance2 = dist_ant2

    print (round(distance2, 2))
    #Fim da leitura do segundo sensor ultrassônico

    #Função de "debouncing" da medição de distância
    if distance2 < 28:
        porta2 = 1
    elif porta2 == 1:
        porta2 = 0
        pessoas -= 1
        if pessoas < 0:
            pessoas = 0

        #Medição do sensor de temperatura/umidade
        umid, temp = Adafruit_DHT.read_retry(sensor, pino_sensor)
        if umid is not None and temp is not None:
            #Post das variáveis
            payload = build_payload(VARIABLE_LABEL_1, pessoas, VARIABLE_TEMP, temp, VARIABLE_UMI, umid)
            post_request(payload)

    #Obtenção do valor do PWM do LED
    valor = get_var(DEVICE_LABEL, VARIABLE)
    if valor != None:
        pwm.ChangeDutyCycle(valor)
                
    time.sleep(1/sampling_rate)


