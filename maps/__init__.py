#!/usr/bin/env python
# encoding: utf-8

from datetime import datetime

import cherrypy
import requests

from cache import Cache
import conf

class MapsProxy(object):

    def __init__(self):
        self.cache = Cache()

    @cherrypy.expose
    @cherrypy.tools.json_out()
    def index(self):
        return {'status': 'ok', 'service': 'mapper/proxy'}

    def transform_maps_response(self, response):
        route = response['routes'][0]
        start_point = route['legs'][0]['start_location']
        end_point = route['legs'][-1]['end_location']
        distance = route['distance']
        duration = route['duration']

        pass

    def p_transit(self, src, tar, arrival_time=None, departure_time=None):
        if arrival_time is None and departure_time is None:
            return {
                'error': 'Either arrival_time or departure_time must be provided'
            }

        url = conf.transit_url % (src, tar)
        if arrival_time:
            url = '%s&arrival_time=%s' % (url, arrival_time)
        else:
            url = '%s&departure_time=%s' % (url, departure_time)

        cached = self.cache.get(url)
        if cached:
            return cached

        r = requests.get(url)
        if r.status_code == 200:
            j = r.json()
            for r in j['routes']:
                total = 0
                for l in r['legs']:
                    total += l['duration']['value']
                r['total_length'] = total
            self.cache.put(url, j)
            return j
        else:
            return r.json()


    def p_biking(self, src, tar, arrival_time=None, departure_time=None):
        if arrival_time is None and departure_time is None:
            return {
                'error': 'Either arrival_time or departure_time must be provided'
            }

        url = conf.bike_url % (src, tar)
        if arrival_time:
            url = '%s&arrival_time=%s' % (url, arrival_time)
        else:
            url = '%s&departure_time=%s' % (url, departure_time)

        cached = self.cache.get(url)
        if cached:
            return cached

        r = requests.get(url)
        if r.status_code == 200:
            j = r.json()
            for r in j['routes']:
                total = 0
                for l in r['legs']:
                    total += l['duration']['value']
                r['total_length'] = total
            self.cache.put(url, j)
            return j
        else:
            return r.json()

    def p_driving(self, src, tar, arrival_time=None, departure_time=None):
        if arrival_time is None and departure_time is None:
            return {
                'error': 'Either arrival_time or departure_time must be provided'
            }

        url = conf.driving_url % (src, tar)
        if arrival_time:
            url = '%s&arrival_time=%s' % (url, arrival_time)
        else:
            url = '%s&departure_time=%s' % (url, departure_time)

        cached = self.cache.get(url)
        if cached:
            return cached

        r = requests.get(url)
        if r.status_code == 200:
            j = r.json()
            for r in j['routes']:
                total = 0
                for l in r['legs']:
                    total += l['duration']['value']
                r['total_length'] = total
            self.cache.put(url, j)
            return j
        else:
            return r.json()

    def p_walking(self, src, tar, arrival_time=None, departure_time=None):
        if arrival_time is None and departure_time is None:
            return {
                'error': 'Either arrival_time or departure_time must be provided'
            }

        url = conf.walking_url % (src, tar)
        if arrival_time:
            url = '%s&arrival_time=%s' % (url, arrival_time)
        else:
            url = '%s&departure_time=%s' % (url, departure_time)

        cached = self.cache.get(url)
        if cached:
            return cached

        r = requests.get(url)
        if r.status_code == 200:
            j = r.json()
            for r in j['routes']:
                total = 0
                for l in r['legs']:
                    total += l['duration']['value']
                r['total_length'] = total
            self.cache.put(url, j)
            return j
        else:
            return r.json()

    @cherrypy.expose
    @cherrypy.tools.json_out()
    def transit(self, src, tar, arrival_time=None, departure_time=None):
        return self.p_transit(src, tar, arrival_time, departure_time)

    @cherrypy.expose
    @cherrypy.tools.json_out()
    def biking(self, src, tar, arrival_time=None, departure_time=None):
        return self.p_biking(src, tar, arrival_time, departure_time)

    @cherrypy.expose
    @cherrypy.tools.json_out()
    def driving(self, src, tar, arrival_time=None, departure_time=None):
        return self.p_driving(src, tar, arrival_time, departure_time)