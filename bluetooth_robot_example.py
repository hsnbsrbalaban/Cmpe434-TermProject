#!/usr/bin/env python3

'''
    Author: yigit.yildirim@boun.edu.tr
'''
from ev3dev2.sensor.lego import UltrasonicSensor
from ev3dev2.button import Button
import bluetooth
import time

class WhereAmI:
    def __init__(self):
        self.server_mac='88:B1:11:79:C5:F6'
        self.port=4
        self.us=UltrasonicSensor()
        self.btn = Button()
    def run(self):
        s=bluetooth.BluetoothSocket(bluetooth.RFCOMM)
        s.connect((self.server_mac, self.port))
        while True:
            text=str(self.us.distance_centimeters)
            if self.btn.any():
                break
            s.send(text)
            print(text)
            time.sleep(0.1)
        s.close()

if __name__ == "__main__":
    wai = WhereAmI()
    wai.run()