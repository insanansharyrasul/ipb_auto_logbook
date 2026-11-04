import QtQuick
import QtQuick.Controls
import "../Theme.js" as Theme

SpinBox {
    id: root

    implicitHeight: Theme.controlHeight
    font.pixelSize: Theme.fontSize

    background: Rectangle {
        radius: Theme.radiusSm
        color: Theme.surface
        border.width: 1
        border.color: root.activeFocus ? Theme.accent : Theme.border

        Rectangle {
            x: parent.width - 29
            y: 1
            width: 1
            height: parent.height - 2
            color: Theme.border
        }
    }

    contentItem: TextInput {
        text: root.displayText
        color: Theme.text
        font: root.font
        leftPadding: Theme.spaceMd
        rightPadding: 38
        verticalAlignment: Text.AlignVCenter
        readOnly: !root.editable
        validator: root.validator
        inputMethodHints: root.inputMethodHints
        selectByMouse: true
        selectionColor: Theme.accent
        selectedTextColor: Theme.surface
    }

    up.indicator: Rectangle {
        x: root.width - width
        y: 1
        width: 28
        height: (root.height - 2) / 2
        color: root.up.pressed ? Theme.surfaceHover : "transparent"

        Text {
            anchors.centerIn: parent
            text: "▴"
            color: Theme.muted
            font.pixelSize: 9
        }
    }

    down.indicator: Rectangle {
        x: root.width - width
        y: root.height / 2
        width: 28
        height: root.height / 2 - 1
        color: root.down.pressed ? Theme.surfaceHover : "transparent"

        Text {
            anchors.centerIn: parent
            text: "▾"
            color: Theme.muted
            font.pixelSize: 9
        }
    }
}
