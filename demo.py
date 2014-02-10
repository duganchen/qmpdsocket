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
        print(text)


if __name__ == '__main__':
    main()
