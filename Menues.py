from PyQt6.QtWidgets import QMenu, QWidget, QColorDialog, QVBoxLayout, QHBoxLayout, QLayout, QLabel, QSlider, QSpinBox, \
    QAbstractSpinBox, QToolBar
from PyQt6.QtGui import QAction, QColor, QIcon, QActionGroup
from PyQt6.QtCore import Qt, QSize

from DrawWidgets import MyColorDialog


class FileMenu(QMenu):

    def __init__(self, main_window):
        super().__init__(main_window)
        self.setTitle("File")

        self.main_window = main_window

        open_action = QAction("Open", self)
        open_action.triggered.connect(main_window.open_pdf)
        open_action.setShortcut("Ctrl+O")
        self.addAction(open_action)

        self.open_recent_menu = QMenu("Open Recent")
        self.open_recent_menu.triggered.connect(self.open)
        self.addMenu(self.open_recent_menu)

        save_action = QAction("Save", self)
        save_action.triggered.connect(lambda: main_window.save_pdf_overlay(main_window.pdf_view.document()))
        self.addAction(save_action)

    def open(self, action):  # functions as an in-between function for recent menu triggered signal
        self.main_window.quick_open_pdf(action.text())

    def reset_actions(self, urls):  # resets urls based on the given list
        self.open_recent_menu.clear()
        for url in urls:
            self.open_recent_menu.addAction(url)


class ColorMenu(QWidget):
    def __init__(self, parent=None):
        super(ColorMenu, self).__init__(parent=parent)
        self.setFixedWidth(300)
        self.brushSize = 5
        self.brush = 1

        dialog = MyColorDialog(parent)
        dialog.setOption(QColorDialog.ColorDialogOption.DontUseNativeDialog, True)
        self.cur_color = dialog.currentColor()
        dialog.currentColorChanged.connect(self.set_color)

        sizeSlider = QSlider(Qt.Orientation.Horizontal, self)
        sizeSlider.setMinimum(1)
        sizeSlider.setValue(5)

        sizeDisplay = QSpinBox(self)
        sizeDisplay.setMinimum(1)
        sizeDisplay.setMaximum(99)
        sizeDisplay.setValue(5)
        sizeDisplay.setButtonSymbols(QAbstractSpinBox.ButtonSymbols.NoButtons)
        sizeDisplay.setMaximumWidth(40)

        sizeSlider.valueChanged.connect(sizeDisplay.setValue)  # triggers signal twice
        sizeDisplay.valueChanged.connect(sizeSlider.setValue)

        sizeSlider.valueChanged.connect(self.setBrushSize)

        brushBar = QToolBar(self)
        brushBar.setIconSize(QSize(40, 40))

        brushGroup = QActionGroup(self)

        eraserIcon = QIcon("Eraser.png")
        eraserAction = QAction(eraserIcon, "Eraser", self)
        eraserAction.setCheckable(True)
        eraserAction.triggered.connect(lambda: self.setBrush(0))

        penIcon = QIcon("Pen.png")
        penAction = QAction(penIcon, "Pen", self)
        penAction.setCheckable(True)
        penAction.setChecked(True)
        penAction.triggered.connect(lambda: self.setBrush(1))

        brushBar.addAction(eraserAction)
        brushBar.addAction(penAction)
        brushGroup.addAction(eraserAction)
        brushGroup.addAction(penAction)

        brushSize = QLabel("Size:", self)
        f = brushSize.font()
        f.setUnderline(True)
        brushSize.setFont(f)
        brushes_label = QLabel("Brushes:", self)
        brushes_label.setFont(f)

        layout = QVBoxLayout()
        sizeLayout = QHBoxLayout()
        sizeLayout.addWidget(brushSize)
        sizeLayout.addWidget(sizeDisplay)
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        layout.addWidget(dialog, alignment=Qt.AlignmentFlag.AlignTop)
        layout.addLayout(sizeLayout)
        layout.addWidget(sizeSlider, alignment=Qt.AlignmentFlag.AlignTop)
        layout.addWidget(brushes_label)
        layout.addWidget(brushBar)

        self.setLayout(layout)

    def set_color(self, color: QColor):
        r, g, b, a = color.getRgb()
        self.cur_color.setRgb(r, g, b, a)

    def setBrushSize(self, size: int):
        self.brushSize = size

    def setBrush(self, brush: int):  # TODO make brush class and accompanied objects
        self.brush = brush



