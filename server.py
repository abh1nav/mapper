#!/usr/bin/env python
# encoding: utf-8

import cherrypy

from maps import MapsProxy
from decision import Decision

class RootHandler(object):

    @cherrypy.expose
    @cherrypy.tools.json_out()
    def index(self):
        return {'status': 'ok', 'service': 'mapper'}

def bootstrap():
    root = RootHandler()
    proxy = MapsProxy()
    decision = Decision(proxy)

    cherrypy.tree.mount(root)
    cherrypy.tree.mount(proxy, '/proxy')
    cherrypy.tree.mount(decision, '/d')
    cherrypy.config.update({
        'server.socket_host': '0.0.0.0',
        'server.socket_port': 5000
    })
    cherrypy.engine.start()
    cherrypy.engine.block()


if __name__ == '__main__':
    bootstrap()