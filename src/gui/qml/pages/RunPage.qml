import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import App 1.0
import "../Theme.js" as Theme
import "../components"

Item {
    id: page

    readonly property color statusColor: {
        switch (Controller.statusKind) {
        case "running": return "#F9A825"
        case "success": return Theme.success
        case "error": return Theme.danger
        default: return Theme.muted
        }
    }

    ColumnLayout {
        anchors.fill: parent
        anchors.margins: Theme.pageMargin
        spacing: Theme.spaceLg

        Card {
            title: "Automation"
            Layout.fillWidth: true

            RowLayout {
                Layout.fillWidth: true
                spacing: Theme.spaceLg

                AppButton {
                    text: Controller.running ? "■  Stop" : "▶  Start"
                    variant: Controller.running ? "danger" : "success"
                    enabled: !Controller.stopping
                    onClicked: {
                        if (Controller.running)
                            Controller.stop()
                        else
                            Controller.start()
                    }
                }

                Text {
                    text: Controller.statusText
                    color: page.statusColor
                    font.pixelSize: Theme.fontSize
                    font.weight: Font.DemiBold
                }

                Item { Layout.fillWidth: true }
            }

            ProgressBar {
                id: progress
                Layout.fillWidth: true
                from: 0
                to: Controller.progressTotal > 0 ? Controller.progressTotal : 1
                value: Controller.progressCurrent

                background: Rectangle {
                    implicitHeight: 6
                    radius: 3
                    color: Theme.track
                }

                contentItem: Item {
                    implicitHeight: 6

                    Rectangle {
                        width: parent.width * progress.visualPosition
                        height: parent.height
                        radius: 3
                        color: Theme.accent
                    }
                }
            }
        }

        Card {
            title: "Log"
            expanded: true
            Layout.fillWidth: true
            Layout.fillHeight: true

            ScrollView {
                id: logScroll
                Layout.fillWidth: true
                Layout.fillHeight: true
                clip: true

                TextArea {
                    id: logArea
                    readOnly: true
                    text: Controller.logText
                    color: Theme.textSoft
                    font.family: "monospace"
                    font.pixelSize: 12
                    wrapMode: TextEdit.Wrap
                    padding: Theme.spaceMd

                    background: Rectangle {
                        color: Theme.navBackground
                        radius: Theme.radiusSm
                        border.width: 1
                        border.color: Theme.border
                    }

                    onTextChanged: {
                        if (Controller.running) {
                            Qt.callLater(function() {
                                logScroll.contentItem.contentY =
                                    Math.max(0, logScroll.contentItem.contentHeight - logScroll.availableHeight)
                            })
                        }
                    }
                }
            }
        }
    }
}
