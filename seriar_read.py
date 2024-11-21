import serial
from time import sleep

s = serial.Serial('COM7')
while True:
    res = s.read()
    print(f"{int.from_bytes(res)}")
