#!/usr/bin/env python
# encoding: utf-8

import cherrypy

from handler import Handler

def bootstrap():
    root_handler = Handler()
    cherrypy.tree.mount(root_handler)
    cherrypy.config.update({
        'server.socket_host': '0.0.0.0',
        'server.socket_port': 5000
    })
    cherrypy.engine.start()
    cherrypy.engine.block()


if __name__ == '__main__':
    bootstrap()