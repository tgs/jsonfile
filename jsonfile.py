"""
jsonfile - incrementally write files in JSON format.
"""


import json
import enum


__version__ = "0.1"


@enum.unique
class State(enum.Enum):
    ListStart = 1
    List = 2


class JsonWriter:
    def __init__(self, out):
        self.out = out
        self.context = [None]

    def _write_obj(self, obj):
        json.dump(obj, self.out)

    def write_pending_separator(self):
        if self.top_state == State.List:
            self.out.write(',')
        elif self.top_state == State.ListStart:
            self.context[-1] = State.List

    def write_list_start(self):
        self.write_pending_separator()
        self.out.write('[')
        self.context.append(State.ListStart)

    def write_list_item(self, item):
        self.write_pending_separator()
        self._write_obj(item)

    def write_list_end(self):
        last_state = self.context.pop()
        assert last_state in (State.List, State.ListStart)
        self.out.write(']')

    @property
    def top_state(self):
        return self.context[-1]
