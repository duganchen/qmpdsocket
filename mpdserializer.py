'''
Converts socket-writable or socket-read text to and from Python data
structures.

This is adapted from python-mpd2, and decoupled from the socket operations.

It also assumes Python 2, as I won't be testing this on Python 3 for a while.
'''


class CommandError(Exception):
    pass


class ConnectionError(Exception):
    pass


class ProtocolError(Exception):
    pass


ErrorPrefix = 'ACK '
HelloPrefix = 'OK MPD '
Next = "list_OK"
Success = "OK"


def writable_command(cls, command, *args):
    parts = (command,) + tuple(_command_arg(arg) for arg in args)
    cmdline = ' '.join(parts)
    return '{}\n'.format(cmdline)


def fetch_hello(text):
    # sample line: u'OK MPD 0.18.0\n'

    for line in _iter_lines(text, command_list=False):

        if not line.endswith('\n'):
            raise ConnectionError('Connection lost while reading MPD hello')

        if not line.startswith(HelloPrefix):
            message = "Got invalid MPD hello: '{}'".format(line)
            raise ProtocolError(message)


def fetch_nothing(text):
    for line in _iter_lines(text, command_list=False):
        raise ProtocolError("Got unexpected return value: '{}'".format(line))


def _test_for_nothing(line):
    raise ProtocolError("Got unexpected return value: '{}'".format(line))


def _command_arg(cls, arg):
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


def _iter_objects(lines, separator, delimiters=[]):
    obj = {}
    for line in lines:
        key, value = _get_pair(line, separator)
        key = key.lower()
        if obj:
            if key in delimiters:
                yield obj
                obj = {}
            elif key in obj:
                if not isinstance(obj[key], list):
                    obj[key] = [obj[key], value]
                else:
                    obj[key].append(value)
                continue
        obj[key] = value
    if obj:
        yield obj


def _iter_lines(text, command_list=False):

    # Assumes that text has been prepared with ".decode('utf-8')".

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


def _get_pair(line, separator):

    pair = line.split(separator, 1)
    if len(pair) < 2:
        raise ProtocolError("Could not parse pair: '{}'".format(line))
    return pair
