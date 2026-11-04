import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import App 1.0
import "../Theme.js" as Theme
import "../components"

Item {
    id: page

    ScrollView {
        id: scroll
        anchors.fill: parent
        contentWidth: availableWidth
        leftPadding: Theme.pageMargin
        rightPadding: Theme.pageMargin
        topPadding: Theme.pageMargin
        bottomPadding: Theme.pageMargin
        ScrollBar.horizontal.policy: ScrollBar.AlwaysOff
        clip: true

        ColumnLayout {
            width: scroll.availableWidth
            spacing: Theme.spaceLg

            Text {
                Layout.fillWidth: true
                text: "IPB Auto Logbook"
                color: Theme.text
                font.pixelSize: Theme.fontSizeHero
                font.weight: Font.Bold
            }

            Text {
                Layout.fillWidth: true
                text: "Automated logbook filler for IPB University Student Portal · v" + Controller.appVersion
                color: Theme.muted
                font.pixelSize: Theme.fontSize
            }

            Card {
                title: "Contributors"
                Layout.fillWidth: true

                Repeater {
                    model: Controller.maintainers

                    Text {
                        required property string modelData
                        Layout.fillWidth: true
                        text: modelData
                        color: Theme.textSoft
                        font.pixelSize: Theme.fontSize
                    }
                }
            }

            Card {
                title: "Donators"
                Layout.fillWidth: true

                Repeater {
                    model: Controller.donators

                    Text {
                        required property string modelData
                        Layout.fillWidth: true
                        text: modelData
                        color: Theme.textSoft
                        font.pixelSize: Theme.fontSize
                    }
                }
            }

            Card {
                title: "Project"
                Layout.fillWidth: true

                Text {
                    Layout.fillWidth: true
                    text: "Original repository: github.com/insanansharyrasul/ipb_auto_logbook"
                    color: Theme.textSoft
                    font.pixelSize: Theme.fontSize
                }

                Text {
                    Layout.fillWidth: true
                    text: "License: GNU General Public License v3.0"
                    color: Theme.textSoft
                    font.pixelSize: Theme.fontSize
                }
            }

            Item { Layout.fillHeight: true }
        }
    }
}
