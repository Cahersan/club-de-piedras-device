from dataclasses import dataclass
from datetime import date, datetime


@dataclass
class SessionData:
    isodatetime: str
    duration: int = 0
    done: bool = False

    def __init__(self, isodatetime=None, duration=None, done=False):
        self.isodatetime = isodatetime or datetime.now().isoformat()
        self.duration = duration
        self.done = done

@dataclass
class DayData:
    isodate: str
    week_num: int
    day_num: int
    done: bool
    file: str
    sessions: list

    def __init__(
        self, isodate=None, week_num=1, day_num=1, done=False, file=None, sessions=[]
    ):
        self.isodate = isodate or date.today().isoformat()
        self.week_num = week_num
        self.day_num = day_num
        self.done = done
        self.file = file
        self.sessions = sessions
