jsonfile - incrementally generate JSON

Incrementally means that, in most places, you can either send in a complete Python
object, or build it a piece at a time.  For example, let's build the JSON structure
``[3, {"cool": true, "awesome": [1,2,3,4,5]}]``::

        >>> import jsonfile
        >>> jp = jsonfile.JsonProto()
        >>> jp.start_list()
        '['
        >>> jp.list_item(3)
        '3'
        >>> jp.start_dict()
        ',{'
        >>> jp.dict_item('cool', True)
        '"cool":true'
        >>> jp.dict_key('awesome')
        ',"awesome"'
        >>> jp.dict_value([1,2,3,4,5])
        ':[1, 2, 3, 4, 5]'
        >>> jp.finish_all()
        '}]'

That used the ``JsonProto`` object, a *sans-io* version that just returns the
text that you should write to your output.  If you are writing to a file in a
normal synchronous context, you could also use the ``JsonWriter`` object, it
will be slightly more convenient::

        >>> import io
        >>> dest = io.StringIO()
        >>> import jsonfile
        >>> jw = jsonfile.JsonWriter(dest)
        >>> jw.start_list()
        >>> jw.list_item(3)
        >>> jw.list_item({'things': 'stuff'})
        >>> jw.start_dict()
        >>> jw.dict_item('cool', True)
        >>> jw.dict_key('awesome')
        >>> jw.dict_value([1,2,3,4,5])
        >>> jw.finish_all()
        >>> dest.getvalue()
        '[3,{"things": "stuff"},{"cool":true,"awesome":[1, 2, 3, 4, 5]}]'


Because the underlying ``JsonProto`` doesn't do IO, it should be easy to make a
version of ``JsonWriter`` that works well in an async context.

Many kinds of errors are caught: having more than one object at the root level
of a file, using a list item in a dictionary, etc.

TODO:

- Allow specifying your own JSONEncoder to use on complete objects.
- Do indentation.
- Implement an ``AsyncJsonWriter``
- Better tests for preventing illegal JSON from being generated (e.g. lists as
  keys).
- Python 2 support?
