#!/usr/bin/env python
# encoding: utf-8

from datetime import datetime


class Cache(object):

    def __init__(self, default_expiry=3600):
        self.c = {}
        self.expiry = default_expiry

    def put(self, key, value, expiry=None):
        if expiry is None:
            expiry = self.expiry
        self.c[key] = (value, datetime.now(), expiry)
        return None

    def get(self, key):
        if key in self.c:
            value = self.c[key]
            expiry = value[2]
            expired = (datetime.now() - value[1]).seconds >= expiry
            if not expired:
                return value[0]
            else:
                return None