#!/usr/bin/env python
# encoding: utf-8

from math import radians, cos, sin, asin, sqrt

from pymongo import MongoClient


class BikePosts(object):

    def __init__(self):
        self.conn = MongoClient('mongo1.x.crowdriff.com')
        self.src = self.conn['geocodes']['bike_posts']

    def _haversine(self, lon1, lat1, lon2, lat2):
        """ Calculate the great circle distance between two points on the earth (specified in decimal degrees) """
        lo1, la1, lo2, la2 = map(radians, [lon1, lat1, lon2, lat2])
        # haversine formula
        dlon = lo2 - lo1
        dlat = la2 - la1
        a = sin(dlat / 2) ** 2 + cos(la1) * cos(la2) * sin(dlon / 2) ** 2
        c = 2 * asin(sqrt(a))
        km = 6367 * c
        return km

    def find_nearest(self, lat, lng, radius=1.0):
        cursor = self.src.find({
            'loc': {
                '$geoWithin': {
                    '$centerSphere': [[lng, lat], radius/6371.39]
                }
            }
        })

        results = []
        for doc in cursor:
            results.append(doc)

        if len(results) > 0:
            for r in results:
                diff = self._haversine(lng, lat, r['loc']['coordinates'][0], r['loc']['coordinates'][1])
                r['distance'] = diff

            nearest = sorted(results, key=lambda r: r['distance'])[0]
            return { 'lat': nearest['loc']['coordinates'][1], 'lng': nearest['loc']['coordinates'][0] }