#!/usr/bin/env python
# encoding: utf-8

base_url = 'http://maps.googleapis.com/maps/api/directions/json?units=metric&origin=%s&destination=%s'
transit_url = '%s&mode=transit' % base_url
bike_url = '%s&mode=bicycling' % base_url
driving_url = '%s&mode=driving' % base_url
walking_url = '%s&mode=walking' % base_url

elevation_url = 'http://maps.googleapis.com/maps/api/elevation/json?locations=%s'