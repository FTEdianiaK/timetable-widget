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

from csv import reader
import PySimpleGUI as sg
from datetime import datetime, timedelta


# Constant list
LAST_CHECK = datetime.now() - timedelta(minutes=1)
LOC = None
RUNNING = True

THEME = "Default"
TIME = ""
CURRENT = []
TIME_LEFT = ""
NEXT = []

FIELDS = []
ROWS = []


# Load data
try:
    with open("timetable.csv", "r", encoding="utf-8") as f:
        _raw = reader(f)
        FIELDS = next(_raw)
        for _row in _raw:
            if _row != []:
                ROWS.append(_row)
        f.close()
except FileNotFoundError:
    sg.PopupOK("Error! File 'timetable.csv' not found!", title="Error!")
    exit()


def time_format(i: timedelta) -> str:
    days, seconds = i.days, i.seconds
    hours = days * 24 + seconds // 3600
    minutes = (seconds % 3600) // 60

    r = f"{minutes}m"
    if hours != 0:
        r = f"{hours}h " + r

    return r


def update():
    global LAST_CHECK, THEME, TIME, CURRENT, TIME_LEFT, NEXT

    TIME = datetime.strftime(LAST_CHECK, "%H:%M")
    _time = datetime.strptime(TIME, "%H:%M")
    _row0 = ROWS[LAST_CHECK.weekday()]
    _row1 = ROWS[LAST_CHECK.weekday() + 7]

    for i in range(0, len(FIELDS)-1):
        _cur = datetime.strptime(FIELDS[i], "%H:%M")
        _nxt = datetime.strptime(FIELDS[i+1], "%H:%M")

        if _nxt > _time >= _cur:
            CURRENT = [_row0[i], _row1[i]]
            NEXT = [_row0[i+1], _row1[i+1]]
            TIME_LEFT = time_format(_nxt - _time)
            break

    if CURRENT == []:
        _bgn = datetime.strptime(FIELDS[0], "%H:%M")
        _end = datetime.strptime(FIELDS[len(FIELDS)-1], "%H:%M")

        if _time <= _bgn:
            CURRENT = [ROWS[14][0], ""]
            NEXT = [_row0[0], _row1[0]]
            TIME_LEFT = time_format(_bgn - _time)
        elif _time >= _end:
            _tommorow = LAST_CHECK + timedelta(days=1)
            _row0 = ROWS[_tommorow.weekday()]
            _row1 = ROWS[_tommorow.weekday() + 7]

            CURRENT = [ROWS[14][1], ""]
            NEXT = [_row0[0], _row1[0]]
            TIME_LEFT = time_format(_bgn - _time + timedelta(hours=24))

    if CURRENT[0] in ROWS[14]:
        if THEME != "LightBlue2":
            THEME = "LightBlue2"
            return True
        else:
            return False
    else:
        if THEME != "LightBrown6":
            THEME = "LightBrown6"
            return True
        else:
            return False


# Window definition
LO = [[sg.T("Initializing..."), sg.P()]]
Win = sg.Window("Timetable Widget", LO, finalize=True)

while RUNNING:
    now = datetime.now()

    if now.minute != LAST_CHECK.minute:
        LAST_CHECK = now
        LOC = Win.CurrentLocation()

        Win.close()

        if update():
            sg.theme(THEME)

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
