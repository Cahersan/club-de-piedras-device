from gpiozero import Button, LED
from time import sleep

# led_1 = LED(14)
# led_2 = LED(15)
# led_3 = LED(4)
# led_4 = LED(17)
# led_5 = LED(27)
# led_6 = LED(22)
# led_7 = LED(10)

button = Button(10)

# leds = [led_1, led_2, led_3, led_4, led_5, led_6, led_7]

while True:
    # for led in leds:
    #     led.on()
    #     sleep(0.1)
    #     led.off()

    button.wait_for_press()
    print("pressed!")

    
