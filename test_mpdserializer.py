'''
As with the code that it's testing, these unit tests are adapted from
python-mpd2.
'''

from __future__ import (absolute_import, generators, nested_scopes,
                        print_function, unicode_literals, with_statement)


from . import mpdserializer
from nose.tools import eq_


def test_serialize_command():

    expected = 'list "album"\n'
    actual = mpdserializer.serialize_command('list', 'album')
    eq_(expected, actual)


def test_fetch_nothing():
    eq_(None, mpdserializer.deserialize_nothing('OK\n'))


def test_fetch_list():
    expected = ('J-Pop', 'Metal')
    raw_text = '\n'.join(['Genre: J-Pop', 'Genre: Metal', 'OK', ''])
    actual = mpdserializer.deserialize_tuple(raw_text)
    eq_(expected, actual)
