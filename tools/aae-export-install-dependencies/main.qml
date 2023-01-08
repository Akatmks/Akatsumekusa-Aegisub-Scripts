/* aae-export-install-dependencies
 * Copyright (c) Akatsumekusa and contributors
 *
 * Permission is hereby granted, free of charge, to any person obtaining a copy
 * of this software and associated documentation files (the "Software"), to deal
 * in the Software without restriction, including without limitation the rights
 * to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
 * copies of the Software, and to permit persons to whom the Software is
 * furnished to do so, subject to the following conditions:
 *
 * The above copyright notice and this permission notice shall be included in all
 * copies or substantial portions of the Software.
 *
 * THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
 * IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
 * FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
 * AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
 * LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
 * OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
 * SOFTWARE.
 */

import QtQuick 2.15
import QtQuick.Controls 2.15

ApplicationWindow {
    width: 720
    height: 480
    minimumWidth: 240
    minimumHeight: 160
    visible: true

    title: qsTr("Installing Dependencies for AAE Export")

    Component.onCompleted: {
        process.run()
    }
    onClosing: (close) => {
        process.term()
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

            text: process.printout
        }
    }
}
