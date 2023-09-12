# Timetable Widget: A basic, portable time table widget.
# Copyright (C) 2023  Foxie EdianiaK a.k.a. F_TEK

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

from csv import reader as cread
from csv import writer as cwrite
import PySimpleGUI as sg
from datetime import datetime, timedelta
from json import dump as jdump
from json import load as jload


# Constant list
LAST_CHECK = datetime.now() - timedelta(minutes=1)
LOC = None
RUNNING = True

TIME = ""
CURRENT = []
TIME_LEFT = 0
NEXT = []

FIELDS = []
ROWS = []
REPL = {}

sg.theme("Default1")


# Load data
try:
    with open("timetable.csv", "x", encoding="utf-8") as f:
        _wrt = cwrite(f)
        _wrt.writerow(['HH:MM', 'HH:MM'])
        _wrt.writerows([['Monday1', 'Monday2'],
                        ['Tuesday1', 'Tuesday2'],
                        ['Wednesday1', 'Wednesday2'],
                        ['Thursday1', 'Thursday2'],
                        ['Friday1', 'Friday2'],
                        ['Saturday1', 'Saturday2'],
                        ['Sunday1', 'Sunday2'],
                        ['Monday1Note', 'Monday2Note'],
                        ['Tuesday1Note', 'Tuesday2Note'],
                        ['Wednesday1Note', 'Wednesday2Note'],
                        ['Thursday1Note', 'Thursday2Note'],
                        ['Friday1Note', 'Friday2Note'],
                        ['Saturday1Note', 'Saturday2Note'],
                        ['Sunday1Note', 'Sunday2Note'],
                        ['DayDidntStartMessage', 'DayEndedMesssage']])
        f.close()
        sg.PopupOK("Please fill out the newly created timetable.csv"
                   + " before relaunching the app.\n"
                   + "NOTE: You may add as many columns as you'd like.")
        exit()
except FileExistsError:
    with open("timetable.csv", "r", encoding="utf-8") as f:
        _raw = cread(f)
        FIELDS = next(_raw)
        for _row in _raw:
            if _row != []:
                ROWS.append(_row)
        f.close()


try:
    with open("substitution.json", "x", encoding="utf-8") as f:
        jdump(dict({"mm-dd": {"0": ["Hour1", "Hour1Note"],
                              "1": ["Hour2", "Hour2Note"]}}), f)
        f.close()
        sg.PopupOK("You may use the newly created substitution.json to fill "
                   + "out any temporary changes to the regular time-table.")
except FileExistsError:
    with open("substitution.json", "r", encoding="utf-8") as f:
        REPL = jload(f)
        f.close()


def time_format(i: timedelta) -> str:
    days, seconds = i.days, i.seconds
    hours = days * 24 + seconds // 3600
    minutes = (seconds % 3600) // 60

    r = f"{minutes}m"
    if hours != 0:
        r = f"{hours}h " + r

    return r


def update():
    global LAST_CHECK, TIME, CURRENT, TIME_LEFT, NEXT

    CURRENT = []
    TIME_LEFT = ""
    NEXT = []

    TIME = datetime.strftime(LAST_CHECK, "%H:%M")
    _time = datetime.strptime(TIME, "%H:%M")
    _row0 = ROWS[LAST_CHECK.weekday()]
    _row1 = ROWS[LAST_CHECK.weekday() + 7]

    try:
        _repl = REPL[datetime.strftime(LAST_CHECK, "%m-%d")]
    except KeyError:
        _repl = None

    for i in range(0, len(FIELDS)-1):
        _cur = datetime.strptime(FIELDS[i], "%H:%M")
        _nxt = datetime.strptime(FIELDS[i+1], "%H:%M")

        if _nxt > _time >= _cur:
            CURRENT = [_row0[i], _row1[i]]
            NEXT = [_row0[i+1], _row1[i+1]]

            if _repl is not None:
                try:
                    CURRENT = _repl[str(i)]
                except KeyError:
                    pass

                try:
                    NEXT = _repl[str(i+1)]
                except KeyError:
                    pass

            TIME_LEFT = time_format(_nxt - _time)

            break

    if CURRENT == []:
        _bgn = datetime.strptime(FIELDS[0], "%H:%M")
        _len = len(FIELDS)-1
        _end = datetime.strptime(FIELDS[_len], "%H:%M")

        if _time <= _bgn:
            CURRENT = [ROWS[14][0], ""]
            NEXT = [_row0[0], _row1[0]]

            if _repl is not None:
                try:
                    NEXT = _repl["0"]
                except KeyError:
                    pass

            TIME_LEFT = time_format(_bgn - _time)
        elif _time >= _end:
            _tommorow = LAST_CHECK + timedelta(days=1)
            _row0 = ROWS[_tommorow.weekday()]
            _row1 = ROWS[_tommorow.weekday() + 7]

            try:
                _repl = REPL[datetime.strftime(_tommorow, "%m-%d")]
            except KeyError:
                _repl = None

            CURRENT = [ROWS[14][1], ""]
            NEXT = [_row0[0], _row1[0]]

            if _repl is not None:
                try:
                    NEXT = _repl["0"]
                except KeyError:
                    pass

            TIME_LEFT = time_format(_bgn - _time + timedelta(hours=24))


# Window definition
LO = [[sg.P(), sg.T(""), sg.P()],
      [sg.T("Current:"), sg.T(""), sg.T("")],
      [sg.T("Time left:"), sg.T("")],
      [sg.T("Next:"), sg.T(""), sg.T("")]]
Win = sg.Window("Timetable Widget",
                LO,
                keep_on_top=True,
                finalize=True,
                grab_anywhere=True,
                no_titlebar=True)


while RUNNING:
    now = datetime.now()

    if now.minute != LAST_CHECK.minute:
        LAST_CHECK = now
        LOC = Win.CurrentLocation()

        Win.close()
        update()
        LO = [[sg.P(), sg.T(TIME, font="Arial 24 bold"), sg.P()],
              [sg.P(), sg.T("Current:", font="Arial 10"), sg.P()],
              [sg.P(), sg.T(CURRENT[0], font="Arial 14"),
               sg.T(CURRENT[1], font="Arial 10 italic"), sg.P()],
              [sg.P(), sg.T("Time left:", font="Arial 10"), sg.P()],
              [sg.P(), sg.T(TIME_LEFT, font="Arial 14"), sg.P()],
              [sg.P(), sg.T("Next:", font="Arial 10"), sg.P()],
              [sg.P(), sg.T(NEXT[0], font="Arial 14"),
               sg.T(NEXT[1], font="Arial 10 italic"), sg.P()]]
        Win = sg.Window("Timetable Widget",
                        LO,
                        keep_on_top=True,
                        grab_anywhere=True,
                        no_titlebar=True,
                        location=LOC)

        now = datetime.now()
        if now.minute == LAST_CHECK.minute:
            if now.second < 55:
                Win.read(timeout=(55 - now.second))

    ev, val = Win.read(timeout=1)

    if ev == sg.WIN_CLOSED:
        RUNNING = False
