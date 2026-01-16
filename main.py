import time

import schedule
from gpiozero import Button, MotionSensor
from tinydb import TinyDB

from classes import RockHandler

# Instantiate Database
db = TinyDB("db.json", sort_keys=True, indent=4, separators=(",", ": "))

Button.was_held = False

sensor = MotionSensor(5, active_state=False, pull_up=None)


# Instantiate RockHandler
rock_handler = RockHandler(db)

# Assign actions to buttons
sensor.when_no_motion = rock_handler.start_meditation
sensor.when_motion = rock_handler.stop_meditation

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
