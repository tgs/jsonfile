"""
jsonfile - incrementally write files in JSON format.
"""


import json


__version__ = "0.1"


class JsonWriter:
    def __init__(self, out):
        self.out = out

    def _write_obj(self, obj):
        json.dump(obj, self.out)

    def write_list_start(self):
        self.out.write('[')
        self.pending_comma = ''

    def write_list_item(self, item):
        self.out.write(self.pending_comma)
        self._write_obj(item)
        self.pending_comma = ','

    def write_list_end(self):
        self.pending_comma = ''
        self.out.write(']')
