**************************************************************************************
One-file utility module filled with helper functions for day to day Python programming
***************************************************************************************

This is a subset of batbelt, with only the most used features, packed in a tiny file, and Python 2.7/3.3 compatible.

So, while you can `pip install minibelt`, you may just drop it in your project and forget about it.

It's under zlib licence.


Get this nest value or a default
=================================

You had a get() method on dict, but not on lists or tuple. Now you do ::

    >>> lst = range(10)
    >>> get(lst, 1, default='whatever_you_want')
    1
    >>> get(lst, 100, default='whatever_you_want')
    'whatever_you_want'

Plus, you can chain look ups :

This::

    try:
        res = data['key'][0]['other key'][1]
    except (KeyError, IndexError):
        res = "value"


Becomes::

    get(data, 'key', 0, 'other key, 1, default="value")


And for attributes... ::

    devise = attr(car, 'insurance', 'expiration_date', 'timezone')


Iteration tools missing in itertools
===================================================================================


Iteration by chunk or with a sliding window::

    >>> for chunk in chunks(l, 3):
    ...     print list(chunk)
    ...
    [0, 1, 2]
    [3, 4, 5]
    [6, 7, 8]
    [9]
    >>> for slide in window(l, 3):
    ...     print list(slide)
    ...
    [0, 1, 2]
    [1, 2, 3]
    [2, 3, 4]
    [3, 4, 5]
    [4, 5, 6]
    [5, 6, 7]
    [6, 7, 8]
    [7, 8, 9]


Get the first element an any iterable (not just indexable) or the first one to be True::

    >>> first(xrange(10))
    0
    >>> first_true(xrange(10))
    1
    >>> first([], default="What the one thing we say to the God of Death ?")
    'What the one thing we say to the God of Death ?'

You can decide what "True" means by passing a function with the `key` parameter.

Sorted Set
===================================================================================

Slow but useful data structure::

    >>> for x in sset((3, 2, 2, 2, 1, 2)):
    ...     print x
    ...
    3
    2
    1


Dictionaries one liners
===================================================================================


I wish '+'' was overloaded for dicts::

    >>> dmerge({"a": 1, "b": 2}, {"b": 2, "c": 3})
    {'a': 1, 'c': 3, 'b': 2}


Sometimes you do not want to simply overwrite the values inside the original dict, but merge them in custom fashion::

    >>> def my_merge(v1, v2):
    ...     if isinstance(v1, dict) and isinstance(v2, dict):
    ...         return dmerge(v1, v2)
    ...     return v2
    >>> dmerge({"a": 1, "b": {'ok': 5}}, {"b": {'ko': 5 }, "c": 3}, my_merge)
    {'a': 1, 'c': 3, 'b': {'ko': 5, 'ok': 5}}


And for lazy people like me ::

    >>> subdict({'a': 1, 'b': 2, 'c': 3}, include=('a', 'b'))
    {'a': 1, 'b': 2}
    >>> subdict({'a': 1, 'b': 2, 'c': 3}, exclude=('c',))
    {'a': 1, 'b': 2}


Which is quite nice when you want a dict of some local variables (like in web framework functions returning responses such as Django, Flask or Bottle) ::


    >>> def test():
    ...     a, b, c, d, e = range(5)
    ...     return subdict(locals(), exclude=('d', 'd'))
    ...
    >>> test()
    {'a': 0, 'c': 2, 'b': 1, 'e': 4}


String tools
===================================================================================

String normalization ::

    >>> normalize(u"Hélo Whorde")
    'Helo Whorde'

The mandatory "slufigy"::

    >>> slugify(u"Hélo Whorde")
    helo-whorde

You get better slugification if you install the `unidecode` lib, but it's optional. You can specify `separator` if you don't like `-` or call directly `normalize()` (the underlying function) if you wish more control.

JSON helpers that handle date/time ::

    >>> import datetime
    >>> json_dumps({'test': datetime.datetime(2000, 1, 1, 1, 1, 1)})
    '{"test": "2000-01-01 01:01:01.000000"}'
    >>> json_dumps({'test': datetime.date(2000, 1, 1)})
    '{"test": "2000-01-01"}'
    >>> json_dumps({'test': datetime.time(1, 1, 1)})
    '{"test": "01:01:01.000000"}'
    >>> json_dumps({'test': datetime.timedelta(1, 1)})
    '{"test": "timedelta(seconds=\'86401.0\')"}'
    >>> json_dumps({u'test': datetime.timedelta(1, 1), u'a': [1, 2]})
    '{"test": "timedelta(seconds=\'86401.0\')", "a": [1, 2]}'

    >>> json_loads('{"test": "2000-01-01 01:01:01.000000"}')
    {u'test': datetime.datetime(2000, 1, 1, 1, 1, 1)}
    >>> json_loads('{"test": "2000-01-01"}')
    {u'test': datetime.date(2000, 1, 1)}
    >>> json_loads('{"test": "01:01:01.000000"}')
    {u'test': datetime.time(1, 1, 1)}
    >>> json_loads('{"test": "timedelta(seconds=\'86401.0\')"}')
    {u'test': datetime.timedelta(1, 1)}
    >>> json_loads('{"test": "timedelta(seconds=\'86401.0\')", "a": [1, 2]}')
    {u'test': datetime.timedelta(1, 1), u'a': [1, 2]}



Import this
===================================================================================


`__import__` is weird. Let's abstract that ::

    YourClass = import_from_path('foo.bar.YourClass')
    obj = YourClass()



Add a any directory to the PYTHON PATH
===========================================

Accepts shell variables and relative paths :

    add_to_pythonpath("~/..")

You can (and probably wants) specify a starting point if you pass a relative path. The default starting point is the result is `os.getcwd()` while you probably wants the directory containing you script. To to so, pass `__file__`:

    add_to_pythonpath("../..", starting_point=__file__)

`starting_point` can be a file path (basename will be stripped) or a directory name. It will be from there that the relative path will be calculated.

You can also choose where in the `sys.path` list your path will be added by passing `insertion_index`, which default to after the last existing item.



To timestamp
=============

datetime.fromtimestamp exists but not the other away around, and it's not likely to change anytime soon (see: http://bugs.python.org/issue2736). In the meantime::

    >>> from datetime import datetime
    >>> to_timestamp(datetime(2000, 1, 1, 2, 1, 1))
    946692061
    >>> datetime.fromtimestamp(946688461) # PYTHON, Y U NO HAZ TO_TIMESTAMP ?
    datetime.datetime(2000, 1, 1, 2, 1, 1)


Removing duplicates
====================

skip_duplicates returns a generator that will yield all objects from an iterable, skipping
duplicates and preserving order ::

    >>> list(skip_duplicates([1, 2, 3, 4, 4, 2, 1, 3 , 4]))
    [1, 2, 3, 4]

Duplicates are identified using the `key` function to calculate a
unique fingerprint. This does not use natural equality, but the
result use a set() to remove duplicates, so defining __eq__
on your objects would have no effect.

By default the fingerprint is the object itself,
which ensure the functions works as-is with iterable of primitives
such as int, str or tuple.

The return value of `key` MUST be hashable, which means for
non hashable objects such as dict, set or list, you need to specify
a a function that returns a hashable fingerprint ::


    >>> list(skip_duplicates(([], [], (), [1, 2], (1, 2)), lambda x: tuple(x)))
    [[], [1, 2]]
    >>> list(skip_duplicates(([], [], (), [1, 2], (1, 2)), lambda x: (type(x), tuple(x))))
    [[], (), [1, 2], (1, 2)]

