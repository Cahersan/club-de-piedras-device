from dataclasses import asdict
from datetime import datetime, timedelta
from itertools import chain
from time import sleep

import pygame.mixer
from gpiozero import LEDBoard
from pygame.mixer import music
from tinydb import where
from tinydb.table import Document

from data_structures import DayData, SessionData

pygame.mixer.init()


class LEDHandler:
    leds = LEDBoard(16, 25, 24, 23, 22, 27, 17, pwm=True)
    led_num = 1

    def slow_blink(self, led_num, fade_time=1):
        self.led_num = led_num % 8
        self.leds[self.led_num - 1].pulse(fade_time, fade_time)

    def fast_blink(self, led_num):
        self.led_num = led_num % 8
        self.leds[self.led_num - 1].blink(0.1, 0.1, n=5)

    def sweep_blink(self, times=3):
        indices = [range(0, 7, 1), range(5, 0, -1)] * times

        for index in chain.from_iterable(indices):
            self.leds[index].on()
            sleep(0.04)
            self.leds[index].off()

    def clear(self):
        self.leds.off()

    def turn_on(self, led_num):
        self.led_num = led_num % 8
        self.leds[self.led_num - 1].on()

    def turn_off(self, led_num):
        self.led_num = led_num % 8
        self.leds[self.led_num - 1].off()

    def move_next(self):
        self.turn_off(self.led_num)
        self.led_num += 1
        self.turn_on(self.led_num)

    def move_prev(self):
        self.turn_off(self.led_num)
        self.led_num -= 1
        self.turn_on(self.led_num)


class Player:
    # files = [
    #     "chakra_meditation/01-Lam.wav",
    #     "chakra_meditation/02-Vam.wav",
    #     "chakra_meditation/03-Ram.wav",
    #     "chakra_meditation/04-Yam.wav",
    #     "chakra_meditation/05-Ham.wav",
    #     "chakra_meditation/06-Om.wav",
    #     "chakra_meditation/07-Am.wav",
    # ]

    files = [
        "cdp_audios/01-carbon.wav",
        "cdp_audios/02-coral.wav",
        "cdp_audios/03-estalagtita.wav",
        "cdp_audios/04-goethita.wav",
        "cdp_audios/05-olivo.wav",
        "cdp_audios/06-volcanica.wav",
        "cdp_audios/07-lapis.wav",
    ]

    file_num = 1

    def play_sound(self, file_num):
        self.file_num = file_num % 8
        music.load(self.files[self.file_num - 1])
        music.set_volume(0.1)
        music.play()
        print(f"playing sound ({self.file_num}) {self.files[self.file_num - 1]}")


    def stop_sound(self):
        music.fadeout(1000)
        music.unload()
        print(f"stopping sound ({self.file_num}) {self.files[self.file_num - 1]}")


class RockHandler:
    db = None
    status_table = None
    journal_table = None
    sessions_table = None

    d_id = None
    current_day = None

    s_id = None
    current_session = None

    led_handler = None
    player = None

    meditating = False

    def __init__(self, db=None):
        self.db = db

    def initialize(self):
        print("loading leds...")
        self.led_handler = LEDHandler()
        print("leds ready!")

        print("loading player...")
        self.player = Player()
        print("player ready!")

    def load_state(self):
        print("loading state...")
        self.led_handler.clear()
        self.current_day = DayData()

        self.status_table = self.db.table("status")
        self.journal_table = self.db.table("journal")

        # Load status (last registered day ID) from DB
        status = self.status_table.get(doc_id=1)

        # A missing status implies an empty DB that must be initialized
        if not (status):
            self.db.drop_tables()
            self.d_id = self.journal_table.insert(asdict(DayData()))
            self.status_table.insert({"d_id": self.d_id})

        # TODO: What happens if the device is off for several days?

        # Load last registered day
        self.d_id = self.status_table.get(doc_id=1)["d_id"]

        current_day = self.journal_table.get(doc_id=self.d_id)
        self.current_day = DayData(**current_day)

        days = self.journal_table.search(where("week_num") == self.current_day.week_num)

        # Load initial state
        for day in days:
            day_num = day["day_num"]
            done = day["done"]
            if done:
                self.led_handler.turn_on(day_num)

        # TODO: As of now, we assume the current day is the last day stored in the db
        self.current_day.day_num = day_num
        self.current_day.done = done

        if not done:
            self.led_handler.slow_blink(self.current_day.day_num)

        print("ready!")

    def start_meditation(self):
        self.meditating = True

        self.player.play_sound(self.current_day.day_num)
        self.led_handler.slow_blink(self.current_day.day_num, fade_time=5)

        # Set up session in DB
        self.current_session = SessionData()
        self.sessions_table = self.db.table("sessions")

        self.s_id = self.sessions_table.insert(asdict(self.current_session))
        self.current_day.sessions.append(self.s_id)
        self.journal_table.upsert(Document({"sessions": self.current_day.sessions}, doc_id=self.d_id))

        print(f"Meditation started at {self.current_session.isodatetime}.")

    def stop_meditation(self):
        self.meditating = False
        self.player.stop_sound()

        self.check_done()

        if self.current_day.done:
            self.led_handler.turn_on(self.current_day.day_num)
        else:
            self.led_handler.slow_blink(self.current_day.day_num)

        # Update day and session in DB
        d_doc = Document({"done": self.current_day.done}, doc_id=self.d_id)
        self.journal_table.upsert(d_doc)

        duration = datetime.now() - datetime.fromisoformat(self.current_session.isodatetime)
        s_doc = Document({"done": self.current_day.done, "duration": duration.total_seconds()}, doc_id=self.s_id)
        self.sessions_table.upsert(s_doc)

        # Clear existing session
        self.current_session = None
        self.s_id = None

        print(f"Meditation stopped. Done={self.current_day.done}")

    def check_done(self):
        if self.current_day.done:
            return

        if (datetime.now() - datetime.fromisoformat(self.current_session.isodatetime)) >= timedelta(minutes=5):
            self.current_day.done = True

    def next_day(self):
        if self.meditating:
            # TODO: Better handling in case of date change while meditation is ongoing
            self.stop_meditation()

        # Do not advance if it's the first day and meditation is not done
        if self.current_day.day_num == 1 and not self.current_day.done:
            print("Will not advance, as meditation is not done on the first day.")
            return

        if not self.current_day.done:
            self.led_handler.turn_off(self.current_day.day_num)

        day_num = self.current_day.day_num + 1
        week_num = self.current_day.week_num

        if day_num > 7:
            day_num = 1
            week_num = self.current_day.week_num + 1
            self.led_handler.clear()

        self.current_day = DayData(week_num=week_num, day_num=day_num)
        self.led_handler.slow_blink(self.current_day.day_num)

        # Set up next day in DB
        self.d_id = self.journal_table.insert(asdict(self.current_day))
        self.status_table.upsert(Document({"d_id": self.d_id}, doc_id=1))
        print("Next day!")
