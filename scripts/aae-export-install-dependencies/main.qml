import QtQuick 2.15
import QtQuick.Controls 2.15

ApplicationWindow {
    width: 540
    height: 360
    minimumWidth: 240
    minimumHeight: 160
    visible: true

    title: qsTr("Installing Dependencies for AAE Export")

    Component.onCompleted: {
        // call the QObject to start the process
    }
    onClosing: (close) => {
        // if the installing is in process,
        // SIGINT and exit
        // or if the install fails, exit
        // (close.accepted is true by default)
    }

    ScrollView {
        anchors.fill: parent
        anchors.margins: 12

        focus: true

        TextArea {
            id: text_printout

            anchors.margins: 4
            wrapMode: TextArea.WrapAnywhere

            focus: true
            readOnly: true
            selectByMouse: true // requires Qt 6.4
            selectByKeyboard: true
            mouseSelectionMode: TextEdit.SelectCharacters

            text: printout.text
        }
    }
}
