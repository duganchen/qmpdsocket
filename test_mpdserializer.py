from . import mpdserializer
from nose.tools import eq_


def test_writable_command():

    expected = 'list "album"\n'
    actual = mpdserializer.writable_command('list', 'album')
    eq_(expected, actual)


def test_fetch_nothing():
    eq_(None, mpdserializer.fetch_nothing('OK\n'))
