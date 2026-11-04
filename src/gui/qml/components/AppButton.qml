import QtQuick
import QtQuick.Controls
import "../Theme.js" as Theme

Button {
    id: root

    property string variant: "outline" // primary | outline | success | danger
    property bool compact: false

    implicitHeight: compact ? 32 : Theme.controlHeight
    leftPadding: compact ? Theme.spaceSm : Theme.spaceLg
    rightPadding: compact ? Theme.spaceSm : Theme.spaceLg
    font.pixelSize: compact ? Theme.fontSizeSmall : Theme.fontSize
    font.weight: Font.DemiBold

    readonly property color foreground: {
        if (variant === "primary" || variant === "success" || variant === "danger")
            return Theme.surface
        return Theme.textSoft
    }
    readonly property color fill: {
        if (variant === "primary")
            return root.pressed ? Theme.accentPressed : (root.hovered ? Theme.accentHover : Theme.accent)
        if (variant === "success")
            return root.pressed ? Theme.successPressed : (root.hovered ? Theme.successHover : Theme.success)
        if (variant === "danger")
            return root.pressed ? Theme.dangerPressed : (root.hovered ? Theme.dangerHover : Theme.danger)
        return root.pressed ? Theme.border : (root.hovered ? Theme.surfaceHover : Theme.surface)
    }

    contentItem: Text {
        text: root.text
        color: root.foreground
        font: root.font
        horizontalAlignment: Text.AlignHCenter
        verticalAlignment: Text.AlignVCenter
    }

    background: Rectangle {
        radius: Theme.radiusSm
        color: root.fill
        border.width: root.variant === "outline" ? 1 : 0
        border.color: Theme.borderStrong
    }
}
