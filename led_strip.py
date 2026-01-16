from gpiozero import LEDBoard
from itertools import chain
from time import sleep

leds = LEDBoard(16, 25, 24, 23, 22, 27, 17, pwm=True)

def sweep_blink(times=3):
    indices = [range(0, 7, 1), range(5, 0, -1)] * times

    for index in chain.from_iterable(indices):
        leds[index].on()
        sleep(0.04)
        leds[index].off()

while True:
    sweep_blink()
    sleep(3)

    
