import QtQuick
import QtQuick.Controls
import "../Theme.js" as Theme

ComboBox {
    id: root

    property bool compact: false

    implicitHeight: compact ? 34 : Theme.controlHeight
    font.pixelSize: compact ? Theme.fontSizeSmall : Theme.fontSize
    leftPadding: Theme.spaceMd - 2
    rightPadding: 28

    background: Rectangle {
        radius: compact ? Theme.radiusXs : Theme.radiusSm
        color: Theme.surface
        border.width: 1
        border.color: root.hovered ? Theme.borderStrong : Theme.border
    }

    contentItem: Text {
        text: root.displayText
        color: Theme.text
        font: root.font
        verticalAlignment: Text.AlignVCenter
        elide: Text.ElideRight
    }

    indicator: Text {
        x: root.width - width - Theme.spaceSm
        y: (root.height - height) / 2
        text: "▾"
        color: Theme.muted
        font.pixelSize: 12
    }
}
