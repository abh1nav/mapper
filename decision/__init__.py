#!/usr/bin/env python
# encoding: utf-8
import cPickle
import calendar
from datetime import datetime
import os
import pickle

import cherrypy
import pandas as pd

from cache import Cache
from geosearch import BikePosts

class Decision(object):

    def __init__(self, maps_proxy):
        self.maps = maps_proxy
        #self.model = BikeSpeedModel()
        self.bike_posts = BikePosts()
        self.cache = Cache()

    @cherrypy.expose
    @cherrypy.tools.json_out()
    def index(self):
        return {'status': 'ok', 'service': 'mapper/d'}

    @cherrypy.expose
    @cherrypy.tools.json_out()
    def bike_owner(self, start_lat, start_lng, end_lat, end_lng, arrive_by=None):
        start_lat = float(start_lat)
        start_lng = float(start_lng)
        end_lat = float(end_lat)
        end_lng = float(end_lng)
        start_point = {
            'lat': start_lat,
            'lng': start_lng
        }

        end_point = {
            'lat': end_lat,
            'lng': end_lng
        }

        # Find the bike post nearest to the end point
        mid_point = self.bike_posts.find_nearest(end_point['lat'], end_point['lng'])

        if arrive_by is None:
            arrive_by = calendar.timegm(datetime.now().timetuple())

        if mid_point:
            leg_2 = self.maps.p_walking('%s,%s' % (mid_point['lat'], mid_point['lng']),
                                     '%s,%s' % (end_lat, end_lng), arrival_time=arrive_by)
            leg_2_route = leg_2['routes'][0]
            leg_2_distance = leg_2_route['legs'][0]['distance']['value']
            leg_2_time = leg_2_route['legs'][0]['duration']['value'] / float(60)

            leg_1_arrive_by = arrive_by - leg_2_time
            leg_1 = self.maps.p_biking('%s,%s' % (start_lat, start_lng),
                                     '%s,%s' % (mid_point['lat'], mid_point['lng']), arrival_time=leg_1_arrive_by)
            leg_1_route = leg_1['routes'][0]
            leg_1_distance = leg_1_route['legs'][0]['distance']['value']

            model = BikeSpeedModel()
            model.create_user_features(start_point, mid_point, alt=10)
            model.scale()
            leg_1_pred_speed = model.predict()
            leg_1_distance_km = leg_1_distance/float(1000)
            leg_1_time = leg_1_distance_km/leg_1_pred_speed * float(60)

            return {
                'leg_1': {
                    'distance': leg_1_distance_km,
                    'speed': leg_1_pred_speed,
                    'time': leg_1_time,
                    'mid_point': mid_point
                },
                'leg_2': {
                    'distance': leg_2_distance,
                    'time': leg_2_time
                },
                'time': leg_1_time + leg_2_time,
                'unit': 'min'
            }

        else:
            leg_1 = self.maps.p_biking('%s,%s' % (start_lat, start_lng),
                                     '%s,%s' % (end_lat, end_lng), arrival_time=arrive_by)
            leg_1_route = leg_1['routes'][0]
            leg_1_distance = leg_1_route['legs'][0]['distance']['value']
            leg_1_time = leg_1_route['legs'][0]['duration']['value']

            return {
                'leg_1': {
                    'distance': leg_1_distance,
                    'time': leg_1_time
                }
            }


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
