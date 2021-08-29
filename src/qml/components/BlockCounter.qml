import QtQuick 2.12
import QtQuick.Controls 2.12

Rectangle {
    color: "black"
    width: label.width * 1.5

    property int blockHeight

    Label {
        id: label
        anchors.centerIn: parent
        color: "orange"
        font.pixelSize: parent.height / 3
        text: parent.blockHeight
    }
}
