from midea.client import client as midea_client
import json
from pprint import pprint
import requests
from time import sleep
import asyncio

class AirAuto(object):
    def __init__(self, file_name):
        with open(file_name, 'r') as f:
            data = json.load(f)
        self.ow_key = data['ow_key']
        self.city = data['city']

        self.key = data['key']
        self.user = data['user']
        self.password = data['password']

        self.client = midea_client(self.key, self.user, self.password)
        self.client.setup()
        #pprint(dir(client._cloud))
        self.devices = self.client.devices()
        self.device1 = self.devices[0]
        self.device1.refresh()

    def log(self, text):
        msg = '|-- {0} ----------------------------------------------------|'.format(text)
        print(msg)

    def getCityHumidity(self):
        url = "http://api.openweathermap.org/data/2.5/weather?q={0}&appid={1}".format(self.city, self.ow_key)
        meteo_data = requests.get(url).json()
        humidity = meteo_data['main']['humidity']
        return humidity

    def getCityTemperature(self):
        url = "http://api.openweathermap.org/data/2.5/weather?q={0}&appid={1}".format(self.city, self.ow_key)
        meteo_data = requests.get(url).json()
        print(meteo_data)
        temperature = meteo_data['main']['temp']/10
        return temperature

    def printDevice(self):
        pprint(dir(self.device1))

    def setTemperature(self, target_temp):
        before = self.device1.target_temperature
        self.device1.target_temperature = target_temp
        self.device1.apply()
        self.device1.refresh()
        changed = self.device1.target_temperature != before
        self.log('changed temperature : {0}'.format(changed))
        return changed

    def setMode(self, mode):
        before = self.device1.operational_mode
        mode_to_set = None
        oper_enum = self.device1.operational_mode_enum
        if mode == "cool":
            mode_to_set = oper_enum.cool
        elif mode == "dry":
            mode_to_set = oper_enum.dry
        if mode_to_set is not None:
            self.device1.operational_mode = mode_to_set
            self.device1.apply()
        self.device1.refresh()

        changed = self.device1.operational_mode != before
        self.log('changed mode : {0}'.format(changed))
        return changed

    async def autoManageHumidity(self):
        while True:
            city_humidity = self.getCityHumidity()
            city_temp = self.getCityTemperature()
            if city_humidity > 65:
                self.setMode('dry')
            elif city_temp > 25:
                self.setMode('cool')
            sleep(60)
