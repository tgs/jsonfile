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
