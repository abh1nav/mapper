#!/usr/bin/env python
# encoding: utf-8
import calendar
from datetime import datetime

import cherrypy

from cache import Cache
from geosearch import BikePosts, BixiPods
from bike_speed_model import BikeSpeedModel


class Decision(object):

    def __init__(self, maps_proxy):
        self.maps = maps_proxy
        self.bike_posts = BikePosts()
        self.bixi_pods = BixiPods()
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
        else:
            arrive_by = long(arrive_by)

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
                'waypoints': [
                    start_point,
                    mid_point,
                    end_point
                ],
                'legs': [
                    {
                        'start': start_point,
                        'end': mid_point,
                        'mode': 'cycling',
                        'distance': leg_1_distance_km,
                        'speed': leg_1_pred_speed,
                        'time': leg_1_time,
                    },
                    {
                        'start': mid_point,
                        'end': end_point,
                        'distance': leg_2_distance,
                        'time': leg_2_time,
                        'mode': 'walking'
                    }
                ],
                'time': leg_1_time + leg_2_time,
                'unit': 'min'
            }

        else:
            leg_1 = self.maps.p_biking('%s,%s' % (start_lat, start_lng),
                                     '%s,%s' % (end_lat, end_lng), arrival_time=arrive_by)
            leg_1_route = leg_1['routes'][0]
            leg_1_distance = leg_1_route['legs'][0]['distance']['value'] / 1000.0
            leg_1_time = leg_1_route['legs'][0]['duration']['value'] / 60.0

            return {
                'waypoints': [
                    start_point,
                    end_point
                ],
                'legs': [
                    {
                        'distance': leg_1_distance,
                        'time': leg_1_time,
                        'mode': 'cycling'
                    }
                ],
                'time': leg_1_time,
                'unit': 'min'
            }

    @cherrypy.expose
    @cherrypy.tools.json_out()
    def bike_share(self, start_lat, start_lng, end_lat, end_lng, arrive_by=None):
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
        mid_point_1 = self.bixi_pods.find_nearest(start_point['lat'], start_point['lng'])
        mid_point_2 = self.bixi_pods.find_nearest(end_point['lat'], end_point['lng'])

        if arrive_by is None:
            arrive_by = calendar.timegm(datetime.now().timetuple())
        else:
            arrive_by = long(arrive_by)

        if mid_point_1 and mid_point_2:
            leg_3 = self.maps.p_walking('%s,%s' % (mid_point_2['lat'], mid_point_2['lng']),
                                     '%s,%s' % (end_lat, end_lng), arrival_time=arrive_by)
            leg_3_route = leg_3['routes'][0]
            leg_3_distance = leg_3_route['legs'][0]['distance']['value']
            leg_3_time = leg_3_route['legs'][0]['duration']['value'] / float(60)

            leg_2_arrive_by = arrive_by - leg_3_time
            leg_2 = self.maps.p_biking('%s,%s' % (mid_point_1['lat'], mid_point_1['lng']),
                                     '%s,%s' % (mid_point_2['lat'], mid_point_2['lng']), arrival_time=leg_2_arrive_by)
            leg_2_route = leg_2['routes'][0]
            leg_2_distance = leg_2_route['legs'][0]['distance']['value']

            model = BikeSpeedModel()
            model.create_user_features(mid_point_1, mid_point_2, alt=10)
            model.scale()
            leg_2_pred_speed = model.predict()
            leg_2_distance_km = leg_2_distance/float(1000)
            leg_2_time = leg_2_distance_km/leg_2_pred_speed * float(60)

            leg_1_arrive_by = leg_2_arrive_by - leg_2_time
            leg_1 = self.maps.p_walking('%s,%s' % (start_lat, start_lng),
                                        '%s,%s' % (mid_point_1['lat'], mid_point_1['lng']), arrival_time=leg_1_arrive_by)
            print leg_1
            leg_1_route = leg_1['routes'][0]
            leg_1_distance = leg_1_route['legs'][0]['distance']['value']
            leg_1_time = leg_1_route['legs'][0]['duration']['value'] / float(60)

            return {
                'waypoints': [
                    start_point,
                    mid_point_1,
                    mid_point_2,
                    end_point
                ],
                'legs': [
                    {
                        'start': start_point,
                        'end': mid_point_1,
                        'mode': 'walking',
                        'time': leg_1_time,
                        'distance': leg_1_distance / 1000.0
                    },
                    {
                        'start': mid_point_1,
                        'end': mid_point_2,
                        'mode': 'cycling',
                        'time': leg_2_time,
                        'speed': leg_2_pred_speed,
                        'distance': leg_2_distance_km
                    },
                    {
                        'start': mid_point_2,
                        'end': end_point,
                        'distance': leg_3_distance / 1000.0,
                        'time': leg_3_time,
                        'mode': 'walking'
                    }
                ],
                'time': leg_1_time + leg_2_time + leg_3_time,
                'unit': 'min'
            }

        else:
            leg_1 = self.maps.p_walking('%s,%s' % (start_lat, start_lng),
                                     '%s,%s' % (end_lat, end_lng), arrival_time=arrive_by)
            leg_1_route = leg_1['routes'][0]
            leg_1_distance = leg_1_route['legs'][0]['distance']['value'] / 1000.0
            leg_1_time = leg_1_route['legs'][0]['duration']['value'] / 60.0

            return {
                'waypoints': [
                    start_point,
                    end_point
                ],
                'legs': [
                    {
                        'distance': leg_1_distance,
                        'time': leg_1_time,
                        'mode': 'walking'
                    }
                ],
                'time': leg_1_time,
                'unit': 'min'
            }

    @cherrypy.expose
    @cherrypy.tools.json_out()
    def walk(self, start_lat, start_lng, end_lat, end_lng, arrive_by=None):
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

        if arrive_by is None:
            arrive_by = calendar.timegm(datetime.now().timetuple())
        else:
            arrive_by = long(arrive_by)

        leg_1 = self.maps.p_walking('%s,%s' % (start_lat, start_lng),
                                     '%s,%s' % (end_lat, end_lng), arrival_time=arrive_by)
        leg_1_route = leg_1['routes'][0]
        leg_1_distance = leg_1_route['legs'][0]['distance']['value'] / 1000.0
        leg_1_time = leg_1_route['legs'][0]['duration']['value'] / 60.0

        return {
            'waypoints': [
                start_point,
                end_point
            ],
            'legs': [
                {
                    'distance': leg_1_distance,
                    'time': leg_1_time,
                    'mode': 'walking'
                }
            ],
            'time': leg_1_time,
            'unit': 'min'
        }

    @cherrypy.expose
    @cherrypy.tools.json_out()
    def transit(self, start_lat, start_lng, end_lat, end_lng, arrive_by=None):
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

        if arrive_by is None:
            arrive_by = calendar.timegm(datetime.now().timetuple())
        else:
            arrive_by = long(arrive_by)

        leg_1 = self.maps.p_transit('%s,%s' % (start_lat, start_lng),
                                    '%s,%s' % (end_lat, end_lng), arrival_time=arrive_by)
        leg_1_route = leg_1['routes'][0]
        leg_1_distance = leg_1_route['legs'][0]['distance']['value'] / 1000.0
        leg_1_time = leg_1_route['legs'][0]['duration']['value'] / 60.0

        return {
            'waypoints': [
                start_point,
                end_point
            ],
            'legs': [
                {
                    'distance': leg_1_distance,
                    'time': leg_1_time,
                    'mode': 'transit'
                }
            ],
            'time': leg_1_time,
            'unit': 'min'
        }

    @cherrypy.expose
    @cherrypy.tools.json_out()
    def driving(self, start_lat, start_lng, end_lat, end_lng, arrive_by=None):
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

        if arrive_by is None:
            arrive_by = calendar.timegm(datetime.now().timetuple())
        else:
            arrive_by = long(arrive_by)

        leg_1 = self.maps.p_driving('%s,%s' % (start_lat, start_lng),
                                    '%s,%s' % (end_lat, end_lng), arrival_time=arrive_by)
        leg_1_route = leg_1['routes'][0]
        leg_1_distance = leg_1_route['legs'][0]['distance']['value'] / 1000.0
        leg_1_time = leg_1_route['legs'][0]['duration']['value'] / 60.0

        return {
            'waypoints': [
                start_point,
                end_point
            ],
            'legs': [
                {
                    'distance': leg_1_distance,
                    'time': leg_1_time,
                    'mode': 'driving'
                }
            ],
            'time': leg_1_time,
            'unit': 'min'
        }



