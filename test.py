import io
import json
import math

from hypothesis import strategies as st, given

import jsonfile


# Generate lists and dicts with various values.
# See http://hypothesis.readthedocs.io/en/latest/data.html#recursive-data
json_objects = st.recursive(
    st.one_of(
        st.text(),
        st.floats().filter(lambda f: not math.isnan(f)),
        st.booleans(),
        st.none()),
    lambda children: st.one_of(
        st.lists(children),
        st.dictionaries(st.text(), children)))
# NaN: serializing and deserializing work fine, but it's a pain to compare
# containers for equality when they contain NaN.


@given(json_objects)
def test_write_obj(obj):
    out = io.StringIO()
    f = jsonfile.JsonWriter(out)
    f._write_obj(obj)

    remade = json.loads(out.getvalue())
    assert remade == obj


def test_write_nan():
    out = io.StringIO()
    f = jsonfile.JsonWriter(out)
    f._write_obj(float('nan'))

    remade = json.loads(out.getvalue())
    assert math.isnan(remade)


@given(st.lists(json_objects))
def test_list(objects):
    out = io.StringIO()
    with jsonfile.JsonList(out) as lst:
        for item in objects:
            lst.write_item(item)

    remade = json.loads(out.getvalue())
    assert remade == objects
