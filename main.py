import time

import schedule
from gpiozero import  Button, MotionSensor
from tinydb import TinyDB

from classes import RockHandler

# Instantiate Database
db = TinyDB("db.json", sort_keys=True, indent=4, separators=(",", ": "))

# Set up motion sensor and volume buttons
sensor = MotionSensor(5, active_state=False, pull_up=None)
vol_up = Button(23)
vol_down = Button(24)

# Instantiate RockHandler
rock_handler = RockHandler(db)

# Assign actions to motion sensor
sensor.when_no_motion = rock_handler.start_meditation
sensor.when_motion = rock_handler.stop_meditation

# Assign actions to volume buttons
vol_up.when_pressed = rock_handler.volume_up
vol_down.when_pressed = rock_handler.volume_down

# Initialize RockHandler
rock_handler.initialize()
rock_handler.pixels_handler.sweep(times=5)
rock_handler.load_state()

# Scheduled actions
schedule.every().day.at("00:00").do(rock_handler.next_day)


def run_schedule():
    while True:
        # Scheduled date change actions
        schedule.run_pending()

        # Run these actions every 5 minutes
        time.sleep(300)

def shutdown():
    rock_handler.shutdown()
    sensor.close()
    db.close()

try:
    run_schedule()
except KeyboardInterrupt:
    pass
finally:
    shutdown()
