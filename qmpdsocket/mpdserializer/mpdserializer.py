'''
Converts socket-writable or socket-read text to and from Python data
structures.

This is adapted from python-mpd2, and decoupled from the socket operations.

It also assumes Python 2, as I won't be testing this on Python 3 for a while.
That means that all of the _fetch_* methods expect text that's been first
prepared with .decode('utf-8')
'''


from __future__ import (absolute_import, generators, nested_scopes,
                        print_function, unicode_literals, with_statement)


class MPDError(Exception):
    pass


class CommandError(MPDError):
    pass


class ConnectionError(MPDError):
    pass


class ProtocolError(MPDError):
    pass


ErrorPrefix = 'ACK '
HelloPrefix = 'OK MPD '
Next = "list_OK"
Success = "OK"


def serialize_command(command, *args):
    parts = (command,) + tuple(_command_arg(arg) for arg in args)
    cmdline = ' '.join(parts)
    return '{}\n'.format(cmdline)


def deserialize_hello(text):
    # sample line: u'OK MPD 0.18.0\n'

    if not text.endswith('\n'):
        raise ConnectionError('Connection lost while reading MPD hello')

    for line in _iter_lines(text, command_list=False):
        if not line.startswith(HelloPrefix):
            message = "Got invalid MPD hello: '{}'".format(line)
            raise ProtocolError(message)


def deserialize_nothing(text):
    for line in _iter_lines(text, command_list=False):
        raise ProtocolError("Got unexpected return value: '{}'".format(line))


def deserialize_tuple(text):
    lines = _iter_lines(text, command_list=False)
    items = _iter_listitems(lines, separator=': ')
    return tuple(items)


def deserialize_dict(text):

    lines = _iter_lines(text, command_list=False)
    for obj in _iter_objects(lines, separator=': ', delimiters=[]):
        return obj
    return {}


def deserialize_songs(text):

    lines = _iter_lines(text, command_list=False)
    return tuple(_iter_objects(lines, separator=': ', delimiters=['file']))


def _command_arg(arg):
    if type(arg) is tuple:
        if len(arg) == 1:
            return '"{}:"'.format(int(arg[0]))
        return '"{}:{}"'.format(int(arg[0]), int(arg[1]))
    return '"{}"'.format(_escape(_encode(arg)))


def _encode(text):
    if type(text) is str:
        return text
    return (unicode(text)).encode("utf-8")


def _escape(text):
    return text.replace("\\", "\\\\").replace('"', '\\"')


def _iter_listitems(lines, separator):

    seen = None
    for key, value in _iter_pairs(lines, separator):
        if key != seen:
            if seen is not None:
                message = "Expected key '{}', got '{}'".format(seen, key)
                raise ProtocolError(message)
            seen = key
        yield value


def _iter_objects(lines, separator, delimiters):
    obj = {}
    for key, value in _iter_pairs(lines, separator):
        key = key.lower()
        if obj:
            if key.lower() in delimiters:
                yield obj
                obj = {}
            elif key.lower() in obj:
                if not isinstance(obj[key], list):
                    obj[key] = [obj[key], value]
                else:
                    obj[key].append(value)
                continue
        obj[key] = value
    if obj:
        yield obj


def _iter_lines(text, command_list=False):

    if not text.endswith('\n'):
        raise ConnectionError('Connection lost while reading line')

    for line in text.split('\n')[:-1]:
        if line.startswith(ErrorPrefix):
            error = line[len(ErrorPrefix):].strip()
            raise CommandError(error)
        if command_list:
            if line == Next:
                continue
            if line == Success:
                raise ProtocolError("Got unexpected '%s'".format(Success))
        elif line != Success:
            yield line


def _iter_pairs(lines, separator):

    for line in lines:
        pair = line.split(separator, 1)
        if len(pair) < 2:
            raise ProtocolError("Could not parse pair: '{}'".format(line))
        yield pair
