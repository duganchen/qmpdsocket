#!/usr/bin/env python

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


from PyQt4 import QtGui
from qmpdsocket import QMPDSocket
from pprint import pprint
import sys


def main():
    app = QtGui.QApplication(sys.argv)
    view = Window()
    view.show()
    sys.exit(app.exec_())


class Window(QtGui.QMainWindow):

    def __init__(self, parent=None):
        super(Window, self).__init__(parent)

        statusButton = QtGui.QPushButton('&Status')
        statusButton.clicked.connect(self.onStatusClick)
        self.setCentralWidget(statusButton)

        self.__mpd = QMPDSocket(self)
        self.__mpd.mpdError.connect(self.printStuff)

        self.__mpd.database.connect(self.onDatabase)
        self.__mpd.update.connect(self.onUpdate)
        self.__mpd.stored_playlist.connect(self.onStoredPlaylist)
        self.__mpd.playlist.connect(self.onPlaylist)
        self.__mpd.player.connect(self.onPlayer)
        self.__mpd.mixer.connect(self.onMixer)
        self.__mpd.output.connect(self.onOutput)
        self.__mpd.options.connect(self.onOptions)
        self.__mpd.sticker.connect(self.onSticker)
        self.__mpd.subscription.connect(self.onSubscription)
        self.__mpd.message.connect(self.onMessage)

        self.__mpd.connectToHost('localhost', 6600)

    def closeEvent(self, event):
        self.__mpd.disconnectFromMPD()

    def printStuff(self, text):
        print(text)

    def onStatusClick(self):
        def on_status(status):
            pprint(status)
        status = self.__mpd.status()
        status.data.connect(on_status)

    def onDatabase(self):
        print('the song database has been modified after update.')

    def onUpdate(self):
         print('a database update has started or finished.')

    def onStoredPlaylist(self):
        msg = 'a stored playlist has been modified, renamed, created or '\
                'deleted'
        print(msg)

    def onPlaylist(self):
        print('the current playlist has been modified')

    def onPlayer(self):
        print('the player has been started, stopped or seeked')

    def onMixer(self):
        print('the volume has been changed')

    def onOutput(self):
        print('an audio output has been enabled or disabled')

    def onOptions(self):
        print('options like repeat, random, crossfade, replay gain')

    def onSticker(self):
        print('the sticker database has been modified.')

    def onSubscription(self):
        print('a client has subscribed or unsubscribed to a channel')

    def onMessage(self):
        print('a message was received on a channel this client is subscribed '
              'to')


if __name__ == '__main__':
    main()
