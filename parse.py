from datetime import datetime, timedelta
from models import TableModel
from proxylist import Proxylist
from PyQt5.QtCore import QThread, QObject, pyqtSignal, pyqtSlot
import aiohttp
import asyncio
import lxml.html as html
import random
import time


class Parse(Proxylist):
    items_model = TableModel('Id', 'Dt', 'Name', 'Price', 'Author', 'Address', 'Phone')
    parse_obj = parse_thread = None
    items = []

    def __init__(self):
        super().__init__()
        self.rootContext().setContextProperty('itemsModel', self.items_model)

    def parse(self):
        if self.parse_thread and self.parse_thread.isRunning():
            return
        self.log('Start parsing', 'Parse')
        self.items = []
        self.parse_obj = ParseWorker(self.proxylist)
        self.parse_thread = QThread()
        self.parse_obj.moveToThread(self.parse_thread)
        self.parse_obj.message.connect(self.parse_on_message)
        self.parse_obj.finished.connect(self.parse_on_finished)
        self.parse_thread.started.connect(self.parse_obj.start)
        self.parse_thread.start()

    def parse_on_message(self, message):
        if message[0]:
            self.log(message[0], 'Parse')
        if message[1]:
            item = message[1]
            self.items_model.addItem(item['id']+1, item['dt'], item['name'], item['price'], item['author'], item['address'], item['phone'])

    def parse_on_finished(self, message):
        self.parse_thread.quit()
        self.parse_thread.wait()
        self.items = message[0]
        self.proxylist = message[1]


class ParseWorker(QObject):
    message = pyqtSignal(list)
    finished = pyqtSignal(list)
    options = {
        'timeout': 2
    }
    items = []

    def __init__(self, proxylist):
        super().__init__()
        self.proxylist = proxylist

    @pyqtSlot()
    def start(self):
        asyncio.run(self._start())
        self.finished.emit([self.items, self.proxylist])

    def log(self, message, data={}):
        self.message.emit([message, data])

    async def _start(self):
        urls = [
            '/odintsovo?sort=date',
            '/golitsyno?sort=date',
            '/lesnoy_gorodok?sort=date',
            '/kubinka?sort=date',
            '/bolshie_vyazemy?sort=date',
            '/gorki-10?sort=date',
            '/zvenigorod?sort=date',
            '/moskovskaya_oblast_krasnoznamensk?sort=date',
            '/novoivanovskoe?sort=date',

            '/odintsovo/transport?sort=date',
            '/odintsovo/bytovaya_elektronika?sort=date',
            '/odintsovo/hobbi_i_otdyh?sort=date',

            '/moskva_i_mo?sort=date'
        ]

        async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(ssl=False)) as session:
            await asyncio.gather(*[self.get_head(session, url) for url in urls])

    def get_proxy(self):
        return self.proxylist[random.randint(0, len(self.proxylist)-1)]

    async def get_head(self, session, url, timeout=None):
        start = time.time()
        if not timeout:
            timeout = self.options['timeout']

        proxy = self.get_proxy()
        data = await self.get_html(session, 'https://m.avito.ru' + url, proxy['url'], timeout)

        if data:
            dom = html.fromstring(data)
            urls = dom.xpath('//a[@itemprop="url"]/@href')

            if len(urls) == 0:
                proxy['error'] += 1
                return
            else:
                proxy['used'] += 1
                self.log(f'{len(urls)} from [{proxy["id"]:3d}|{proxy["used"]:3d}|{proxy["error"]:2d}|{len(data):6d}|{time.time()-start:.2f}] {url}')
                await asyncio.gather(*[self.get_page(session, url) for url in urls])
        else:
            proxy['error'] += 1

    async def get_page(self, session, url, timeout=None):
        proxy = self.get_proxy()
        if not timeout:
            timeout = self.options['timeout']

        data = await self.get_html(session, 'https://m.avito.ru' + url, proxy['url'], timeout)
        if data:
            proxy['used'] += 1
            await self.extract_data(url, data)
        else:
            proxy['error'] += 1

    async def get_html(self, session, url, proxy_url, timeout):
        try:
            async with session.get(url, proxy=proxy_url, timeout=timeout) as response:
                return await response.text()
        except:
            return False

    async def extract_data(self, url, data):
        dom = html.fromstring(data)

        item = {
            'id': len(self.items),
            'dt': self.extract_datetime(self.xpath(dom, '//div[@data-marker="item-stats/timestamp"]/span/text()')),
            'url': url,
            'name': self.xpath(dom, '//h1[@data-marker="item-description/title"]/span/text()'),
            'price': self.xpath(dom, '//span[@data-marker="item-description/price"]/text()'),
            'desc': self.xpath(dom, '//div[@data-marker="item-description/text"]/text()'),
            'author': self.xpath(dom, '//span[@data-marker="seller-info/name"]/text()'),
            'author_postfix': self.xpath(dom, '//span[@data-marker="seller-info/postfix"]/text()'),
            'author_summary': self.xpath(dom, '//span[@data-marker="seller-info/summary"]/text()').split(),

            'address': self.xpath(dom, '//span[@data-marker="delivery/location"]/text()'),
            'phone': self.xpath(dom, '//a[@data-marker="item-contact-bar/call"]/@href'),

            'avatar': self.xpath(dom, '//div[@data-marker="avatar-seller-info"]/img/@src'),

            'stats': self.xpath(dom, '//div[@data-marker="item-stats/views"]'),
            'timestamp': self.xpath(dom, '//div[@data-marker="item-stats/timestamp"]')
        }

        if item['author_summary']:
            item['author_summary'] = item['author_summary'][0]
        else:
            item['author_summary'] = 0

        if item['phone'].strip() != '':
            item['phone'] = item['phone'].replace('tel:', '')
            if len(item['phone']) > 12:
                item['phone'] = ''

        if item['stats'] != '':
            item['stats'] = item['stats'].text_content()

        if item['timestamp'] != '':
            item['timestamp'] = item['timestamp'].text_content()

        if item['phone'] != '':
            self.items.append(item)
            self.log('', item)

    def extract_datetime(self, dt):
        # Сегодня, 10:32
        # Вчера, 16:04
        # 12 июля, 18:14
        if dt.strip() == '':
            return datetime.strftime(datetime.now(), '%Y-%m-%d %H:%M:%S')
        if 'Сегодня' in dt:
            dt = dt.replace('Сегодня,', datetime.strftime(datetime.now(), '%Y-%m-%d')) + ':00'
            dt = datetime.strptime(dt, '%Y-%m-%d %H:%M:%S')
        elif 'Вчера' in dt:
            dt = dt.replace('Вчера,', datetime.strftime(datetime.now() - timedelta(days=1), '%Y-%m-%d')) + ':00'
        else:
            dt = dt.replace(',', '')
            dt = dt.split()
            month = ['января', 'февраля', 'марта', 'апреля', 'мая', 'июня', 'июля', 'августа', 'сентября', 'октября', 'ноября', 'декабря'].index(dt[1]) + 1
            dt = f'{datetime.strftime(datetime.now(), "%Y")}-{month}-{dt[0]} {dt[2]}:00'
            dt = datetime.strptime(dt, '%Y-%m-%d %H:%M:%S')
        return dt

    def xpath(self, dom, query):
        tmp = dom.xpath(query)
        if tmp:
            return tmp[0]
        return ''
