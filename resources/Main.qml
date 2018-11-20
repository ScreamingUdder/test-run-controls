import QtQuick 2.11
import QtQuick.Controls 2.4

ApplicationWindow {
    title: "Test run controls"
    id: window
    visible: true
    width: 640
    height: 480

    Pane {
        focus: true
        anchors.fill: parent

        Label {
            anchors.verticalCenter: parent.verticalCenter
            anchors.horizontalCenter: parent.horizontalCenter
            text: "Hello World!"
        }
    }
}
