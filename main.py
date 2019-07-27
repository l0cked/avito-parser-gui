from datetime import datetime
from db import Db
from models import LogModel
from PyQt5.QtCore import QThread, QObject, pyqtSignal, pyqtSlot
from PyQt5.QtQml import QQmlApplicationEngine
from PyQt5.QtWidgets import QApplication
import aiohttp
import asyncio
import time


class Proxy(QObject):
    message = pyqtSignal(str)
    finished = pyqtSignal(list)
    options = {
        'check_url': 'https://m.avito.ru',
        'check_timeout': 2,
        'check_threads_enable': True,
        'check_threads': 999,
        'check_sleep': .1
    }
    proxylist = []
    checking = 0
    check_proxylist = []

    def __init__(self):
        super().__init__()

    @pyqtSlot()
    def start(self):
        asyncio.run(self._start())
        self.finished.emit(self.check_proxylist)

    def log(self, message):
        self.message.emit(message)

    async def _start(self):
        start = time.time()
        self.log('Starting proxylist update')
        async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(ssl=False)) as session:
            async with session.get('https://raw.githubusercontent.com/fate0/proxylist/master/proxy.list', timeout=5) as response:
                html = await response.text()
                self.log(f'Proxylist HTML load ({len(html)} bytes)')
                if await self.parse(html):
                    self.log(f'{len(self.proxylist)} http proxy found')
                    self.log(f'Checking proxylist url: {self.options["check_url"]}, timeout: {self.options["check_timeout"]}, threads: {self.options["check_threads"]}')

                    await asyncio.gather(*[self.check(session, proxy) for proxy in self.proxylist])
        self.log(f'Found {len(self.check_proxylist)} proxy in {time.time()-start:.2f} sec')

    async def parse(self, html):
        data = html.split('\n')
        null = None
        for d in data:
            if d != '':
                try:
                    proxy = eval(d)
                except:
                    return False
                if proxy['type'] == 'http':
                    del proxy['type']
                    del proxy['anonymity']
                    del proxy['export_address']
                    del proxy['from']
                    del proxy['response_time']
                    proxy['port'] = str(proxy['port'])
                    proxy['url'] = 'http://{host}:{port}'.format(**proxy)
                    proxy['index'] = len(self.proxylist)

                    if proxy['country']:
                        self.proxylist.append(proxy)
        return True

    async def check(self, session, proxy):
        if self.options['check_threads_enable']:
            while self.checking > self.options['check_threads']:
                await asyncio.sleep(self.options['check_sleep'])

        start = time.time()
        self.checking += 1

        try:
            async with session.get(self.options['check_url'], proxy=proxy['url'], timeout=self.options['check_timeout']) as response:
                data = await response.text()
                if response.status == 200:
                    proxy['response_time'] = time.time()-start
                    proxy['id'] = len(self.check_proxylist)

                    self.log('[{id}/{index}] {country} {url}  {response_time:.2f} sec'.format(**proxy))

                    self.check_proxylist.append(proxy)
        except:
            pass

        self.checking -= 1


class Main(QQmlApplicationEngine, Db):
    app = QApplication([])
    thread = None
    loop = asyncio.get_event_loop()

    def __init__(self):
        super().__init__()
        self.log_model = LogModel()
        self.rootContext().setContextProperty('logModel', self.log_model)
        self.load('qml/main.qml')
        self.rootObjects()[0].findChild(QObject, 'btn').clicked.connect(self.btn_clicked)
        self.loop.run_until_complete(self._init())
        self.log('Init OK')
        self.app.exec_()
        self.loop.run_until_complete(self._close())

    async def _init(self):
        await self.db_init()

    async def _close(self):
        await self.db_close()

    def log(self, message, type='System', time=None):
        if not time:
            dt = datetime.now()
            time = dt.strftime('%H:%M:%S')
        self.log_model.addItem(time, type, message)

    def btn_clicked(self):
        self.log('btn clicked')
        if self.thread and self.thread.isRunning():
            return
        self.obj = Proxy()
        self.thread = QThread()
        self.obj.moveToThread(self.thread)
        self.obj.message.connect(self.on_message)
        self.obj.finished.connect(self.on_finished)
        self.thread.started.connect(self.obj.start)
        self.thread.start()

    def on_message(self, message):
        self.log(message, 'Proxy')

    def on_finished(self, message):
        self.thread.quit()
        self.thread.wait()
        self.proxylist = message
        self.loop.run_until_complete(self.save_proxylist())

    async def save_proxylist(self):
        await self.db.executemany('INSERT OR REPLACE INTO proxy (country,host,port,url,response_time) VALUES (?,?,?,?,?)',
            [(proxy['country'], proxy['host'], proxy['port'], proxy['url'], proxy['response_time']) for proxy in self.proxylist])
        await self.db.commit()
        self.log(f'Saved {len(self.proxylist)} proxy')


Main()
