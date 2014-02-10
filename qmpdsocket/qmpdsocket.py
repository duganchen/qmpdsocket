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

from .mpdserializer import (ConnectionError, ProtocolError, deserialize_hello)


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
        response = self.readAll().data().decode('utf-8')
        handle = self.__responseHandlers[self.__commandState]
        handle(response)

    def onHello(self, response):
        try:
            deserialize_hello(response)
        except ProtocolError as e:
            self.mpdError.emit(str(e))
        except ConnectionError as e:
            self.disconnectFromHost()
            self.mpdError.emit(str(e))

    def disconnectFromMPD(self):
        if self.state() == QtNetwork.QTcpSocket.ConnectedState:
            self.disconnectFromHost()
