#!/usr/bin/env python

from sip import setapi
setapi("QDate", 2)
setapi("QDateTime", 2)
setapi("QTextStream", 2)
setapi("QTime", 2)
setapi("QVariant", 2)
setapi("QString", 2)
setapi("QUrl", 2)


from PyQt4 import QtCore, QtGui, QtNetwork
import collections
import sys


def main():
    app = QtGui.QApplication(sys.argv)
    view = Window()
    view.show()
    sys.exit(app.exec_())


class Window(QtGui.QMainWindow):

    def __init__(self, parent=None):
        super(Window, self).__init__(parent)

        self.__mpd = QMPDSocket(self)
        self.__mpd.mpdError.connect(self.printStuff)
        self.__mpd.connectToHost('localhost', 6600)

    def closeEvent(self, event):
        self.__mpd.disconnectFromMPD()

    def printStuff(self, text):
        print text


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

    HelloState = 0

    def __init__(self, parent=None):
        super(QMPDSocket, self).__init__(parent)
        self.connected.connect(self.onConnect)
        self.readyRead.connect(self.onReadyRead)

    def connectToMPD(self, host, port):
        self.connectToHost(host, port)

    def onConnect(self):
        self.__state = self.HelloState

    def onReadyRead(self):
        response = self.readFromMPD()
        if self.__state == self.HelloState:
            error = MPDParser.hello_error(response)
            if error is not None:
                if error.error_type == 'protocol':
                    self.disconnectFromHost()
                self.mpdError.emit(error.msg)

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
    def hello_error(line):
        # sample line: u'OK MPD 0.18.0\n'

        if not line.endswith('\n'):
            return MPDError('connection',
                            'Connection lost while reading MPD hello')

        if not line.startswith('OK MPD '):
            return MPDError('protocol',
                            "Got invalid MPD hello: '{}'".format(line))


MPDError = collections.namedtuple('Error', ['error_type', 'msg'])


if __name__ == '__main__':
    main()
