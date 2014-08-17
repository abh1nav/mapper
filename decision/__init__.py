#!/usr/bin/env python
# encoding: utf-8

import cherrypy
import os
import pickle
from datetime import datetime
import pandas as pd
from sklearn.preprocessing import MinMaxScaler
from sklearn.ensemble import RandomForestRegressor

class Decision(object):

    def __init__(self, maps_proxy):
        self.maps = maps_proxy
        self.model = BikeSpeedModel()

    @cherrypy.expose
    @cherrypy.tools.json_out()
    def index(self):
        return {'status': 'ok', 'service': 'mapper/d'}

    @cherrypy.expose
    @cherrypy.tools.json_out()
    def bike_owner(self, start_loc, end_loc, arrive_by=None):
        self.model.create_user_features(start_loc, end_loc)

        if not arrive_by:
            pass
        else:
            pass

        return {'time': 'not yet implemented'}



class BikeSpeedModel:
    def __init__(self):
        self.model = None
        self.scaler = None
        self.temp_today = None
        self.feature_list = []
        self._deserialize()
        self._get_weather()

    def _deserialize(self):
        with open(os.path.join(os.path.dirname(__file__), '/model'), "r") as f:
            self.model = pickle.load(f)#['model']
            #self.scaler = pickle.load(f)['scaler']

    def _get_weather(self):
        today = datetime.now().date()
        with open(os.path.join(os.path.dirname(__file__), '/weather.csv', 'r')) as w:
            weather = pd.read_csv(w)
            weather['Date'] = pd.to_datetime(weather['Date'], format='%m-%d-%Y')
            weather['Simple Date'] = weather.apply(lambda row: row['Date'].date(), axis=1)
            temp_today = weather[weather['Simple Date'] == today]
        self.temp_today = temp_today

    def create_user_features(self, start_loc, end_loc, alt):
        now = datetime.now()
        self.feature_list = [start_loc['latitude'], start_loc['longitude']]
        if now.weekday in [5, 6]:
            weekend = 1
        else:
            weekend = 0

        lat_delta = end_loc['latitude'] - start_loc['latitude']
        lon_delta = end_loc['longitude'] - start_loc['longitude']

        alt_delta = end_loc['altitude'] - start_loc['altitude']

        raining = 0  # Assuming not raining - rain has little effect on prediction anyways

        hour = [0]*24
        hour[now.hour] = 1

        days_of_week = [0]*7
        days_of_week[now.day] = 1

        self.feature_list.extend([weekend, lat_delta, lon_delta, alt_delta, self.temp_today, raining])
        self.feature_list.extend(hour)
        self.feature_list.extend(days_of_week)

    def scale(self):
        self.feature_list = self.scaler.transform(self.feature_list)

    def predict(self, start_loc, end_loc):
        pass
