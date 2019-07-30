from log import Log
from models import TableModel
from PyQt5.QtCore import QThread, QObject, pyqtSignal, pyqtSlot
import aiohttp
import asyncio
import time


class Proxylist(Log):
    proxy_model = TableModel('Id', 'Country', 'Url', 'Response_time', 'Used', 'Error')
    proxylist_obj = proxylist_thread = None
    proxylist = []

    def __init__(self):
        super().__init__()
        self.rootContext().setContextProperty('proxyModel', self.proxy_model)

    async def proxylist_init(self):
        cursor = await self.db.execute('SELECT * FROM proxy')
        proxylist = await cursor.fetchall()
        if proxylist:
            for p in proxylist:
                self.proxylist.append({'id': p[0], 'added': p[1], 'country': p[2], 'host': p[3], 'port': p[4], 'url': p[5], 'response_time': p[6], 'used': p[7], 'error': p[8]})
                self.proxy_model.addItem(p[0], p[2], p[5], f'{p[6]:.2f}', p[7], p[8])
            self.log(f'Load {len(self.proxylist)} proxy', 'Proxylist')

    async def proxylist_close(self):
        if self.proxylist:
            await self.db.executemany('UPDATE proxy SET used=?, error=? WHERE id=?',
                [(proxy['used'], proxy['error'], proxy['id']) for proxy in self.proxylist])
            await self.db.commit()

    def proxylist_update(self):
        if self.proxylist_thread and self.proxylist_thread.isRunning():
            return
        self.log('Start update proxylist', 'Proxylist')
        self.proxy_model.clear()
        self.proxylist = []
        self.proxylist_obj = ProxylistUpdate()
        self.proxylist_thread = QThread()
        self.proxylist_obj.moveToThread(self.proxylist_thread)
        self.proxylist_obj.message.connect(self.proxylist_on_message)
        self.proxylist_obj.finished.connect(self.proxylist_on_finished)
        self.proxylist_thread.started.connect(self.proxylist_obj.start)
        self.proxylist_thread.start()

    async def proxylist_save(self):
        await self.db.executemany('INSERT OR REPLACE INTO proxy (country,host,port,url,response_time) VALUES (?,?,?,?,?)',
            [(proxy['country'], proxy['host'], proxy['port'], proxy['url'], proxy['response_time']) for proxy in self.proxylist])
        await self.db.commit()
        self.log(f'Save {len(self.proxylist)} proxy', 'Proxylist')

    async def proxylist_clear(self):
        self.proxy_model.clear()
        self.proxylist = []
        await self.db.execute(f'DELETE FROM proxy')
        await self.db.execute(f'DELETE FROM sqlite_sequence WHERE name="proxy"')
        await self.db.commit()
        self.log('Clear proxylist', 'Proxylist')

    def proxylist_on_message(self, message):
        if message[0]:
            self.log(message[0], 'Proxylist')
        if message[1]:
            proxy = message[1]
            self.proxy_model.addItem(proxy['id']+1, proxy['country'], proxy['url'], f'{proxy["response_time"]:.2f}', proxy['used'], proxy['error'])

    def proxylist_on_finished(self, message):
        self.proxylist_thread.quit()
        self.proxylist_thread.wait()
        self.proxylist = message
        self.loop.run_until_complete(self.proxylist_save())


class ProxylistUpdate(QObject):
    message = pyqtSignal(list)
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

    def log(self, message, data=None):
        self.message.emit([message, data])

    async def _start(self):
        start = time.time()
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
                    proxy['used'] = 0
                    proxy['error'] = 0

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

                    self.log('[{id}/{index}] {country} {url}  {response_time:.2f} sec'.format(**proxy), proxy)

                    self.check_proxylist.append(proxy)
        except:
            pass

        self.checking -= 1
