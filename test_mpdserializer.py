'''
As with the code that it's testing, these unit tests are adapted from
python-mpd2.
'''

from . import mpdserializer
from nose.tools import eq_


def test_writable_command():

    expected = 'list "album"\n'
    actual = mpdserializer.writable_command('list', 'album')
    eq_(expected, actual)


def test_fetch_nothing():
    eq_(None, mpdserializer.fetch_nothing('OK\n'))


def test_fetch_list():
    expected = ('J-Pop', 'Metal')
    raw_text = '\n'.join(['Genre: J-Pop', 'Genre: Metal', 'OK', ''])
    actual = mpdserializer.fetch_list(raw_text)
    eq_(expected, actual)
