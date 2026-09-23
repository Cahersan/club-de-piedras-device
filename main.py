import time

import schedule
from gpiozero import MotionSensor
from tinydb import TinyDB

from classes import RockHandler

# Instantiate Database
db = TinyDB("db.json", sort_keys=True, indent=4, separators=(",", ": "))

sensor = MotionSensor(5, active_state=False, pull_up=None)

# Instantiate RockHandler
rock_handler = RockHandler(db)

# Assign actions to motion sensor
sensor.when_no_motion = rock_handler.start_meditation
sensor.when_motion = rock_handler.stop_meditation

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