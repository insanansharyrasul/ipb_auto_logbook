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

            Card {
                title: "Account"
                Layout.fillWidth: true

                RowLayout {
                    Layout.fillWidth: true
                    spacing: Theme.spaceLg
                    FieldLabel { text: "Username" }
                    AppTextField {
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
                        info: "Nama Dosen Penggerak dari Student Portal.\n"
                              + "Kemahasiswaan → Aktivitas → Log (ikon list) → Tambah.\n"
                              + "Contoh: 'Jeffrey Einstein, S.Komp., Ph.D.'."
                    }
                    AppTextField {
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
                        info: "Angka di kolom 'No' pada halaman Kemahasiswaan → Aktivitas."
                    }
                    AppTextField {
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
                        info: "Tahun & semester sesuai kolom 'Tahun Semester'.\n"
                              + "Contoh: '2026/2027 Semester Genap'."
                    }
                    AppTextField {
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
                        Layout.fillWidth: true
                        text: Controller.csvPath
                        onTextEdited: Controller.csvPath = text
                    }
                    AppButton {
                        text: "Browse"
                        onClicked: Controller.chooseCsvFile()
                    }
                }
            }

            Card {
                title: "Options"
                Layout.fillWidth: true

                AppCheckBox {
                    text: "Headless (no browser window)"
                    checked: Controller.headless
                    onToggled: Controller.headless = checked
                }

                RowLayout {
                    Layout.fillWidth: true
                    spacing: Theme.spaceLg
                    FieldLabel { text: "Slow Mo (ms)" }
                    AppSpinBox {
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
                    onClicked: Controller.chooseSaveConfig()
                }
                AppButton {
                    text: "Load Config"
                    onClicked: Controller.chooseLoadConfig()
                }
                Item { Layout.fillWidth: true }
            }

            Item { Layout.fillHeight: true }
        }
    }
}
