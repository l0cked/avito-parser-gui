from PyQt5.QtCore import Qt, pyqtSlot, QModelIndex, QSortFilterProxyModel, QAbstractItemModel, QAbstractListModel, QDateTime


class TableModel(QAbstractListModel):
    def __init__(self, *roles):
        super().__init__()
        self.roles = {}
        self.rows = []
        n = 0
        for role in roles:
            n += 1
            value = Qt.UserRole + n
            setattr(self, role+'Role', value)
            self.roles[value] = bytes(role.lower(), encoding='utf8')

    def roleNames(self):
        return self.roles

    def rowCount(self, parent=QModelIndex()):
        return len(self.rows)

    def data(self, index, role=Qt.DisplayRole):
        if role in self.roles:
            ret = self.rows[index.row()][self.roles[role].decode()]
            if type(ret) == QDateTime:
                return ret.toString('dd-MM-yyyy HH:mm:ss')
            return ret

    @pyqtSlot(tuple)
    def addRow(self, row):
        self.addRows([row])

    @pyqtSlot(list)
    def addRows(self, rows):
        self.beginInsertRows(QModelIndex(), self.rowCount(), self.rowCount())
        for row in rows:
            newrow = {}
            n = 0
            for key, role in self.roles.items():
                value = None
                data = row[n]
                try:
                    value = float(data)
                except:
                    value = QDateTime.fromString(str(data), 'yyyy-MM-dd hh:mm:ss')
                    if not value:
                        value = str(data)
                newrow[role.decode()] = value
                n += 1
            self.rows.append(newrow)
        self.endInsertRows()

    @pyqtSlot()
    def clear(self):
        self.beginRemoveRows(QModelIndex(), 0, self.rowCount())
        self.removeRows(0, self.rowCount(), QModelIndex())
        self.endRemoveRows()
        self.rows = []


class SortFilterProxyModel(QSortFilterProxyModel):
    def __init__(self, source):
        super().__init__()
        self.setSourceModel(source)
        self.source = source

    @pyqtSlot(int, int)
    def sort(self, column, order):
        key = list(self.source.roles)[column]

        self.currentSortRole = self.source.roles[key].decode()

        self.setSortRole(key)
        super().sort(0, order)

    def lessThan(self, left, right):
        if self.source.rows[left.row()][self.currentSortRole] < self.source.rows[right.row()][self.currentSortRole]:
            return True
        return False
