"""
jsonfile - incrementally write files in JSON format.
"""


import json
import enum
from functools import partial, update_wrapper


__version__ = "1.0.1"


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

# Add 'can_consume' or something, and put the pending comma on the stack, rather
# than as a new type of state?
# on_exit would become fancy, to say "pop another one after me"?
#
#
# That sounds like a pain in the butt.



# How could that state enum get generated automatically or be implicit in some code?
#
#
# At the moment, this is only smart enough to deal with 'end_container' closing the *top*
# of the stack.  If it weren't, then you could deal with the comma-separation and the start/end container separately?

# push comma-separation onto stack and THEN start/end list?  start/end list doesn't handle normal items, passes them on.
# comma-separation does handle them.  start/end list handles start/end list messages, pops TWO.
#
#


# what if it yields formatters?
def listof(what):
    yield literal('[')
    yield commaseparated(what)
    yield literal(']')


def commaseparated(what):
    first = yield what | nothing
    if first is not None:
        yield (literal(',') + what).many()



class JsonProto:
    """
    Incrementally generate a file in JSON format.
    """
    def __init__(self):
        """
        """
        self.context = [State.TopLevel]

    def _before_item(self):
        old = self.swap_state(self.top_state.state_on_item)
        return old.before_item

    def _start_container(self, state):
        self.push_state(state)
        return state.on_enter

    def start_list(self):
        return (
            self._before_item() +
            self._start_container(State.ListStart)
        )

    def toplevel_item(self, item):
        """
        If your file only contains one item, why are using this library?

        But in any case, you can write one item using this.
        """
        assert self.top_state == State.TopLevel
        return self._any_item(item)

    def _any_item(self, item):
        return (
            self._before_item() +
            json.dumps(item)
        )

    def list_item(self, item):
        assert self.top_state in (State.List, State.ListStart)
        return self._any_item(item)

    def _end_container(self):
        return self.context.pop().on_exit

    def end_list(self):
        assert self.top_state in (State.List, State.ListStart)
        return self._end_container()

    def start_dict(self):
        return (
            self._before_item() +
            self._start_container(State.DictStart)
        )

    def dict_item(self, key, value):
        assert self.top_state in (State.DictStart, State.DictBeforeKey)
        return (self.dict_key(key) + self.dict_value(value))

    def dict_key(self, key):
        assert self.top_state in (State.DictStart, State.DictBeforeKey)
        return self._any_item(key)

    def dict_value(self, value):
        assert self.top_state == State.DictBeforeValue
        return self._any_item(value)

    def end_dict(self):
        assert self.top_state in (State.DictBeforeKey, State.DictStart)
        return self._end_container()

    @property
    def top_state(self):
        return self.context[-1]

    def swap_state(self, new_state):
        old = self.top_state
        self.context[-1] = new_state
        return old

    def push_state(self, new_state):
        self.context.append(new_state)

    @property
    def done(self):
        return len(self.context) == 1

    def finish_all(self):
        parts = []
        while not self.done:
            parts.append(self._end_container())
        return ''.join(parts)


class JsonWriter:
    def __init__(self, out):
        self.protocol = JsonProto()
        self.out = out

    def _write_proto_result(self, method, *args, **kwargs):
        result = method(*args, **kwargs)
        assert type(result) is str
        self.out.write(result)

    def __getattr__(self, name):
        value = getattr(self.protocol, name)
        if callable(value):
            writer = partial(self._write_proto_result, value)
            update_wrapper(writer, value)
            return writer
        else:
            return value
