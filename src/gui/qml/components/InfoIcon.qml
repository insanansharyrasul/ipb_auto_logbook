import QtQuick
import QtQuick.Controls
import "../Theme.js" as Theme

Item {
    id: root

    property string text: ""

    implicitWidth: 15
    implicitHeight: 15
    visible: text !== ""

    Rectangle {
        anchors.fill: parent
        radius: width / 2
        color: "transparent"
        border.width: 1.2
        border.color: Theme.info

        Text {
            anchors.centerIn: parent
            text: "i"
            color: Theme.info
            font.pixelSize: 10
            font.weight: Font.Bold
        }
    }

    HoverHandler { id: hover }

    ToolTip.visible: hover.hovered && root.text !== ""
    ToolTip.text: root.text
    ToolTip.delay: 300
}
