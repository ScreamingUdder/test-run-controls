import QtQuick 2.11
import QtQuick.Controls 2.4
import QtQuick.Dialogs 1.3
import Kafka 1.0

ApplicationWindow {
    title: "Test run controls"
    id: window
    visible: true
    width: 640
    height: 480

    Pane {
        focus: true
        anchors.fill: parent

        LabeledTextField {
            id: instrumentField
            anchors.top: parent.top
            anchors.right: parent.right
            editorWidth: 300
            labelText: "Instrument name:"
            editorText: kafka.instrument
            onEditingFinished: kafka.instrument = editorText
        }
        LabeledTextField {
            id: brokerField
            anchors.top: instrumentField.bottom
            anchors.right: parent.right
            editorWidth: 300
            labelText: "Broker address:"
            editorText: kafka.broker
            onEditingFinished: kafka.broker = editorText
        }
        LabeledTextField {
            id: brokerVersionField
            anchors.top: brokerField.bottom
            anchors.right: parent.right
            editorWidth: 300
            labelText: "Broker version:"
            editorText: kafka.version
            onEditingFinished: kafka.version = editorText
        }

        Frame {
            id: startRunContainer
            anchors.top: brokerVersionField.bottom
            anchors.left: parent.left
            anchors.right: parent.right
            contentHeight: runNumberField.height + filenameField.height

            property int runNumber: 1
            property url mappingFile

            Button {
                anchors.verticalCenter: runNumberField.verticalCenter
                anchors.left: parent.left
                id: startRunButton
                text: "Start run"
                onClicked: kafka.start_run(startRunContainer.runNumber, startRunContainer.mappingFile)
            }

            // Field for run number
            LabeledTextField {
                id: runNumberField
                anchors.top: parent.top
                anchors.right: filenameField.right
                labelText: "Run number:"
                editorText: startRunContainer.runNumber
                onEditingFinished: startRunContainer.runNumber = parseInt(editorText)
                validator: IntValidator {}
            }

            // Field for detector spectrum mapping file
            LabeledTextField {
                id: filenameField
                anchors.top: runNumberField.bottom
                anchors.left: parent.left
                labelText: "Detector spectrum mapping file:"
                editorText: startRunContainer.mappingFile
                editorWidth: 300
                enabled: false
            }

            Button {
                anchors.verticalCenter: filenameField.verticalCenter
                anchors.left: filenameField.right
                text: "Choose file"
                onClicked: spectrumMappingFileDialog.open()
            }

            FileDialog {
                id: spectrumMappingFileDialog
                title: "Detector spectrum mapping file"
                nameFilters: ["DAT files (*.dat *.DAT)", "All files (*)"]
                onAccepted: startRunContainer.mappingFile = fileUrl
            }
        }

        Frame {
            id: stopRunContainer
            anchors.top: startRunContainer.bottom
            anchors.left: parent.left
            anchors.right: parent.right
            contentHeight: stopRunNumberField.height

            property int runNumber: 1
            property url mappingFile

            Button {
                anchors.verticalCenter: stopRunNumberField.verticalCenter
                anchors.left: parent.left
                id: stopRunButton
                text: "Stop run"
                onClicked: kafka.stop_run(stopRunContainer.runNumber, stopRunContainer.mappingFile)
            }

            // Field for run number
            LabeledTextField {
                id: stopRunNumberField
                anchors.top: parent.top
                anchors.right: parent.right
                labelText: "Run number:"
                editorText: stopRunContainer.runNumber
                onEditingFinished: stopRunContainer.runNumber = parseInt(editorText)
                validator: IntValidator {}
            }
        }
    }

    KafkaConnector {
        id: kafka
    }
}
