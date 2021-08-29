import QtQuick 2.12
import QtQuick.Controls 2.12

Rectangle {
    width: 300
    height: 200
    color: "black"

    property int blockHeight

    Label {
        anchors.centerIn: parent
        color: "orange"
        font.pixelSize: 30
        text: parent.blockHeight
    }
}
