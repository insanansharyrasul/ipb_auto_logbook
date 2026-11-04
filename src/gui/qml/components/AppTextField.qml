import QtQuick
import QtQuick.Controls
import "../Theme.js" as Theme

TextField {
    id: root

    property bool compact: false

    implicitHeight: compact ? 34 : Theme.controlHeight
    leftPadding: Theme.spaceMd
    rightPadding: Theme.spaceMd
    color: Theme.text
    placeholderTextColor: Theme.placeholder
    selectionColor: Theme.accent
    selectedTextColor: Theme.surface
    font.pixelSize: compact ? Theme.fontSizeSmall : Theme.fontSize

    background: Rectangle {
        radius: root.compact ? Theme.radiusXs : Theme.radiusSm
        color: root.readOnly ? Theme.navBackground : Theme.surface
        border.width: 1
        border.color: root.activeFocus
                      ? Theme.accent
                      : (root.hovered ? Theme.borderStrong : Theme.border)
    }
}
