import QtQuick
import QtQuick.Controls
import QtQuick.Dialogs
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

            Card {
                title: "Account"
                Layout.fillWidth: true

                RowLayout {
                    Layout.fillWidth: true
                    spacing: Theme.spaceLg
                    FieldLabel { text: "Username" }
                    AppTextField {
                        id: usernameField
                        Layout.fillWidth: true
                        text: Controller.username
                        onTextEdited: Controller.username = text
                    }
                }

                RowLayout {
                    Layout.fillWidth: true
                    spacing: Theme.spaceLg
                    FieldLabel { text: "Password" }
                    AppTextField {
                        id: passwordField
                        Layout.fillWidth: true
                        echoMode: TextInput.Password
                        text: Controller.password
                        onTextEdited: Controller.password = text
                    }
                }
            }

            Card {
                title: "Logbook"
                Layout.fillWidth: true

                RowLayout {
                    Layout.fillWidth: true
                    spacing: Theme.spaceLg
                    FieldLabel {
                        text: "Dosen"
                        info: Controller.dosenInfo
                    }
                    AppTextField {
                        id: dosenField
                        Layout.fillWidth: true
                        text: Controller.dosen
                        onTextEdited: Controller.dosen = text
                    }
                }

                RowLayout {
                    Layout.fillWidth: true
                    spacing: Theme.spaceLg
                    FieldLabel {
                        text: "Row Number"
                        info: Controller.rowNumberInfo
                    }
                    AppTextField {
                        id: rowField
                        Layout.fillWidth: true
                        text: Controller.rowNumber
                        onTextEdited: Controller.rowNumber = text
                    }
                }

                RowLayout {
                    Layout.fillWidth: true
                    spacing: Theme.spaceLg
                    FieldLabel {
                        text: "Semester"
                        info: Controller.semesterInfo
                    }
                    AppTextField {
                        id: semesterField
                        Layout.fillWidth: true
                        text: Controller.semester
                        onTextEdited: Controller.semester = text
                    }
                }
            }

            Card {
                title: "Data Source"
                Layout.fillWidth: true

                RowLayout {
                    Layout.fillWidth: true
                    spacing: Theme.spaceLg
                    FieldLabel { text: "CSV File" }
                    AppTextField {
                        id: csvField
                        Layout.fillWidth: true
                        text: Controller.csvPath
                        onTextEdited: Controller.csvPath = text
                    }
                    AppButton {
                        text: "Browse"
                        onClicked: csvDialog.open()
                    }
                }
            }

            Card {
                title: "Options"
                Layout.fillWidth: true

                AppCheckBox {
                    id: headlessBox
                    text: "Headless (no browser window)"
                    checked: Controller.headless
                    onToggled: Controller.headless = checked
                }

                RowLayout {
                    Layout.fillWidth: true
                    spacing: Theme.spaceLg
                    FieldLabel { text: "Slow Mo (ms)" }
                    AppSpinBox {
                        id: slowMoSpin
                        Layout.fillWidth: true
                        from: 50
                        to: 500
                        stepSize: 50
                        value: Controller.slowMo
                        onValueModified: Controller.slowMo = value
                    }
                }
            }

            Item { Layout.preferredHeight: Theme.spaceXs }

            RowLayout {
                Layout.fillWidth: true
                spacing: Theme.spaceSm

                AppButton {
                    text: "Save Config"
                    variant: "primary"
                    onClicked: saveConfigDialog.open()
                }
                AppButton {
                    text: "Load Config"
                    onClicked: loadConfigDialog.open()
                }
                Item { Layout.fillWidth: true }
            }

            Item { Layout.fillHeight: true }
        }
    }

    Connections {
        target: Controller

        function onConfigLoaded() {
            usernameField.text = Controller.username
            passwordField.text = Controller.password
            dosenField.text = Controller.dosen
            rowField.text = Controller.rowNumber
            semesterField.text = Controller.semester
            csvField.text = Controller.csvPath
            headlessBox.checked = Controller.headless
            slowMoSpin.value = Controller.slowMo
        }

        function onCsvPathChanged() {
            if (!csvField.activeFocus)
                csvField.text = Controller.csvPath
        }
    }

    FileDialog {
        id: csvDialog
        title: "Select CSV file"
        nameFilters: ["CSV files (*.csv)", "All files (*)"]
        onAccepted: Controller.setCsvPathFromUrl(selectedFile)
    }

    FileDialog {
        id: saveConfigDialog
        title: "Save config"
        fileMode: FileDialog.SaveFile
        defaultSuffix: "json"
        nameFilters: ["JSON files (*.json)", "All files (*)"]
        onAccepted: Controller.saveConfigTo(selectedFile)
    }

    FileDialog {
        id: loadConfigDialog
        title: "Load config"
        nameFilters: ["JSON files (*.json)", "All files (*)"]
        onAccepted: Controller.loadConfigFrom(selectedFile)
    }
}
