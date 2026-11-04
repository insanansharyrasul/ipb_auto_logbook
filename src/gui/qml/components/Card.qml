import QtQuick
import QtQuick.Layouts
import "../Theme.js" as Theme

Rectangle {
    id: root

    property string title: ""
    property bool expanded: false
    default property alias content: body.data

    implicitHeight: expanded ? 0 : layout.implicitHeight + Theme.cardPadding * 2
    color: Theme.surface
    radius: Theme.radius
    border.width: 1
    border.color: Theme.border

    ColumnLayout {
        id: layout
        anchors.left: parent.left
        anchors.right: parent.right
        anchors.top: parent.top
        anchors.bottom: root.expanded ? parent.bottom : undefined
        anchors.margins: Theme.cardPadding
        spacing: Theme.spaceMd

        RowLayout {
            visible: root.title !== ""
            Layout.fillWidth: true
            spacing: Theme.spaceSm + 2

            Rectangle {
                Layout.preferredWidth: 3
                Layout.preferredHeight: 18
                radius: 1.5
                color: Theme.accent
            }

            Text {
                text: root.title
                color: Theme.text
                font.pixelSize: Theme.fontSizeTitle
                font.weight: Font.Bold
            }

            Item { Layout.fillWidth: true }
        }

        ColumnLayout {
            id: body
            Layout.fillWidth: true
            Layout.fillHeight: root.expanded
            spacing: Theme.spaceMd
        }
    }
}
