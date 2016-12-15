import io
import json
import math

import pytest
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
    jp = jsonfile.JsonProto()
    remade = json.loads(jp.toplevel_item(obj))
    assert remade == obj


def test_write_nan():
    jp = jsonfile.JsonProto()
    remade = json.loads(jp.toplevel_item(float('nan')))
    assert math.isnan(remade)


@given(st.lists(json_objects, max_size=5))
def test_list_raw(objects):
    out = io.StringIO()
    jp = jsonfile.JsonProto()
    out.write(jp.start_list())

    for item in objects:
        out.write(jp.list_item(item))

    out.write(jp.end_list())

    remade = json.loads(out.getvalue())
    assert remade == objects


@given(st.lists(json_objects, max_size=5))
def test_nested_list(objects):
    out = io.StringIO()
    jw = jsonfile.JsonWriter(out)
    jw.start_list()

    for item in objects:
        if isinstance(item, list):
            jw.start_list()
            for item2 in item:
                jw.list_item(item2)
            jw.end_list()
        else:
            jw.list_item(item)

    jw.end_list()

    serialized = out.getvalue()
    note(serialized)
    remade = json.loads(serialized)
    assert remade == objects


@given(st.dictionaries(st.text(max_size=5), json_objects, max_size=5))
def test_dict_raw(objects):
    out = io.StringIO()
    jp = jsonfile.JsonProto()
    out.write(jp.start_dict())

    for item in objects.items():
        out.write(jp.dict_item(*item))

    out.write(jp.end_dict())

    serialized = out.getvalue()
    note(serialized)
    remade = json.loads(serialized)
    assert remade == objects


@given(st.dictionaries(st.text(max_size=5), json_objects, max_size=5))
def test_dict_piecemeal(objects):
    out = io.StringIO()
    jp = jsonfile.JsonProto()
    out.write(jp.start_dict())

    for k, v in objects.items():
        out.write(jp.dict_key(k))
        out.write(jp.dict_value(v))

    out.write(jp.end_dict())

    serialized = out.getvalue()
    note(serialized)
    remade = json.loads(serialized)
    assert remade == objects


def test_finish_all():
    out = io.StringIO()
    jw = jsonfile.JsonWriter(out)
    jw.start_dict()
    jw.dict_key('things')
    jw.start_list()
    jw.list_item('toothbrushes')
    jw.list_item('microphones')
    jw.finish_all()

    serialized = out.getvalue()
    print(serialized)
    remade = json.loads(serialized)
    assert remade == {
        'things': ['toothbrushes', 'microphones']
    }


def write_list_item(jw, item):
    if isinstance(item, list):
        write_list(jw, item)
    elif isinstance(item, dict):
        write_dict(jw, item)
    else:
        jw.list_item(item)


def write_dict_key(jw, item):
    jw.dict_key(item)


def write_dict_value(jw, item):
    if isinstance(item, list):
        write_list(jw, item)
    elif isinstance(item, dict):
        write_dict(jw, item)
    else:
        jw.dict_value(item)


def write_list(jw, items):
    jw.start_list()
    for item in items:
        write_list_item(jw, item)
    jw.end_list()


def write_dict(jw, items):
    jw.start_dict()
    for k,v in items.items():
        write_dict_key(jw, k)
        write_dict_value(jw, v)
    jw.end_dict()


def write_toplevel(jw, item):
    if isinstance(item, list):
        write_list(jw, item)
    elif isinstance(item, dict):
        write_dict(jw, item)
    else:
        jw.toplevel_item(item)


@given(json_objects)
def test_recursive_writes(obj):
    out = io.StringIO()
    jw = jsonfile.JsonWriter(out)
    write_toplevel(jw, obj)

    serialized = out.getvalue()
    note(serialized)
    remade = json.loads(serialized)
    assert remade == obj


def test_two_top_level_items():
    jp = jsonfile.JsonProto()
    jp.start_list()
    jp.end_list()
    with pytest.raises(Exception):
        jp.start_list()


def test_list_item_in_dict():
    jp = jsonfile.JsonProto()
    jp.start_list()
    with pytest.raises(Exception):
        jp.dict_key('asdf')

# TODO: how to test whether it's possible to make invalid JSON?
# (it's currently possible, since you can make a list into a dict key)
