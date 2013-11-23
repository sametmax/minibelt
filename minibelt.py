# -*- coding: utf-8 -*-

"""
One-file utility module filled with helper functions for day to day Python
programming

This is a subset of batbelt, with only the most used features, packed in a tiny
file so you can just drop it in your project and forget about it.

It's under zlib licence.

"""

from __future__ import unicode_literals


import os
import re
import sys
import json
import unicodedata
import codecs

from itertools import islice, chain
from collections import MutableSet, deque
from datetime import datetime, timedelta, date, time


__version__ = '0.1.1'

__all__ = [
'slugify', 'normalize', 'json_dumps', 'json_loads', 'CLASSIC_DATETIME_FORMAT',
'to_timestamp', 'import_from_path', 'attr', 'chunks', 'window', 'dmerge',
'get', 'subdict', 'iget', 'skip_duplicates', 'sset', 'unpack',
'add_to_pythonpath', 'write', 'flatten'
]

CLASSIC_DATETIME_FORMAT = '%Y-%m-%d %H:%M:%S.%f'
CLASSIC_DATETIME_PATTERN = r'\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}\.\d{6}'

# for P3K compat
try:
    unicode
except NameError:
    unicode = str
    xrange = range

try:
    import unidecode

    def slugify(string, separator=r'-'):
        r"""
        Slugify a unicode string using unidecode to normalize the string.

        :Example:

            >>> slugify(u"H\xe9ll\xf8 W\xc3\xb6rld")
            'hello-world'
            >>> slugify("Bonjour, tout l'monde !", separator="_")
            'bonjour_tout_lmonde'
            >>> slugify("\tStuff with -- dashes and...   spaces   \n")
            'stuff-with-dashes-and-spaces'
        """
        string = normalize(string)
        string = re.sub(r'[^\w\s' + separator + ']', '',  string, flags=re.U)
        string = string.strip().lower()
        return re.sub(r'[' + separator + '\s]+', separator, string, flags=re.U)


    def normalize(string):
        r"""
            Returns a new string withou non ASCII characters, trying to replace
            them with their ASCII closest counter parts when possible.

            :Example:

                >>> normalize(u"H\xe9ll\xf8 W\xc3\xb6rld")
                'Hello World'

            This version use unidecode and provide enhanced results.
        """
        return unidecode.unidecode(string).decode('ascii')


except ImportError:

    def normalize(string):
        r"""
            Returns a new string withou non ASCII characters, trying to replace
            them with their ASCII closest counter parts when possible.

            :Example:

                >>> normalize(u"H\xe9ll\xf8 W\xc3\xb6rld")
                'Hell World'


            This version use unicodedata and provide limited yet
            useful results.
        """
        string = unicodedata.normalize('NFKD', string).encode('ascii', 'ignore')
        return string.decode('ascii')


    def slugify(string, separator=r'-'):
        r"""
        Slugify a unicode string using unicodedata to normalize the string.

        :Example:

            >>> slugify(u"H\xe9ll\xf8 W\xc3\xb6rld")
            'hell-world'
            >>> slugify("Bonjour, tout l'monde !", separator="_")
            'bonjour_tout_lmonde'
            >>> slugify("\tStuff with -- dashes and...   spaces   \n")
            'stuff-with-dashes-and-spaces'
        """

        string = normalize(string)
        string = re.sub(r'[^\w\s' + separator + ']', '', string, flags=re.U)
        string = string.strip().lower()
        return re.sub(r'[' + separator + '\s]+', separator, string, flags=re.U)



class JSONEncoder(json.JSONEncoder):
    """
        Json encoder with date and time handling.

        You should use naive datetime only. If you have timezone information,
        store them in a separate field.
    """

    DATETIME_FORMAT = CLASSIC_DATETIME_FORMAT
    DATE_FORMAT, TIME_FORMAT = DATETIME_FORMAT.split()
    TIMEDELTA_FORMAT = "timedelta(seconds='%s')"


    def __init__(self, datetime_format=None, date_format=None, time_format=None,
                timedelta_format=None, *args, **kwargs):

        self.datetime_format = datetime_format or self.DATETIME_FORMAT
        self.date_format = date_format or self.DATE_FORMAT
        self.time_format = time_format or self.TIME_FORMAT
        self.timedelta_format = timedelta_format or self.TIMEDELTA_FORMAT

        super(JSONEncoder, self).__init__(self, *args, **kwargs)


    def default(self, obj):

        if isinstance(obj, datetime):
            return obj.strftime(self.datetime_format)

        if isinstance(obj, date):
            return obj.strftime(self.date_format)

        if isinstance(obj, time):
            return obj.strftime(self.time_format)

        if isinstance(obj, timedelta):
            return self.timedelta_format % obj.total_seconds()

        return json.JSONEncoder.default(self, obj)


class JSONDecoder(json.JSONDecoder):
    """
        Json decoder that decode JSON encoded with JSONEncoder
    """

    DATETIME_PATTERN = CLASSIC_DATETIME_PATTERN
    DATE_PATTERN, TIME_PATTERN = DATETIME_PATTERN.split()
    TIMEDELTA_PATTERN = r"timedelta\(seconds='(?P<seconds>\d+(?:\.\d+)*)'\)"


    def __init__(self, datetime_pattern=None, date_pattern=None,
                time_pattern=None, timedelta_pattern=None, datetime_format=None,
                date_format=None, time_format=None, *args, **kwargs):

        self.datetime_format = datetime_format or JSONEncoder.DATETIME_FORMAT
        self.date_format = date_format or JSONEncoder.DATE_FORMAT
        self.time_format = time_format or JSONEncoder.TIME_FORMAT

        self.datetime_pattern = re.compile(datetime_pattern or self.DATETIME_PATTERN)
        self.date_pattern = re.compile(date_pattern or self.DATE_PATTERN)
        self.time_pattern = re.compile(time_pattern or self.TIME_PATTERN)
        self.timedelta_pattern = re.compile(timedelta_pattern or self.TIMEDELTA_PATTERN)

        super(JSONDecoder, self).__init__(object_pairs_hook=self.object_pairs_hook,
                                          *args, **kwargs)

    def object_pairs_hook(self, obj):
        return dict((k, self.decode_on_match(v)) for k, v in obj)


    def decode_on_match(self, obj):
        """
            Try to match the string, and if it fits any date format,
            parse it and returns a Python object.
        """

        string = unicode(obj)

        match = re.search(self.datetime_pattern, string)
        if match:
            return datetime.strptime(match.string, self.datetime_format)

        match = re.search(self.date_pattern, string)
        if match:
            return datetime.strptime(match.string, self.date_format).date()

        match = re.search(self.time_pattern, string)
        if match:
            return datetime.strptime(match.string, self.time_format).time()

        match = re.search(self.timedelta_pattern, string)
        if match:
            return timedelta(seconds=float(match.groupdict()['seconds']))

        return obj


def json_dumps(data, datetime_format=None, date_format=None, time_format=None,
                timedelta_format=None, *args, **kwargs):
    r"""
        Same as Python's json.dumps but also serialize datetime, date, time
        and timedelta.

        Example:
            >>> import datetime
            >>> json_dumps({'test': datetime.datetime(2000, 1, 1, 1, 1, 1)})
            '{"test": "2000-01-01 01:01:01.000000"}'
            >>> json_dumps({'test': datetime.date(2000, 1, 1)})
            '{"test": "2000-01-01"}'
            >>> json_dumps({'test': datetime.time(1, 1, 1)})
            '{"test": "01:01:01.000000"}'
            >>> json_dumps({'test': datetime.timedelta(1, 1)})
            '{"test": "timedelta(seconds=\'86401.0\')"}'
            >>> json_dumps({'test': datetime.timedelta(1, 1), 'a': [1, 2]})
            '{"test": "timedelta(seconds=\'86401.0\')", "a": [1, 2]}'

    """
    return JSONEncoder(datetime_format, date_format, time_format,
                       timedelta_format, *args, **kwargs).encode(data)


def json_loads(string, datetime_pattern=None, date_pattern=None,
                time_pattern=None, timedelta_pattern=None, datetime_format=None,
                date_format=None, time_format=None, *args, **kwargs):
    r"""
        Same as Python's json.loads, but handles formats from batbelt.json_dumps
        which are currently mainly date formats.

        Example:

            >>> json_loads('{"test": "2000-01-01 01:01:01.000000"}')
            {'test': datetime.datetime(2000, 1, 1, 1, 1, 1)}
            >>> json_loads('{"test": "2000-01-01"}')
            {'test': datetime.date(2000, 1, 1)}
            >>> json_loads('{"test": "01:01:01.000000"}')
            {'test': datetime.time(1, 1, 1)}
            >>> json_loads('{"test": "timedelta(seconds=\'86401.0\')"}')
            {'test': datetime.timedelta(1, 1)}
            >>> json_loads('{"test": "timedelta(seconds=\'86401.0\')", "a": [1, 2]}')
            {'test': datetime.timedelta(1, 1), 'a': [1, 2]}

    """
    return JSONDecoder(datetime_pattern, date_pattern, time_pattern,
                       timedelta_pattern, datetime_format, date_format,
                       time_format, *args, **kwargs).decode(string)


def to_timestamp(dt):
    """
        Return a timestamp for the given datetime object.

        Example:

            >>> import datetime
            >>> to_timestamp(datetime.datetime(2000, 1, 1, 1, 1, 1, 1))
            946688461
    """
    return (dt - datetime(1970, 1, 1)).total_seconds()



def import_from_path(path):
    """
        Import a class dynamically, given it's dotted path.
    """
    module_name, class_name = path.rsplit('.', 1)
    try:
        return getattr(__import__(module_name, fromlist=[class_name]), class_name)
    except AttributeError:
        raise ImportError('Unable to import %s' % path)



def attr(obj, *attrs, **kwargs):
    """
        Follow chained attributes and get the value of the last attributes.
        If an attribute error is raised, returns the default value.

        res = attr(data, 'test', 'o', 'bla', default="yeah")

        is the equivalent of

        try:
            res = getattr(getattr(getattr(data, 'test'), 'o'), 'bla')
        except AttributeError:
            res = "yeah"

    """
    try:
        value = getattr(obj, attrs[0])

        for attr in attrs[1:]:
            value = getattr(value, attr)
    except (IndexError, AttributeError):
        return kwargs.get('default', None)

    return value


def chunks(seq, chunksize, process=tuple):
    """
        Yields items from an iterator in iterable chunks.
    """
    it = iter(seq)
    while True:
        yield process(chain([next(it)], islice(it, chunksize - 1)))



def window(iterable, size=2):
    """
        Yields iterms by bunch of a given size, but rolling only one item
        in and out at a time when iterating.
    """
    iterable = iter(iterable)
    d = deque(islice(iterable, size), size)
    yield d
    for x in iterable:
        d.append(x)
        yield d


def dmerge(d1, d2, merge_func=None):
    """
        Create a new dictionary being the merge of the two passed as a
        parameter. If a key is in both dictionaries, the values are processed
        with the merge_func.

        By default the value in the second dictionary erases the value in the
        first one.
    """
    d = {}

    d.update(d1)

    if merge_func is None:
        d.update(d2)
        return d

    for k, v in d2.iteritems():
        if k in d:
            d[k] = merge_func(d[k], v)
        else:
            d[k] = v
    return d



def get(data, *keys, **kwargs):
    """
        Extract a data from nested mapping and sequences using a list of keys
        and indices to apply successively. If a key error or an index error
        is raised, returns the default value.

        res = get(data, 'test', 0, 'bla', default="yeah")

        is the equivalent of

        try:
            res = data['test'][0]['bla']
        except (KeyError, IndexError):
            res = "yeah"

    """
    try:
        value = data[keys[0]]

        for key in keys[1:]:
            value = value[key]
    except (KeyError, IndexError, TypeError):
        return kwargs.get('default', None)

    return value



def subdict(dct, include=(), exclude=()):
    """
        Return a dictionary that is a copy of the given one.

        All values in `include` are used as key to be copied to
         the resulting dictionary.

        You can also pass a list of key to exclude instead by setting
        `exclude`. But you can't use both `include` and `exclude`: if you do,
        `exclude will be ignored`

        Example:

        >>> subdict({1:None, 2: False, 3: True}, [1, 2])
        {1: None, 2: False}
        >>> subdict({1:None, 2: False, 3: True}, exclude=[1, 2])
        {3: True}

    """

    if include:
        return dict((k, v) for k, v in dct.iteritems() if k in include)

    return dict((k, v) for k, v in dct.iteritems() if k not in exclude)



def iget(data, value, default=None):
    """
        Same as indexing, but works with any iterable,
        and accept a default value.

        :Example:

        >>> iget(xrange(10), 0)
        0
        >>> iget(xrange(10), 5)
        5
        >>> iget(xrange(10), 10000, default='wololo')
        u'wololo'
    """

    for x in islice(data, value, None):
        return x
    return default


def unpack(indexable, *args, **kwargs):
    """
        Return an generator with the values for the given keys/indices or
        a default value.

        :Example:

        >>> dct = {'a': 2, 'b': 4, 'z': 42}
        >>> a, b, c = unpack(dct, 'a', 'b', 'c', default=1)
        >>> a
        2
        >>> b
        4
        >>> c
        1
        >>> list(unpack(range(5, 10), 2, 4))
        [7, 9]
    """

    default = kwargs.get('default', None)

    for key in args:
        yield get(indexable, key, default=default)


def skip_duplicates(iterable, key=lambda x: x):
    """
        Returns a generator that will yield all objects from iterable, skipping
        duplicates.

        Duplicates are identified using the `key` function to calculate a
        unique fingerprint. This does not use natural equality, but the
        result use a set() to remove duplicates, so defining __eq__
        on your objects would have effect.

        By default the fingerprint is the object itself,
        which ensure the functions works as-is with iterable of primitives
        such as int, str or tuple.

        :Example:

            >>> list(skip_duplicates([1, 2, 3, 4, 4, 2, 1, 3 , 4]))
            [1, 2, 3, 4]

        The return value of `key` MUST be hashable, which means for
        non hashable objects such as dict, set or list, you need to specify
        a a function that returns a hashable fingerprint.

        :Example:

            >>> list(skip_duplicates(([], [], (), [1, 2], (1, 2)), lambda x: tuple(x)))
            [[], [1, 2]]
            >>> list(skip_duplicates(([], [], (), [1, 2], (1, 2)), lambda x: (type(x), tuple(x))))
            [[], (), [1, 2], (1, 2)]

        For more complex types, such as custom classes, the default behavior
        is to remove nothing. You MUST provide a `key` function is you wish
        to filter those.

        :Example:

            >>> class Test(object):
                def __init__(self, foo='bar'):
                    self.foo = foo
                def __repr__(self):
                    return "Test('%s')" % self.foo
            ...
            >>> list(skip_duplicates([Test(), Test(), Test('other')]))
            [Test('bar'), Test('bar'), Test('other')]
            >>> list(skip_duplicates([Test(), Test(), Test('other')], lambda x: x.foo))
            [Test('bar'), Test('other')]

        See also :
            - strip_duplicates : a simpler, slower function that returns a list
                                 of elements with no duplicates. It accepts
                                 non hashable elements and honors __eq__.
          - remove_duplicates : remove duplicates from a list in place.
                                Most ressource efficient merthod.
    """
    fingerprints = set()

    try:
        # duplicate some code to gain perf in the most common case
        if key is None:
            for x in iterable:
                if x not in fingerprints:
                    yield x
                    fingerprints.add(x)
        else:
            for x in iterable:
                fingerprint = key(x)
                if fingerprint not in fingerprints:
                    yield x
                    fingerprints.add(fingerprint)
    except TypeError:
        try:
            hash(fingerprint)
        except TypeError:
            raise TypeError(
                "Calculating the key on one element resulted in a non hashable "
                "object of type '%s'. Change the 'key' parameter to a function "
                "that always, returns a hashable object. Hint : primitives "
                "like int, str or tuple, are hashable, dict, set and list are "
                "not. \nThe object that triggered the error was:\n%s" % (
                type(fingerprint), x)
            )
        else:
            raise


KEY, PREV, NEXT = range(3)


class sset(MutableSet):
    """
        Set that preserves ordering.

        From http://code.activestate.com/recipes/576694/
    """

    def __init__(self, iterable=None):
        self.end = end = []
        end += [None, end, end]         # sentinel node for doubly linked list
        self.map = {}                   # key --> [key, prev, next]
        if iterable is not None:
            self |= iterable

    def __len__(self):
        return len(self.map)

    def __contains__(self, key):
        return key in self.map

    def add(self, key):
        if key not in self.map:
            end = self.end
            curr = end[PREV]
            curr[NEXT] = end[PREV] = self.map[key] = [key, curr, end]

    def discard(self, key):
        if key in self.map:
            key, prev, next = self.map.pop(key)
            prev[NEXT] = next
            next[PREV] = prev

    def __iter__(self):
        end = self.end
        curr = end[NEXT]
        while curr is not end:
            yield curr[KEY]
            curr = curr[NEXT]

    def __reversed__(self):
        end = self.end
        curr = end[PREV]
        while curr is not end:
            yield curr[KEY]
            curr = curr[PREV]

    def pop(self, last=True):
        if not self:
            raise KeyError('set is empty')
        key = next(reversed(self)) if last else next(iter(self))
        self.discard(key)
        return key

    def __repr__(self):
        if not self:
            return '%s()' % (self.__class__.__name__,)
        return '%s(%r)' % (self.__class__.__name__, list(self))

    def __eq__(self, other):
        if isinstance(other, sset):
            return len(self) == len(other) and list(self) == list(other)
        return set(self) == set(other)

    def __del__(self):
        self.clear()   # remove circular references


def add_to_pythonpath(path, starting_point='.', insertion_index=None):
    """
        Add the directory to the sys.path.

        You can path an absolute or a relative path to it.

        If you choose to use a relative path, it will be relative to
        `starting_point` by default, which is set to '.'.

        You may want to set it to something like __file__ (the basename will
        be stripped, and the current file's parent directory will be used
        as a starting point, which is probably what you expect in the
        first place).

        :example:

        >>> add_to_pythonpath('../..', __file__)
    """

    if not os.path.isabs(path):

        if os.path.isfile(starting_point):
            starting_point = os.path.dirname(starting_point)

        path = os.path.join(starting_point, path)

    path = os.path.realpath(os.path.expandvars(os.path.expanduser(path)))

    if path not in sys.path:
        if insertion_index is None:
            sys.path.append(path)
        else:
            sys.path.insert(insertion_index, path)


def write(path, *args, **kwargs):
    r"""
        Try to write to the file at `path` the values passed as `args` as lines.

        It will attempt decoding / encoding and casting automatically each value
        to a string.

        This is an utility function : its slow and doesn't consider edge cases,
        but allow to do just what you want most of the time in one line.

        :Example:

            s = '/tmp/test'
            write(s, 'test', '\xe9', 1, ['fdjskl'])
            print open(s).read()
            test
            \xe9
            1
            ['fdjskl']

        You can optionally pass :

        mode : among 'a', 'w', which default to 'w'. Binary mode is forced.
        encoding : which default to utf8 and will condition decoding AND encoding
        errors : what to do when en encoding error occurs : 'replace' by default,
                which replace faulty caracters with '?'

        You can pass string or unicode as *args, but if you pass strings,
        make sure you pass them with the same encoding you wish to write to
        the file.
    """

    mode = kwargs.get('mode', 'w')
    encoding = kwargs.get('encoding', 'utf8')
    errors = kwargs.get('encoding', 'replace')

    with codecs.open(path, mode=mode, encoding=encoding, errors=errors) as f:

        for line in args:

            if isinstance(line, bytes):
                line = line.decode(encoding, errors)

            if not isinstance(line, unicode):
                line = repr(line)

            f.write(line + os.linesep)


class Flattener(object):
    """
        Create a flattener that you can call on a deeply nested data
        structures to iterate over the items as it if it were a flat iterable.

        The flattener returns a generator that lazily yield the items and
        deals with up to hundred of levels of nesting (~800 on my machine,
        and you can control it with sys.setrecursionlimit).

        A default flattener named 'flatten' is available by default.

        :Example:

            a = []
            for i in range(10):
                a = [a, i]
            print(a)

            [[[[[[[[[[[], 0], 1], 2], 3], 4], 5], 6], 7], 8], 9]

            print(list(flatten(a)))

            [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]

        By default, it flattens all the types listed in
        Flattener.DEFAULT_FLATTEN_TYPES but you can pass you list via
        flatten_types while calling a Flatener instance.

        For ambigious types like dict, you can pass iterable_getters, a
        mapping type / callback letting you define how to extract items from
        each type.

        :Example:

            a = []
            for i in range(2):
                a = [a, i] + [{'a': 1., 'b': {'c': 3.}}]
            print(a)

            [[[], 0, {'a': 1.0, 'b': {'c': 3.0}}], 1, {'a': 1.0, 'b': {'c': 3.0}}]

            new_ft = Flattener.DEFAULT_FLATTEN_TYPES + (dict,)

            dico_flatten = Flattener(flatten_types=new_ft,
                                     iterable_getters={dict: lambda x: x.items()})

            print(list(dico_flatten(a)))

            [0, u'a', 1.0, u'b', u'c', 3.0, 1, u'a', 1.0, u'b', u'c', 3.0]

    """

    DEFAULT_FLATTEN_TYPES = (
        list,
        tuple,
        set,
        (x for x in ()).__class__,
        xrange,
        deque,
        MutableSet,
        # Sequence # warning, a string is a subclass of Sequence
    )


    def __init__(self, flatten_types=None, iterable_getters={}):
        self.flatten_types = flatten_types or self.DEFAULT_FLATTEN_TYPES
        self.iterable_getters = iterable_getters


    def should_flatten(self, obj):
        """
            Returns if the object should be flatten or not, checking if the
            objects is an instance of type listed in DEFAULT_FLATTEN_TYPES
            by default.
        """
        return isinstance(obj, self.flatten_types)


    def transform_iterable(self, obj):
        """
            Apply a pre-processing to an object before iterate on it. Can
            be useful for types such as dict on which you may want to call
            values() or items() before iteration.

            By defaut, it check if the object is an DIRECT instance (not
            a subclass) of any key in iterable_getters, passed in __init__
            and apply the transform.

            iterable_getter should be a mapping with types as key and
            transformation function as values, such as :

            {dict: lambda x: x.items()}

            iterable_getter default value is {}, making transform_iterable
            a noop.
        """
        if obj.__class__ in self.iterable_getters:
            return self.iterable_getters[obj.__class__](obj)
        return obj


    def __call__(self, iterable):
        """
            Returns a generator yieling items from a deeply nested iterable
            like it would be a flat one.
        """
        for e in iterable:
            if self.should_flatten(e):
                for f in self(self.transform_iterable(e)):
                    yield f
            else:
                yield e



flatten = Flattener()
