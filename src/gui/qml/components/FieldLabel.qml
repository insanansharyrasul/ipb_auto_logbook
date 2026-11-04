import QtQuick
import QtQuick.Layouts
import "../Theme.js" as Theme
import "."

Item {
    id: root

    property string text: ""
    property string info: ""

    implicitWidth: Theme.labelWidth
    implicitHeight: Math.max(label.implicitHeight, infoIcon.implicitHeight)

    RowLayout {
        anchors.left: parent.left
        anchors.verticalCenter: parent.verticalCenter
        spacing: Theme.spaceSm - 2

        Text {
            id: label
            text: root.text
            color: Theme.text
            font.pixelSize: Theme.fontSize
        }

        InfoIcon {
            id: infoIcon
            text: root.info
            visible: root.info !== ""
        }
    }
}
