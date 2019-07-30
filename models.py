from PyQt5.QtCore import QAbstractListModel, Qt, pyqtSlot, QModelIndex


class TableModel(QAbstractListModel):
    def __init__(self, *roles):
        super().__init__()
        self.roles = roles
        self.items = []
        self.values = []
        n = 0
        for role in self.roles:
            n += 1
            value = Qt.UserRole + n
            self.values.append(value)
            setattr(self, role+'Role', value)

    def data(self, index, role=Qt.DisplayRole):
        if role in self.values:
            row = index.row()
            index = self.values.index(role)
            name = self.roles[index]
            return self.items[row][name.lower()]

    def rowCount(self, parent=QModelIndex()):
        return len(self.items)

    def roleNames(self):
        ret = {}
        for v in self.values:
            i = self.values.index(v)
            ret[v] = bytes(str(self.roles[i]).lower(), encoding='utf8')
        return ret

    @pyqtSlot()
    def addItem(self, *args):
        ret = {}
        n = 0
        for v in self.values:
            i = self.values.index(v)
            ret[str(self.roles[i]).lower()] = str(args[n])
            n += 1
        self.beginInsertRows(QModelIndex(), self.rowCount(), self.rowCount())
        self.items.append(ret)
        self.endInsertRows()

    @pyqtSlot()
    def clear(self):
        self.beginRemoveRows(QModelIndex(), 0, self.rowCount())
        self.removeRows(0, self.rowCount(), QModelIndex())
        self.endRemoveRows()
        self.items = []
