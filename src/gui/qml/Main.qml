pragma ComponentBehavior: Bound
import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import App 1.0
import "Theme.js" as Theme
import "pages"

ApplicationWindow {
    id: window

    width: 1080
    height: 900
    minimumWidth: 900
    minimumHeight: 640
    visible: true
    title: "IPB Auto Logbook v" + Controller.appVersion
    color: Theme.background

    property int currentTab: 0

    readonly property var tabs: [
        { label: "Configuration", icon: "icons/settings.svg" },
        { label: "Logbook Data", icon: "icons/table.svg" },
        { label: "Run", icon: "icons/play.svg" },
        { label: "About", icon: "icons/info.svg" }
    ]

    onClosing: Controller.shutdown()

    header: Rectangle {
        height: 58
        color: Theme.navBackground

        RowLayout {
            anchors.fill: parent
            anchors.leftMargin: Theme.pageMargin
            anchors.rightMargin: Theme.pageMargin
            spacing: Theme.spaceXs

            Repeater {
                model: window.tabs

                Item {
                    id: tab
                    required property int index
                    required property var modelData

                    readonly property bool tabEnabled: index === 2 || !Controller.running
                    readonly property bool active: window.currentTab === index

                    Layout.fillHeight: true
                    Layout.preferredWidth: tabContent.implicitWidth + Theme.spaceXl
                    opacity: tabEnabled ? 1 : 0.4

                    RowLayout {
                        id: tabContent
                        anchors.centerIn: parent
                        spacing: Theme.spaceSm

                        Image {
                            source: tab.modelData.icon
                            sourceSize.width: 18
                            sourceSize.height: 18
                            opacity: tab.active ? 1 : 0.75
                            Layout.alignment: Qt.AlignVCenter
                        }

                        Text {
                            text: tab.modelData.label
                            color: tab.active ? Theme.text : Theme.muted
                            font.pixelSize: Theme.fontSize
                            font.weight: tab.active ? Font.DemiBold : Font.Normal
                        }
                    }

                    Rectangle {
                        anchors.left: parent.left
                        anchors.right: parent.right
                        anchors.bottom: parent.bottom
                        height: 3
                        radius: 1.5
                        color: Theme.accent
                        visible: tab.active
                    }

                    MouseArea {
                        anchors.fill: parent
                        enabled: tab.tabEnabled
                        cursorShape: Qt.PointingHandCursor
                        onClicked: window.currentTab = tab.index
                    }
                }
            }

            Item { Layout.fillWidth: true }
        }

        Rectangle {
            anchors.left: parent.left
            anchors.right: parent.right
            anchors.bottom: parent.bottom
            height: 1
            color: Theme.border
        }
    }

    StackLayout {
        anchors.fill: parent
        currentIndex: window.currentTab

        ConfigPage {}
        DataPage {}
        RunPage {}
        AboutPage {}
    }
}
