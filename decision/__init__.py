#!/usr/bin/env python
# encoding: utf-8

import cherrypy

class Decision(object):

    def __init__(self):
        pass

    @cherrypy.expose
    @cherrypy.tools.json_out()
    def index(self):
        return {'status': 'ok', 'service': 'mapper/d'}

    @cherrypy.expose
    @cherrypy.tools.json_out()
    def bike_owner(self, start_loc, end_loc, arrive_by=None):
        return {'error': 'not yet implemented'}
