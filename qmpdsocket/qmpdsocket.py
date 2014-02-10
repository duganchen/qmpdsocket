from __future__ import (absolute_import, generators, nested_scopes,
                        print_function, unicode_literals, with_statement)

from sip import setapi
setapi("QDate", 2)
setapi("QDateTime", 2)
setapi("QTextStream", 2)
setapi("QTime", 2)
setapi("QVariant", 2)
setapi("QString", 2)
setapi("QUrl", 2)
from PyQt4 import QtCore, QtNetwork

from .mpdserializer import (ConnectionError, MPDError, ProtocolError,
                            serialize_command, deserialize_dict,
                            deserialize_hello)


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

    # For use internally to send data to MPDResponse objects.
    response = QtCore.pyqtSignal(unicode)

    # Program states. For reading.
    HelloState, CommandState = range(2)

    def __init__(self, parent=None):
        super(QMPDSocket, self).__init__(parent)
        self.connected.connect(self.onConnect)
        self.readyRead.connect(self.onReadyRead)
        self.__commandState = self.HelloState
        self.__responseHandlers = {self.HelloState: self.onHello,
                                   self.CommandState: self.onCommand}

    def connectToMPD(self, host, port):
        self.connectToHost(host, port)

    def onConnect(self):
        self.__state = self.HelloState

    def onReadyRead(self):
        print('Ready Read')
        response = self.readAll().data().decode('utf-8')
        handle = self.__responseHandlers[self.__commandState]
        handle(response)

    def onHello(self, response):
        try:
            deserialize_hello(response)
        except ProtocolError as e:
            self.onMPDError(unicode(e))
        except ConnectionError as e:
            self.onConnectionError(unicode(e))

    def onCommand(self, responseText):
        print('On Command')
        self.response.emit(responseText)

    def onConnectionError(self, message=None):
        self.disconnectFromHost()
        if message is not None:
            self.onMPDError(message)

    def onMPDError(self, message):
        self.mpdError.emit(message)

    def disconnectFromMPD(self):
        if self.state() == QtNetwork.QTcpSocket.ConnectedState:
            self.disconnectFromHost()

    def status(self):
        self.write(serialize_command('status'))
        self.__commandState = self.CommandState
        response = MPDResponse(deserialize_dict, self)
        self.response.connect(response.onResponse)
        response.connectionError.connect(self.onConnectionError)
        self.response.connect(response.onResponse)
        return response


class MPDResponse(QtCore.QObject):

    data = QtCore.pyqtSignal([dict], [tuple])
    error = QtCore.pyqtSignal(unicode)

    # ConnectionErrors get handled by the socket class.
    connectionError = QtCore.pyqtSignal(unicode)

    def __init__(self, deserialize_func, parent=None):
        super(MPDResponse, self).__init__(parent)
        self.__deserialize_func = deserialize_func

    def onResponse(self, text):
        self.deleteLater()
        try:
            data = self.__deserialize_func(text)
            self.data.emit(data)
        except ConnectionError as e:
            self.connectionError.emit(unicode(e))
        except MPDError as e:
            self.error.emit(unicode(e))
