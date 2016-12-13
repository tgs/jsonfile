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

    def list(self):
        return JsonList(self.out)


class JsonList:
    def __init__(self, out):
        self.out = out
        self.started = False
        self.entered = False

    def __enter__(self):
        self.out.write('[')
        self.entered = True
        return self

    def write_item(self, item):
        assert self.entered

        if self.started:
            self.out.write(',')
        self.started = True

        json.dump(item, self.out)

    def __exit__(self, etype, evalue, etraceback):
        self.out.write(']')
        self.entered = False
