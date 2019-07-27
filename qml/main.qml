import QtQuick 2.12
import QtQuick.Window 2.12
import QtQuick.Controls 1.4

Window {
    visible: true
    width: 640
    height: 480
    title: "avito-parser-gui"

    TabView {
        id: tabView
        anchors.fill: parent
        currentIndex: 1
        Tab {
            title: "Parse"
        }
        Tab {
            title: "Proxy"
            Rectangle {
                TableView {
                    id: table
                    model: logModel
                    headerVisible: false
                    alternatingRowColors: false
                    anchors.bottom: parent.bottom
                    width: parent.width
                    height: 300
                    TableViewColumn {
                        role: "time"
                        width: 100
                    }
                    TableViewColumn {
                        role: "type"
                        width: 100
                    }
                    TableViewColumn {
                        role: "message"
                        width: table.width - 220
                    }
                    Timer {
                        id: timer
                        interval: 0
                        onTriggered: {
                            table.positionViewAtRow(table.rowCount-1, TableView.End)
                            stop()
                        }
                    }
                    onRowCountChanged: {
                        timer.start()
                    }

                }

                Button {
                    objectName: "btn"
                    x: 24
                    y: 24
                    text: "Update"
                }

            }
        }
    }

}
