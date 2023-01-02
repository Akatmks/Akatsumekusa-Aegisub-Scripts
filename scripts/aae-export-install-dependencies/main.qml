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
        // if the installing is in process, do
        // close.accepted = false
        // or if the install fails, do nothing
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

            text: "Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum."
        }
    }
}
