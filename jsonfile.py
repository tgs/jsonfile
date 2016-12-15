"""
jsonfile - incrementally write files in JSON format.
"""


import json
import enum


__version__ = "0.1"


@enum.unique
class State(enum.Enum):
    List = ('', ',', 'List', ']')
    ListStart = ('[', '', 'List', ']')

    DictBeforeKey = ('', ',', 'DictBeforeValue', '}')
    DictBeforeValue = ('', ':', 'DictBeforeKey', NotImplemented)
    DictStart = ('{', '', 'DictBeforeValue', '}')

    TopLevel = ('', '', 'ExtraTopLevel', '')
    ExtraTopLevel = ('', NotImplemented, 'ExtraTopLevel', '')

    def __init__(self, on_enter, before_item, state_on_item_str, on_exit):
        self.on_enter = on_enter
        self.before_item = before_item
        self.state_on_item_str = state_on_item_str
        self.on_exit = on_exit

    @property
    def state_on_item(self):
        return type(self)[self.state_on_item_str]


class JsonWriter:
    def __init__(self, out):
        self.out = out
        self.context = [State.TopLevel]

    def _before_item(self):
        self.out.write(self.top_state.before_item)
        self.swap_state(self.top_state.state_on_item)

    def _start_container(self, state):
        self.out.write(state.on_enter)
        self.push_state(state)

    def start_list(self):
        self._before_item()
        self._start_container(State.ListStart)

    def list_item(self, item):
        assert self.top_state in (State.List, State.ListStart, State.TopLevel)
        self._before_item()
        json.dump(item, self.out)

    def end_container(self):
        last_state = self.context.pop()
        self.out.write(last_state.on_exit)

    def end_list(self):
        assert self.top_state in (State.List, State.ListStart)
        self.end_container()

    def start_dict(self):
        self._before_item()
        self._start_container(State.DictStart)

    def dict_item(self, key, value):
        assert self.top_state in (State.DictStart, State.DictBeforeKey)
        self._before_item()
        json.dump(key, self.out)
        self._before_item()
        json.dump(value, self.out)

    def dict_key(self, key):
        assert self.top_state in (State.DictStart, State.DictBeforeKey)
        self._before_item()
        json.dump(key, self.out)

    def dict_value(self, value):
        assert self.top_state == State.DictBeforeValue
        self._before_item()
        json.dump(value, self.out)

    def end_dict(self):
        self.end_container()

    @property
    def top_state(self):
        return self.context[-1]

    def swap_state(self, new_state):
        self.context[-1] = new_state

    def push_state(self, new_state):
        self.context.append(new_state)
