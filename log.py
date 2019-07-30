from datetime import datetime
from db import Db
from models import TableModel


class Log(Db):
    log_model = TableModel('Time', 'Type', 'Message')

    def __init__(self):
        self.rootContext().setContextProperty('logModel', self.log_model)

    def log(self, message, messageType='System', messageTime=None):
        if not messageTime:
            messageTime = datetime.now().strftime('%H:%M:%S')
        self.log_model.addItem(messageTime, messageType, message)
