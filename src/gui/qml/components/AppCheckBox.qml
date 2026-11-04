import QtQuick
import QtQuick.Controls
import "../Theme.js" as Theme

CheckBox {
    id: root

    spacing: Theme.spaceSm
    font.pixelSize: Theme.fontSize
    topPadding: 0
    bottomPadding: 0

    indicator: Rectangle {
        implicitWidth: 18
        implicitHeight: 18
        x: 0
        y: (root.availableHeight - height) / 2
        radius: 4
        color: root.checked ? Theme.accent : Theme.surface
        border.width: 1
        border.color: root.checked ? Theme.accent : Theme.borderStrong

        Text {
            visible: root.checked
            anchors.centerIn: parent
            text: "✓"
            color: Theme.surface
            font.pixelSize: 12
            font.weight: Font.Bold
        }
    }

    contentItem: Text {
        text: root.text
        color: Theme.text
        font.pixelSize: Theme.fontSize
        leftPadding: root.indicator.width + root.spacing
        verticalAlignment: Text.AlignVCenter
    }
}
