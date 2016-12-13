import io
import json

from hypothesis import strategies as st, given

import jsonfile


@given(st.text())
def test_write_obj(obj):
    out = io.StringIO()
    f = jsonfile.JsonWriter(out)
    f.write_obj(obj)
    assert json.loads(out.getvalue()) == obj
