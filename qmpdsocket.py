#!/usr/bin/env python

from sip import setapi
setapi("QDate", 2)
setapi("QDateTime", 2)
setapi("QTextStream", 2)
setapi("QTime", 2)
setapi("QVariant", 2)
setapi("QString", 2)
setapi("QUrl", 2)


from PyQt4 import QtCore, QtNetwork


class ConnectionError(Exception):
    pass


class ProtocolError(Exception):
    pass


class QMPDSocket(QtNetwork.QTcpSocket):

    # idle notifications
    database = QtCore.pyqtSignal()
    update = QtCore.pyqtSignal()
    stored_playist = QtCore.pyqtSignal()
    playlist = QtCore.pyqtSignal()
    player = QtCore.pyqtSignal()
    mixer = QtCore.pyqtSignal()
    output = QtCore.pyqtSignal()
    options = QtCore.pyqtSignal()
    sticker = QtCore.pyqtSignal()
    subscription = QtCore.pyqtSignal()
    message = QtCore.pyqtSignal()

    mpdError = QtCore.pyqtSignal(unicode)

    # Program states. For reading.
    HelloState = 0

    def __init__(self, parent=None):
        super(QMPDSocket, self).__init__(parent)
        self.connected.connect(self.onConnect)
        self.readyRead.connect(self.onReadyRead)
        self.__commandState = self.HelloState
        self.__responseHandlers = {self.HelloState: self.onHello}

    def connectToMPD(self, host, port):
        self.connectToHost(host, port)

    def onConnect(self):
        self.__state = self.HelloState

    def onReadyRead(self):
        response = self.readFromMPD()
        handle = self.__responseHandlers[self.__commandState]
        handle(response)

    def onHello(self, response):
        try:
            MPDParser.validate_hello(response)
        except ProtocolError as e:
            self.mpdError.emit(str(e))
        except ConnectionError as e:
            self.disconnectFromHost()
            self.mpdError.emit(str(e))

    def readFromMPD(self):
        return self.readAll().data().decode('utf-8')

    def disconnectFromMPD(self):
        if self.state() == QtNetwork.QTcpSocket.ConnectedState:
            self.disconnectFromHost()


class MPDParser(object):

    # This is largely extracted from python-mpd2.

    @classmethod
    def writable_command(cls, command, *args):
        parts = (command,) + tuple(cls.command_arg(arg) for arg in args)
        cmdline = ' '.join(parts)
        return '{}\n'.format(cmdline)

    @classmethod
    def command_arg(cls, arg):
        if type(arg) is tuple:
            if len(arg) == 1:
                return '"{}:"'.format(int(arg[0]))
            return '"{}:{}"'.format(int(arg[0]), int(arg[1]))
        return '"{}"'.format(cls.escape(cls.encode(arg)))

    @staticmethod
    def encode(text):
        if type(text) is str:
            return text
        return (unicode(text)).encode("utf-8")

    @staticmethod
    def escape(text):
        return text.replace("\\", "\\\\").replace('"', '\\"')

    @staticmethod
    def iter_objects(lines, separator, delimiters=[]):
        obj = {}
        for line in lines:
            key, value = line.split(separator, 1)
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

    @staticmethod
    def validate_hello(line):
        # sample line: u'OK MPD 0.18.0\n'

        if not line.endswith('\n'):
            raise ConnectionError('Connection lost while reading MPD hello')

        if not line.startswith('OK MPD '):
            message = "Got invalid MPD hello: '{}'".format(line)
            raise ProtocolError(message)
