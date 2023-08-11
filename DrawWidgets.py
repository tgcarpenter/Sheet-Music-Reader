from PyQt6.QtWidgets import QLabel, QWidget, QSizePolicy, QApplication, QColorDialog, QHBoxLayout, QVBoxLayout
from PyQt6.QtCore import QPointF, Qt, QSize
from PyQt6.QtGui import QPainter, QMouseEvent, QPaintEvent, QPixmap, QCursor, QResizeEvent, QPainterPath


class DrawLabel(QWidget):
    def __init__(self, margin, colorMenu):
        super().__init__()
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.top_margin = margin
        self.colorMenu = colorMenu
        self.pixmap = QPixmap(100, 100)
        self.pixmap.fill(Qt.GlobalColor.transparent)
        self.pixmap = self.pixmap.scaled(self.size())

    def draw_at_point(self, point: QPointF):
        center = self.rect().center()
        point.setY(point.y() - self.top_margin)
        point.setX(point.x() - (center.x() - (self.pixmap.width() // 2)))

        path = QPainterPath()
        path.addEllipse(point, self.colorMenu.brushSize, self.colorMenu.brushSize)

        painter = QPainter()
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        painter.begin(self.pixmap)
        if self.colorMenu.brush:
            painter.fillPath(path, self.colorMenu.cur_color)
        else:
            painter.setCompositionMode(QPainter.CompositionMode.CompositionMode_Source)
            painter.fillPath(path, Qt.GlobalColor.transparent)

        self.repaint()

    def mousePressEvent(self, a0: QMouseEvent) -> None:
        self.draw_at_point(a0.position())

    def mouseMoveEvent(self, a0: QMouseEvent) -> None:
        self.draw_at_point(a0.position())
        super().mouseMoveEvent(a0)

    def paintEvent(self, a0: QPaintEvent) -> None:  # location might have to be overhauled
        center = self.rect().center()
        center.setY(self.top_margin)
        center.setX(center.x() - (self.pixmap.width() // 2))
        painter = QPainter(self)
        painter.begin(self)
        painter.drawPixmap(center, self.pixmap)
        painter.end()


class MyColorDialog(QColorDialog):

    def __init__(self, parent=None):
        super().__init__(parent=parent)

        self.c_label = QLabel("Custom Colors:")
        self.custom_layout = QVBoxLayout()
        self.custom_layout.addWidget(self.c_label)
        self.layout().addLayout(self.custom_layout)
        self.setCurrentColor(self.customColor(0))

        for child in self.findChildren(QWidget):
            classname = child.metaObject().className()
            if classname not in ("QColorPicker", "QColorLuminancePicker", "QColorShower", "QDialogButtonBox",
                                 "QWellArray", "QPushButton"):
                child.hide()

            if classname == "QWellArray":
                if child.sizeHint() == QSize(224, 144):
                    child.hide()
                else:
                    self.custom_layout.addWidget(child)

            if classname == "QPushButton":
                if child.text() != "&Add to Custom Colors":
                    child.hide()
                else:
                    child.setText("Save Color")
                    child.setFixedWidth(125)
                    self.custom_layout.addWidget(child)
