import QtQuick
import QtQuick.Controls
import QtQuick.Dialogs
import QtQuick.Layouts
import App 1.0
import "../Theme.js" as Theme
import "../components"

Item {
    id: page

    property int pendingFileRow: -1

    ColumnLayout {
        anchors.fill: parent
        anchors.margins: Theme.pageMargin
        spacing: Theme.spaceLg

        RowLayout {
            Layout.fillWidth: true
            spacing: Theme.spaceSm

            AppButton {
                text: "Load CSV from Config"
                onClicked: {
                    if (Controller.csvPath === "")
                        loadCsvDialog.open()
                    else
                        Controller.loadCsv()
                }
            }
            AppButton {
                text: "Add Row"
                onClicked: Controller.rows.addRow()
            }
            AppButton {
                text: "Delete Last"
                onClicked: Controller.rows.removeLastRow()
            }
            AppButton {
                text: "Save CSV"
                variant: "primary"
                onClicked: saveCsvDialog.open()
            }
            Item { Layout.fillWidth: true }
        }

        Card {
            title: "Logbook Rows"
            expanded: true
            Layout.fillWidth: true
            Layout.fillHeight: true

            ScrollView {
                id: tableScroll
                Layout.fillWidth: true
                Layout.fillHeight: true
                clip: true
                contentWidth: Math.max(availableWidth, Theme.tableMinWidth)
                ScrollBar.horizontal.policy: ScrollBar.AsNeeded

                ColumnLayout {
                    width: Math.max(tableScroll.availableWidth, Theme.tableMinWidth)
                    spacing: 0

                    RowLayout {
                        Layout.fillWidth: true
                        Layout.leftMargin: Theme.spaceXs
                        Layout.rightMargin: Theme.spaceXs
                        Layout.topMargin: Theme.spaceXs
                        Layout.bottomMargin: Theme.spaceSm
                        spacing: Theme.columnGap

                        Repeater {
                            model: ["Tanggal", "Mulai", "Selesai", "Keterangan", "File", "Tipe", "Lokasi", "Berita"]

                            Text {
                                required property int index
                                required property string modelData
                                Layout.preferredWidth: Theme.columnWidths[index]
                                text: modelData
                                color: Theme.muted
                                font.pixelSize: Theme.fontSizeSmall
                                font.weight: Font.DemiBold
                                elide: Text.ElideRight
                            }
                        }

                        Item { Layout.fillWidth: true }
                    }

                    Rectangle {
                        Layout.fillWidth: true
                        implicitHeight: 1
                        color: Theme.border
                    }

                    Repeater {
                        model: Controller.rows

                        Rectangle {
                            id: rowRoot
                            required property int index
                            required property string tanggal
                            required property string mulai
                            required property string selesai
                            required property string keterangan
                            required property string file
                            required property string tipe
                            required property string lokasi
                            required property string berita

                            Layout.fillWidth: true
                            implicitHeight: 46
                            color: rowHover.hovered ? Theme.surfaceHover : "transparent"

                            HoverHandler { id: rowHover }

                            RowLayout {
                                anchors.fill: parent
                                anchors.leftMargin: Theme.spaceXs
                                anchors.rightMargin: Theme.spaceXs
                                spacing: Theme.columnGap

                                AppTextField {
                                    compact: true
                                    Layout.preferredWidth: Theme.columnWidths[0]
                                    text: rowRoot.tanggal
                                    onTextEdited: Controller.rows.setField(rowRoot.index, "tanggal", text)
                                }

                                AppTextField {
                                    compact: true
                                    Layout.preferredWidth: Theme.columnWidths[1]
                                    text: rowRoot.mulai
                                    onTextEdited: Controller.rows.setField(rowRoot.index, "mulai", text)
                                }

                                AppTextField {
                                    compact: true
                                    Layout.preferredWidth: Theme.columnWidths[2]
                                    text: rowRoot.selesai
                                    onTextEdited: Controller.rows.setField(rowRoot.index, "selesai", text)
                                }

                                AppTextField {
                                    compact: true
                                    Layout.preferredWidth: Theme.columnWidths[3]
                                    text: rowRoot.keterangan
                                    onTextEdited: Controller.rows.setField(rowRoot.index, "keterangan", text)
                                }

                                RowLayout {
                                    Layout.preferredWidth: Theme.columnWidths[4]
                                    spacing: Theme.spaceXs

                                    AppTextField {
                                        compact: true
                                        Layout.fillWidth: true
                                        text: rowRoot.file
                                        onTextEdited: Controller.rows.setField(rowRoot.index, "file", text)
                                    }
                                    AppButton {
                                        compact: true
                                        text: "…"
                                        Layout.preferredWidth: 32
                                        onClicked: {
                                            page.pendingFileRow = rowRoot.index
                                            fileDialog.open()
                                        }
                                    }
                                }

                                AppComboBox {
                                    compact: true
                                    Layout.preferredWidth: Theme.columnWidths[5]
                                    model: Controller.tipeValues
                                    currentIndex: Math.max(0, Controller.tipeValues.indexOf(rowRoot.tipe))
                                    onActivated: Controller.rows.setField(rowRoot.index, "tipe", currentText)
                                }

                                AppTextField {
                                    compact: true
                                    Layout.preferredWidth: Theme.columnWidths[6]
                                    text: rowRoot.lokasi
                                    onTextEdited: Controller.rows.setField(rowRoot.index, "lokasi", text)
                                }

                                AppComboBox {
                                    compact: true
                                    Layout.preferredWidth: Theme.columnWidths[7]
                                    model: Controller.beritaValues
                                    currentIndex: Math.max(0, Controller.beritaValues.indexOf(rowRoot.berita))
                                    onActivated: Controller.rows.setField(rowRoot.index, "berita", currentText)
                                }

                                Item { Layout.fillWidth: true }
                            }
                        }
                    }
                }
            }
        }
    }

    FileDialog {
        id: loadCsvDialog
        title: "Select CSV file"
        nameFilters: ["CSV files (*.csv)", "All files (*)"]
        onAccepted: Controller.loadCsvFromUrl(selectedFile)
    }

    FileDialog {
        id: saveCsvDialog
        title: "Save CSV"
        fileMode: FileDialog.SaveFile
        defaultSuffix: "csv"
        nameFilters: ["CSV files (*.csv)", "All files (*)"]
        onAccepted: Controller.saveCsvTo(selectedFile)
    }

    FileDialog {
        id: fileDialog
        title: "Select file"
        onAccepted: {
            if (page.pendingFileRow >= 0)
                Controller.setRowFile(page.pendingFileRow, selectedFile)
            page.pendingFileRow = -1
        }
    }
}
