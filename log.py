from datetime import datetime
from db import Db
from models import TableModel


class Log(Db):
    def __init__(self):
        self.logModel = TableModel('Time', 'Type', 'Message')
        self.rootContext().setContextProperty('logModel', self.logModel)

    def log(self, message, messageType='System', messageTime=None):
        if not messageTime:
            messageTime = datetime.now().strftime('%H:%M:%S')
        self.logModel.addRow([messageTime, messageType, message])
