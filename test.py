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
    f.list_item(obj)

    remade = json.loads(out.getvalue())
    assert remade == obj


def test_write_nan():
    out = io.StringIO()
    f = jsonfile.JsonWriter(out)
    f.list_item(float('nan'))

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
