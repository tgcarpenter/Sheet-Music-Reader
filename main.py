from PyQt6.QtWidgets import QApplication, QMainWindow, QStackedLayout, QSpinBox, QVBoxLayout, QWidget, QHBoxLayout, \
    QLabel, QAbstractSpinBox, QPushButton, QSizePolicy, QFileDialog, QStackedWidget, QMessageBox, QLayout
from PyQt6.QtGui import QPdfWriter, QCloseEvent
from PyQt6.QtCore import Qt, QSize, QSettings, QFile, QDataStream, QIODevice
from PyQt6.QtPdfWidgets import QPdfView
from PyQt6.QtPdf import QPdfDocument

import sys
import io

from Menues import *
from DrawWidgets import DrawLabel

MAGIC_NUMBER = 0x23454217
FILE_VERSION = 100


class MyMainWindow(QMainWindow):

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Sheet Music Viewer")
        self.resize(800, 1000)
        self.showMaximized()

        self.last_url = str()
        self.cur_name = str()
        self.recent_docs = []

        self.pdf_view = QPdfView(self)
        self.pdf_view.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.pdf_view.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        self.file_menu = FileMenu(self)
        self.menuBar().addMenu(self.file_menu)
        self.load_recent_url()
        self.file_menu.reset_actions(self.recent_docs)

        self.color_menu = ColorMenu(self)

        self.hideIcon = QIcon("Less.png")
        self.showIcon = QIcon("Greater.png")
        self.hideButton = QPushButton(self.hideIcon, "", self)
        self.hideButton.setFixedWidth(24)
        self.hideButton.clicked.connect(self.toggleHide)

        self.page_down_button = QPushButton()
        self.page_down_button.setFixedHeight(100)
        self.page_down_button.setStyleSheet("QPushButton {background-image: url(L.png) 0 0 0 0 stretch stretch; "
                                            r"background-position:center center; background-repeat: no-repeat;"
                                            r"border: borderless} "
                                            r"QPushButton:hover {border-radius: 5px; "
                                            r"background-color: rgba(88, 205, 240, 70);}")

        self.page_down_button.pressed.connect(lambda: self.page_scroller.setValue(self.page_scroller.value() - 1))

        self.spacer = QWidget()
        self.spacer.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

        self.page_up_button = QPushButton()
        self.page_up_button.setFixedHeight(100)
        self.page_up_button.setStyleSheet("QPushButton {background-image: url(G.png) 0 0 0 0 stretch stretch; "
                                          r"background-position:center center; background-repeat: no-repeat;"
                                          r"border: borderless;} "
                                          r"QPushButton:hover {border-radius: 5px; "
                                          r"background-color: rgba(88, 205, 240, 70);}")

        self.page_up_button.pressed.connect(lambda: self.page_scroller.setValue(self.page_scroller.value() + 1))

        self.page_scroller = QSpinBox()
        self.page_scroller.setMinimum(1)
        self.page_scroller.setMaximum(1)
        self.page_scroller.setStyleSheet(
            "QSpinBox {border: borderless; background-color: white; background-position:center center;}")
        self.page_scroller.setButtonSymbols(QAbstractSpinBox.ButtonSymbols.NoButtons)
        self.page_scroller.valueChanged.connect(self.change_page)

        self.page_total = QLabel("/")

        self.layout_stack = QStackedWidget()

        self.layout2 = QHBoxLayout()
        self.layout2.addWidget(self.page_down_button)
        self.layout2.addWidget(self.spacer)
        self.layout2.addWidget(self.page_up_button)
        base_layout = QStackedLayout()
        base_layout.setStackingMode(QStackedLayout.StackingMode.StackAll)
        base_layout.addWidget(self.pdf_view)
        base_layout.addWidget(self.layout_stack)
        scroll_layout = QHBoxLayout()
        scroll_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        scroll_layout.addWidget(self.page_scroller)
        scroll_layout.addWidget(self.page_total)
        layout = QVBoxLayout()
        layout.addLayout(base_layout)
        layout.addLayout(scroll_layout)
        color_layout = QHBoxLayout()
        color_layout.addWidget(self.color_menu)
        color_layout.addWidget(self.hideButton, alignment=Qt.AlignmentFlag.AlignTop)
        color_layout.addLayout(layout)

        widget = QWidget()
        widget.setLayout(color_layout)

        self.setCentralWidget(widget)

    def resize_pixmap(self, draw_label: DrawLabel, page: int):
        size = self.pdf_view.document().pagePointSize(page).toSize()
        size.setWidth(round(size.width() * (1 / .75)))
        size.setHeight(round(size.height() * (1 / .75)))
        draw_label.pixmap = draw_label.pixmap.scaled(size * self.pdf_view.zoomFactor())

    def toggleHide(self):
        if self.color_menu.isHidden():
            self.color_menu.setHidden(False)
            self.hideButton.setIcon(self.hideIcon)
        else:
            self.color_menu.hide()
            self.hideButton.setIcon(self.showIcon)

    def change_page(self, page):  # Changes pdf page bast of self.page_scroller value
        self.pdf_view.pageNavigator().jump(page - 1, self.pdf_view.pageNavigator().currentLocation())
        self.layout_stack.setCurrentIndex(page - 1)
        self.resize_pixmap(self.layout_stack.currentWidget(), page - 1)
        self.layout_stack.currentWidget().setLayout(self.layout2)

    def open_pdf(self):  # opens file browser to retrieve user selected url
        directory = QFileDialog().getOpenFileName(self, "Open PDF", self.last_url, filter='PDF Files (*.pdf)')

        if not directory[0]:
            return
        self.quick_open_pdf(directory[0])

    def quick_open_pdf(self, url):  # sets psf document, opens it in self.pdf_view, and adds url to list of recent urls
        if self.pdf_view.document():
            ret = self.save_prompt()
            if ret == QMessageBox.StandardButton.Cancel:
                return
            elif ret == QMessageBox.StandardButton.Yes:
                self.save_pdf_overlay(self.pdf_view.document())
        doc = QPdfDocument(self)
        doc.load(url)

        self.pdf_view.setDocument(doc)

        l = url[::-1].find("/")
        self.last_url = url[:(l * -1) - 1]
        self.cur_name = url[(l * -1):-4]

        if url in self.recent_docs:
            self.recent_docs.remove(url)
        elif len(self.recent_docs) > 5:
            self.recent_docs.pop()
        self.recent_docs.insert(0, url)

        a = self.pdf_view.document().pageCount()
        self.page_scroller.setMaximum(a)
        self.page_total.setText("/ " + str(a))

        self.file_menu.reset_actions(self.recent_docs)

        self.load_pdf_overlay(doc)
        self.change_page(1)

    def set_pixmaps(self, doc):  # Adds default label widgets to layout_stack, passes cur_color to be held within
        for _ in range(doc.pageCount()):
            self.layout_stack.addWidget(DrawLabel(self.pdf_view.documentMargins().top(), self.color_menu))

    def save_pdf_overlay(self, doc):  # Saves Pdf pixmap overlays
        if not self.pdf_view.document():
            return
        save = QSettings(fr"saves\{self.cur_name}\{self.cur_name}.ini", QSettings.Format.IniFormat)
        save.beginGroup("overlays")
        save.setValue("overlay", [self.layout_stack.widget(i) for i in range(self.layout_stack.count())])
        save.setValue("author", doc.metaData(QPdfDocument.MetaDataField.Author))
        save.endGroup()
        QApplication.processEvents()  # uses settings to make folder for dat file to be made in

        file = QFile(fr"saves\{self.cur_name}\{self.cur_name}.dat")
        if not file.open(QIODevice.OpenModeFlag.WriteOnly):
            raise IOError
        stream = QDataStream(file)
        stream.writeInt32(MAGIC_NUMBER)
        stream.writeInt32(FILE_VERSION)
        stream.setVersion(QDataStream.Version.Qt_6_4)

        for i in range(self.layout_stack.count()):
            widget = self.layout_stack.widget(i)
            stream << widget.pixmap

    def save_recent_url(self):
        settings = QSettings(r"settings.ini", QSettings.Format.IniFormat)
        settings.beginGroup("recentdocs")
        settings.setValue("urls", self.recent_docs)
        settings.endGroup()

    def load_recent_url(self):
        settings = QSettings(r"settings.ini", QSettings.Format.IniFormat)
        settings.beginGroup("recentdocs")
        urls = settings.value("urls")
        if urls is not None:
            self.recent_docs = urls
        settings.endGroup()

    def load_pdf_overlay(self, doc):  # Loads Pdf pixmap overlays
        save = QSettings(fr"saves\{self.cur_name}\{self.cur_name}.ini", QSettings.Format.IniFormat)
        save.beginGroup("overlays")
        temp = save.value("author")
        save.endGroup()
        if temp != doc.metaData(QPdfDocument.MetaDataField.Author) and temp is not None:
            ret = QMessageBox.warning(self, "Error", "The file you are trying to open has been updated or modified. "
                                                     "Loading could cause unexpected errors, are you sure you would "
                                                     "like to continue?", QMessageBox.StandardButton.Yes |
                                      QMessageBox.StandardButton.No, QMessageBox.StandardButton.No)
            if ret == QMessageBox.StandardButton.No:
                save.endGroup()
                return
        self.clearLayout(self.layout_stack)
        self.set_pixmaps(doc)

        file = QFile(fr"saves\{self.cur_name}\{self.cur_name}.dat")
        if not file.open(QFile.OpenModeFlag.ReadOnly):
            self.save_pdf_overlay(doc)
            file = QFile(fr"saves\{self.cur_name}\{self.cur_name}.dat")
            file.open(QFile.OpenModeFlag.ReadOnly)
        stream = QDataStream(file)
        magic = stream.readInt32()
        if magic != MAGIC_NUMBER:
            raise IOError("invalid magic number")
        version = stream.readInt32()
        if version != FILE_VERSION:
            raise IOError("invalid version number")
        stream.setVersion(QDataStream.Version.Qt_6_4)
        for i in range(self.layout_stack.count()):
            widget = self.layout_stack.widget(i)
            pixmap = widget.pixmap
            stream >> pixmap

    def save_prompt(self):
        return QMessageBox.question(self, "Save?", "Would you like to save your changes before closing?",
                                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No |
                                    QMessageBox.StandardButton.Cancel, QMessageBox.StandardButton.Yes)

    def closeEvent(self, a0: QCloseEvent) -> None:
        if self.pdf_view.document():
            ret = self.save_prompt()
            if ret == QMessageBox.StandardButton.Cancel:
                a0.ignore()
                return
            elif ret == QMessageBox.StandardButton.Yes:
                self.save_pdf_overlay(self.pdf_view.document())
        self.save_recent_url()
        a0.accept()

    @staticmethod
    def clearLayout(layout):
        if layout is not None:
            while layout.count():
                child = layout.widget(0)
                if child is not None:
                    layout.removeWidget(child)
                    child.deleteLater()


app = QApplication(sys.argv)

window = MyMainWindow()
window.show()

app.exec()
