"""
jsonfile - incrementally write files in JSON format.
"""


import json
import enum


__version__ = "0.1"


@enum.unique
class State(enum.Enum):
    Nothing = (0, '')

    ListStart = (1, '')
    List = (2, ', ')

    DictStart = (3, '')
    Dict = (4, ', ')

    def __init__(self, _, prefix):
        self.prefix = prefix


class JsonWriter:
    def __init__(self, out):
        self.out = out
        self.context = [State.Nothing]

    def write_pending_separator(self):
        self.out.write(self.top_state.prefix)
        # TODO: make pretty
        if self.top_state == State.ListStart:
            self.context[-1] = State.List
        if self.top_state == State.DictStart:
            self.context[-1] = State.Dict

    def start_list(self):
        self.write_pending_separator()
        self.out.write('[')
        self.context.append(State.ListStart)

    def list_item(self, item):
        assert self.top_state in (State.List, State.ListStart, State.Nothing)
        self.write_pending_separator()
        json.dump(item, self.out)

    def end_list(self):
        last_state = self.context.pop()
        assert last_state in (State.List, State.ListStart)
        self.out.write(']')

    def start_dict(self):
        self.write_pending_separator()
        self.out.write('{')
        self.context.append(State.DictStart)

    def dict_item(self, key, value):
        assert self.top_state in (State.Dict, State.DictStart)
        self.write_pending_separator()
        json.dump(key, self.out)
        self.out.write(': ')
        json.dump(value, self.out)

    def end_dict(self):
        last_state = self.context.pop()
        assert last_state in (State.Dict, State.DictStart)
        self.out.write('}')

    @property
    def top_state(self):
        return self.context[-1]
