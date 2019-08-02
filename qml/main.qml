import QtQuick 2.12
import QtQuick.Window 2.12
import QtQuick.Layouts 1.3
import QtQuick.Controls 2.3
import QtQuick.Controls 1.6 as C


Window {
    visible: true
    width: 1400
    height: 700
    minimumWidth: 640
    minimumHeight: 480
    title: "avito-parser"
    color: "#191919"
    ColumnLayout {
        anchors.fill: parent
        spacing: 0
        Rectangle {
            Layout.fillWidth: true
            height: 40
            color: "#191919"
            Rectangle {
                id: rectangle
                anchors.right: parent.right
                anchors.rightMargin: 20
                anchors.verticalCenter: parent.verticalCenter
                width: 300
                height: 25
                color: "#191919"
                border.color: "#303030"
                clip: true
                TextInput {
                    topPadding: 3
                    leftPadding: 10
                    rightPadding: 10
                    anchors.verticalCenter: parent.verticalCenter
                    width: parent.width
                    height: 20
                    color: "#aaa"
                    text: "Search..."
                    selectionColor: "#8383f3"
                    renderType: Text.NativeRendering
                }
            }
        }
        RowLayout{
            property var index: 0
            id: menu
            Layout.fillWidth: true
            Layout.fillHeight: true
            spacing: 0
            Rectangle {
                width: 220
                Layout.fillHeight: true
                color: "#191919"
                Column {
                    width: parent.width
                    spacing: 10
                    Button {
                        id: btn1
                        text: "Parser"
                        x: 10
                        width: 200
                        height: 30
                        onClicked: {
                            if (highlighted == true) {
                                highlighted = false
                                menu.index = 0
                                btn2.highlighted = true
                            }
                        }
                    }
                    Button {
                        id: btn2
                        text: "Proxylist"
                        x: 10
                        width: 200
                        height: 30
                        highlighted: true
                        onClicked: {
                            if (highlighted == true) {
                                highlighted = false
                                menu.index = 1
                                btn1.highlighted = true
                            }
                        }
                    }
                }
            }
            Rectangle {
                Layout.fillWidth: true
                Layout.fillHeight: true
                color: "#202020"
                SwipeView {
                    anchors.fill: parent
                    clip: true
                    currentIndex: menu.index
                    interactive: false
                    Item {
                        Item {
                            anchors.margins: 20
                            anchors.fill: parent
                            RowLayout {
                                anchors.fill: parent
                                spacing: 10
                                Rectangle {
                                    Layout.alignment: Qt.AlignTop
                                    width: 80
                                    Button {
                                        width: 70
                                        height: 30
                                        text: "Parse"
                                        onClicked: self.click('parse')
                                    }
                                }
                                Rectangle {
                                    Layout.fillWidth: true
                                    Layout.fillHeight: true
                                    color: "#202020"
                                    border.color: "#303030"
                                    C.TableView {
                                        id: itemsTable
                                        model: sortItemsModel
                                        anchors.fill: parent
                                        anchors.margins: 1
                                        frameVisible: false
                                        alternatingRowColors: false
                                        backgroundVisible: false
                                        sortIndicatorVisible: true
                                        onSortIndicatorOrderChanged: model.sort(sortIndicatorColumn, sortIndicatorOrder)
                                        onSortIndicatorColumnChanged: model.sort(sortIndicatorColumn, sortIndicatorOrder)
                                        rowDelegate: Rectangle {
                                            height: 20
                                            color: styleData.selected ? "#777777" : "#202020"
                                        }
                                        itemDelegate: Rectangle {
                                            clip: true
                                            color: "transparent"
                                            Text {
                                                anchors.fill: parent
                                                anchors.leftMargin: 12
                                                verticalAlignment: Text.AlignVCenter
                                                color: "#aaa"
                                                text: styleData.value
                                                renderType: Text.NativeRendering
                                            }
                                        }
                                        C.TableViewColumn {
                                            role: "id"
                                            title: "#"
                                            width: 50
                                        }
                                        C.TableViewColumn {
                                            role: "dt"
                                            title: "Datetime"
                                        }
                                        C.TableViewColumn {
                                            role: "name"
                                            title: "Name"
                                        }
                                        C.TableViewColumn {
                                            role: "price"
                                            title: "Price"
                                        }
                                        C.TableViewColumn {
                                            role: "author"
                                            title: "Author"
                                        }
                                        C.TableViewColumn {
                                            role: "address"
                                            title: "Address"
                                        }
                                        C.TableViewColumn {
                                            role: "phone"
                                            title: "Phone"
                                        }
                                    }
                                }
                            }
                        }
                    }
                    Item {
                        Item {
                            anchors.margins: 20
                            anchors.fill: parent
                            RowLayout {
                                anchors.fill: parent
                                spacing: 10
                                Rectangle {
                                    Layout.alignment: Qt.AlignTop
                                    width: 230
                                    RowLayout {
                                        spacing: 5
                                        Button {
                                            Layout.preferredWidth: 70
                                            Layout.preferredHeight: 30
                                            text: "Update"
                                            onClicked: self.click('proxylist_update')
                                        }
                                        Button {
                                            Layout.preferredWidth: 70
                                            Layout.preferredHeight: 30
                                            text: "Clear"
                                            onClicked: self.click('proxylist_clear')
                                        }
                                        Button {
                                            Layout.preferredWidth: 70
                                            Layout.preferredHeight: 30
                                            text: "..."
                                        }
                                    }
                                }
                                Rectangle {
                                    Layout.fillWidth: true
                                    Layout.fillHeight: true
                                    color: "#202020"
                                    border.color: "#303030"
                                    C.TableView {
                                        id: proxyTable
                                        model: sortProxyModel
                                        anchors.fill: parent
                                        anchors.margins: 1
                                        frameVisible: false
                                        alternatingRowColors: false
                                        backgroundVisible: false
                                        sortIndicatorVisible: true
                                        onSortIndicatorOrderChanged: model.sort(sortIndicatorColumn, sortIndicatorOrder)
                                        onSortIndicatorColumnChanged: model.sort(sortIndicatorColumn, sortIndicatorOrder)
                                        rowDelegate: Rectangle {
                                            height: 20
                                            color: styleData.selected ? "#777777" : "#202020"
                                        }
                                        itemDelegate: Rectangle {
                                            color: "transparent"
                                            Text {
                                                anchors.fill: parent
                                                anchors.leftMargin: 12
                                                verticalAlignment: Text.AlignVCenter
                                                color: "#aaa"
                                                text: styleData.value
                                                renderType: Text.NativeRendering
                                            }
                                        }
                                        C.TableViewColumn {
                                            role: "id"
                                            title: "#"
                                            width: 50
                                        }
                                        C.TableViewColumn {
                                            role: "country"
                                            title: "Country"
                                        }
                                        C.TableViewColumn {
                                            role: "url"
                                            title: "Url"
                                        }
                                        C.TableViewColumn {
                                            role: "response_time"
                                            title: "Time"
                                        }
                                        C.TableViewColumn {
                                            role: "used"
                                            title: "Used"
                                        }
                                        C.TableViewColumn {
                                            role: "error"
                                            title: "Error"
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            }
        }
        Rectangle {
            Layout.fillWidth: true
            height: 150
            color: "#191919"
            C.TableView {
                id: logTable
                model: logModel
                anchors.fill: parent
                backgroundVisible: false
                headerVisible: false
                alternatingRowColors: false
                frameVisible: false
                rowDelegate: Rectangle {
                    height: 20
                    color: "#191919"
                }
                itemDelegate: Rectangle {
                    color: "#191919"
                    Text {
                        anchors.verticalCenter: parent.verticalCenter
                        color: "#aaa"
                        text: styleData.value
                    }
                }
                C.TableViewColumn {
                    role: "time"
                }
                C.TableViewColumn {
                    role: "type"
                }
                C.TableViewColumn {
                    role: "message"
                }
                Timer {
                    id: logTimer
                    interval: 0
                    onTriggered: {
                        logTable.positionViewAtRow(logTable.rowCount-1, TableView.End)
                        stop()
                    }
                }
                onRowCountChanged: {
                    logTimer.start()
                }
            }
        }
        Rectangle {
            Layout.fillWidth: true
            height: 20
            color: "#333333"
            Text {
                anchors.fill: parent
                anchors.leftMargin: 10
                renderType: Text.NativeRendering
                text: "Ready"
                color: "#aaa"
                verticalAlignment: Text.AlignVCenter
            }
        }
    }
}
