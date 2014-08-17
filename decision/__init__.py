#!/usr/bin/env python
# encoding: utf-8
import cPickle
import calendar

import cherrypy
import os
import pickle
from datetime import datetime
import pandas as pd
from sklearn.preprocessing import MinMaxScaler
from sklearn.ensemble import RandomForestRegressor
from sklearn.externals import joblib

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
        if not arrive_by:
            location_info = self.maps.biking(start_loc, end_loc, departure_time=calendar.timegm(datetime.now().timetuple()))
        else:
            location_info = self.maps.biking(start_loc, end_loc, arrival_time=arrive_by)

        route = location_info['routes'][0]
        start_point = route['legs'][0]['start_location']
        end_point = route['legs'][-1]['end_location']

        self.model.create_user_features(start_point, end_point, alt=10)
        self.model.scale()
        pred_speed = self.model.predict()

        return {'time': "?", 'predicted_speed': pred_speed}



class BikeSpeedModel:
    def __init__(self):
        self.model = None
        self.scaler = None
        self.temp_today = None
        self.feature_list = []
        self._deserialize()
        self._get_weather()

    def _deserialize(self):
        file_location = os.path.dirname(os.path.abspath(__file__))
        print file_location
        with open(file_location + '/model.txt', "r") as f:
            model_scaler_dict = pickle.load(f)
            self.model = model_scaler_dict['model']
            self.scaler = model_scaler_dict['scaler']

    def _get_weather(self):
        simple_today = str(datetime.now().month) + str(datetime.now().day)
        with open(os.path.dirname(os.path.abspath(__file__)) + '/weather.csv', 'r') as w:
            weather = pd.read_csv(w)
            weather['Date'] = pd.to_datetime(weather['Date'], format='%m-%d-%Y')
            weather['Simple Date'] = weather.apply(lambda row: str(row['Date'].month) + str(row['Date'].day), axis=1)
            temp_today = weather[weather['Simple Date'] == simple_today]
        self.temp_today = temp_today['Mean_Temperature_C'].values[0]

    def create_user_features(self, start_loc, end_loc, alt):
        now = datetime.now()
        self.feature_list = [start_loc['lat'], start_loc['lng']]

        if now.weekday in [5, 6]:
            weekend = 1
        else:
            weekend = 0

        lat_delta = end_loc['lat'] - start_loc['lat']
        lon_delta = end_loc['lng'] - start_loc['lng']

        #alt_delta = end_loc['altitude'] - start_loc['altitude']
        alt_delta = 10

        raining = 0  # Assuming not raining - rain has little effect on prediction anyways

        hour = [0]*22
        if now.hour in [0,1]:
            hour[now.hour] = 1
        else:
            hour[now.hour-2] = 1

        days_of_week = [0]*7
        days_of_week[now.weekday()] = 1

        self.feature_list.extend([weekend, lat_delta, lon_delta, alt_delta, self.temp_today, raining])
        self.feature_list.extend(hour)
        self.feature_list.extend(days_of_week)

    def scale(self):
        self.feature_list = self.scaler.transform(self.feature_list)

    def predict(self):
        predicted_value = self.model.predict(self.feature_list)[0]
        return predicted_value
