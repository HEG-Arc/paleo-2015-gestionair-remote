# -*- coding: UTF-8 -*-
# simulate_players.py
#
# Copyright (C) 2015 HES-SO//HEG Arc
#
# Author(s): Cédric Gaspoz <cedric.gaspoz@he-arc.ch>, Boris Fritscher <boris.fritscher@he-arc.ch>
#
# This file is part of paleo-2015-gestionair-control.
#
# paleo-2015-gestionair-control is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# paleo-2015-gestionair-control is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with paleo-2015-gestionair-control. If not, see <http://www.gnu.org/licenses/>.
import BaseHTTPServer

import json
import logging
import random
import time
import datetime
from threading import Thread, Timer

logging.basicConfig(level=logging.DEBUG)

CALL_CENTER = {'isRunning':False, 'startTime':None, 'demoState':'FREE', 'demoStart':None}

def format_datetime(start_time):
    if CALL_CENTER[start_time]:
        return CALL_CENTER[start_time].isoformat(' ')
    else:
        return None


def get_call_center():
    if CALL_CENTER['isRunning'] and CALL_CENTER['startTime']<datetime.datetime.now()-datetime.timedelta(seconds=5):
        CALL_CENTER['isRunning'] = False
        CALL_CENTER['startTime'] = None
    if CALL_CENTER['demoState']=='RINGING' and CALL_CENTER['demoStart']<datetime.datetime.now()-datetime.timedelta(seconds=3):
        CALL_CENTER['demoState'] = 'FREE'
        CALL_CENTER['demoStart'] = None
    print("Current state: %s" % CALL_CENTER)
    return {
             'isRunning':CALL_CENTER['isRunning'],
             'startTime':format_datetime('startTime'),
             'demoState':CALL_CENTER['demoState'],
             'demoStart':format_datetime('demoStart')
           }

class remote_sim(BaseHTTPServer.BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "application/json")
        self.end_headers()
        if self.path == '/game/api/status':
            self.wfile.write(json.dumps(get_call_center()))
        if self.path == '/game/start':
            CALL_CENTER['isRunning'] = True
            CALL_CENTER['startTime'] = datetime.datetime.now()
            self.wfile.write('OK')
        if self.path == '/game/stop':
            CALL_CENTER['isRunning'] = False
            CALL_CENTER['startTime'] = None
            self.wfile.write('OK')
        if self.path == '/game/api/play_sound/call':
            self.wfile.write('OK')
        if self.path == '/game/api/call/1201':
            CALL_CENTER['demoState'] = 'RINGING'
            CALL_CENTER['demoStart'] = datetime.datetime.now()
            self.wfile.write('OK')
        self.wfile.close()

    def log_message(self, format, *args):
        return


def web():
    server_address = ('', 8088)
    httpd = BaseHTTPServer.HTTPServer(server_address, remote_sim)
    httpd.serve_forever()

t = Thread(target=web)
t.start()
