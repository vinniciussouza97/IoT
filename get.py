import requests
import random
import time
import RPi.GPIO as GPIO

GPIO.setmode(GPIO.BCM)

LED = 21

GPIO.setup(LED, GPIO.OUT)

TOKEN = "A1E-nkLIQeYE47RzHQ0ymL0jlDxBJWjwZk" # Assign your Ubidots Token
DEVICE = "raspberry" # Assign the device label to obtain the variable
VARIABLE = "led" # Assign the variable label to obtain the variable value
DELAY = 1  # Delay in seconds

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

pwm = GPIO.PWM(21,100)
pwm.start(0)

if __name__ == "__main__":
    while True:
        valor = get_var(DEVICE, VARIABLE)
        print(valor)
        if valor != None:
            pwm.ChangeDutyCycle(valor)
        time.sleep(DELAY)
