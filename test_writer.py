import io
import json
import math

from hypothesis import strategies as st, given, note

import jsonfile


# Generate lists and dicts with various values.
# See http://hypothesis.readthedocs.io/en/latest/data.html#recursive-data
json_objects = st.recursive(
    st.one_of(
        st.text(max_size=30),
        st.floats().filter(lambda f: not math.isnan(f)),
        st.booleans(),
        st.none()),
    lambda children: st.one_of(
        st.lists(children, max_size=30),
        st.dictionaries(st.text(), children, max_size=30)),
    max_leaves=15)
# NaN: serializing and deserializing work fine, but it's a pain to compare
# containers for equality when they contain NaN.


@given(json_objects)
def test_write_obj(obj):
    out = io.StringIO()
    f = jsonfile.JsonWriter(out)
    f.toplevel_item(obj)

    remade = json.loads(out.getvalue())
    assert remade == obj


def test_write_nan():
    out = io.StringIO()
    f = jsonfile.JsonWriter(out)
    f.toplevel_item(float('nan'))

    remade = json.loads(out.getvalue())
    assert math.isnan(remade)


@given(st.lists(json_objects, max_size=5))
def test_list_raw(objects):
    out = io.StringIO()
    f = jsonfile.JsonWriter(out)
    f.start_list()

    for item in objects:
        f.list_item(item)

    f.end_list()

    remade = json.loads(out.getvalue())
    assert remade == objects


@given(st.lists(json_objects, max_size=5))
def test_nested_list(objects):
    out = io.StringIO()
    f = jsonfile.JsonWriter(out)
    f.start_list()

    for item in objects:
        if isinstance(item, list):
            f.start_list()
            for item2 in item:
                f.list_item(item2)
            f.end_list()
        else:
            f.list_item(item)

    f.end_list()

    serialized = out.getvalue()
    note(serialized)
    remade = json.loads(serialized)
    assert remade == objects


@given(st.dictionaries(st.text(max_size=5), json_objects, max_size=5))
def test_dict_raw(objects):
    out = io.StringIO()
    f = jsonfile.JsonWriter(out)
    f.start_dict()

    for item in objects.items():
        f.dict_item(*item)

    f.end_dict()

    serialized = out.getvalue()
    note(serialized)
    remade = json.loads(serialized)
    assert remade == objects


@given(st.dictionaries(st.text(max_size=5), json_objects, max_size=5))
def test_dict_piecemeal(objects):
    out = io.StringIO()
    f = jsonfile.JsonWriter(out)
    f.start_dict()

    for k, v in objects.items():
        f.dict_key(k)
        f.dict_value(v)

    f.end_dict()

    serialized = out.getvalue()
    note(serialized)
    remade = json.loads(serialized)
    assert remade == objects


def test_finish_all():
    out = io.StringIO()
    f = jsonfile.JsonWriter(out)
    f.start_dict()
    f.dict_key('things')
    f.start_list()
    f.list_item('toothbrushes')
    f.list_item('microphones')
    f.finish_all()

    serialized = out.getvalue()
    print(serialized)
    remade = json.loads(serialized)
    assert remade == {
        'things': ['toothbrushes', 'microphones']
    }


def write_list_item(f, item):
    f.list_item(item)


def write_dict_key(f, item):
    f.dict_key(item)


def write_dict_value(f, item):
    if isinstance(item, list):
        write_list(f, item)
    elif isinstance(item, dict):
        write_dict(f, item)
    else:
        f.dict_value(item)


def write_list(f, items):
    f.start_list()
    for item in items:
        write_list_item(f, item)
    f.end_list()


def write_dict(f, items):
    f.start_dict()
    for k,v in items.items():
        write_dict_key(f, k)
        write_dict_value(f, v)
    f.end_dict()


def write_toplevel(f, item):
    if isinstance(item, list):
        write_list(f, item)
    elif isinstance(item, dict):
        write_dict(f, item)
    else:
        f.toplevel_item(item)


@given(json_objects)
def test_recursive_writes(obj):
    out = io.StringIO()
    f = jsonfile.JsonWriter(out)
    write_toplevel(f, obj)

    serialized = out.getvalue()
    note(serialized)
    remade = json.loads(serialized)
    assert remade == obj


# TODO: how to test whether it's possible to make invalid JSON?
# (it's currently possible, since you can make a list into a dict key)
