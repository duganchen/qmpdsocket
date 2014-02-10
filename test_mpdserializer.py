from . import mpdserializer
from nose.tools import eq_


def test_fetch_nothing():
    eq_(None, mpdserializer.fetch_nothing('OK\n'))
