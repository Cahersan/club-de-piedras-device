from classes import PixelsHandler
import time


pixels = PixelsHandler()
sleep_time = 0.02

# for i in range(8):
#     pixels.turn_on(i)
#     time.sleep(sleep_time)

# for i in range(8):
#     pixels.turn_off(i)
#     time.sleep(sleep_time)

# pixels.sweep_blink()

for i in range(1, 17):
    print(pixels.pixel_num)
    print(i)
    pixels.move_next()
    time.sleep(.5)

pixels.clear()
