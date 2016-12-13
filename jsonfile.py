"""
jsonfile - incrementally write files in JSON format.
"""


import json


__version__ = "0.1"


class JsonWriter:
    def __init__(self, out):
        self.out = out

    def write_obj(self, obj):
        json.dump(obj, self.out)
