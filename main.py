import time

import schedule
from gpiozero import Button
from tinydb import TinyDB

from classes import RockHandler

# Instantiate Database
db = TinyDB("db.json", sort_keys=True, indent=4, separators=(",", ": "))

Button.was_held = False

button_1 = Button(5, bounce_time=0.1, hold_time=3)
button_2 = Button(6, bounce_time=0.1)


# Instantiate RockHandler
rock_handler = RockHandler(db)

# Assign actions to buttons
button_1.when_released = rock_handler.btn_released
button_1.when_held = rock_handler.finish_meditation
button_2.when_pressed = rock_handler.next_day

rock_handler.initialize()
rock_handler.led_handler.sweep_blink(times=5)
rock_handler.load_state()

# Scheduled actions
schedule.every().day.at("00:00").do(rock_handler.next_day)

while True:
    # Check if meditation was running for 5 minutes
    if rock_handler.meditating and not rock_handler.current_day.done:
        rock_handler.check_done()

    # Scheduled date change actions
    schedule.run_pending()

    # Run these actions every 5 seconds
    time.sleep(5)
