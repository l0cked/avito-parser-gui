from parse import Parse
from PyQt5.QtCore import pyqtSlot
from PyQt5.QtQml import QQmlApplicationEngine
from PyQt5.QtWidgets import QApplication
import asyncio


class Main(QQmlApplicationEngine, Parse):
    app = QApplication([])
    loop = asyncio.get_event_loop()

    def __init__(self):
        super().__init__()
        self.rootContext().setContextProperty('self', self)
        self.load('qml/main.qml')
        self.loop.run_until_complete(self.init())
        self.log('Init OK')
        self.app.exec_()
        self.loop.run_until_complete(self.close())

    async def init(self):
        await self.db_init()
        await self.proxylist_init()

    async def close(self):
        await self.proxylist_close()
        await self.db_close()

    @pyqtSlot(str)
    def click(self, value):
        if value == 'parse':
            self.parse()
        if value == 'proxylist_update':
            self.proxylist_update()
        if value == 'proxylist_clear':
            self.loop.run_until_complete(self.proxylist_clear())


Main()
