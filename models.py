from PyQt5.QtCore import QAbstractListModel, Qt, pyqtSlot, QModelIndex


class LogModel(QAbstractListModel):
    TimeRole = Qt.UserRole + 1
    TypeRole = Qt.UserRole + 2
    MessageRole = Qt.UserRole + 3

    items = []

    def __init__(self):
        super().__init__()
        # self.items =  [{'time': '__:__:__', 'type': '', 'message': 'Lorem ipsum dolor sit amet, consectetur adipisicing elit. Dolores debitis minima iure fugit voluptates sit, tenetur beatae iusto officiis necessitatibus cupiditate quibusdam voluptas nulla quos ratione animi repellendus ipsam. Eos.'} for _ in range(20)]

    def data(self, index, role=Qt.DisplayRole):
        row = index.row()
        if role == LogModel.TimeRole:
            return self.items[row]['time']
        if role == LogModel.TypeRole:
            return self.items[row]['type']
        if role == LogModel.MessageRole:
            return self.items[row]['message']

    def rowCount(self, parent=QModelIndex()):
        return len(self.items)

    def roleNames(self):
        return {
            LogModel.TimeRole: b'time',
            LogModel.TypeRole: b'type',
            LogModel.MessageRole: b'message'
        }

    @pyqtSlot(str, str, str)
    def addItem(self, time, type, message):
        self.beginInsertRows(QModelIndex(), self.rowCount(), self.rowCount())
        self.items.append({'time': time, 'type': type, 'message': message})
        self.endInsertRows()
