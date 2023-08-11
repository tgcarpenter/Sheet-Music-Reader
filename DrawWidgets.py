from PyQt6.QtWidgets import QLabel, QWidget, QSizePolicy, QApplication, QColorDialog, QHBoxLayout, QVBoxLayout
from PyQt6.QtCore import QPointF, Qt, QSize
from PyQt6.QtGui import QPainter, QMouseEvent, QPaintEvent, QPixmap, QCursor, QResizeEvent, QPainterPath, QPen, QBrush


class DrawLabel(QWidget):
    def __init__(self, margin, colorMenu):
        super().__init__()
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.top_margin = margin
        self.colorMenu = colorMenu
        self.cur_pos = None
        self.pixmap = QPixmap(100, 100)
        self.pixmap.fill(Qt.GlobalColor.transparent)
        self.pixmap = self.pixmap.scaled(self.size())

    def offsetPoint(self, point: QPointF) -> QPointF:  # // Helper function // offsets point to correct position
        center = self.rect().center()

        point.setY(point.y() - self.top_margin)
        point.setX(point.x() - (center.x() - (self.pixmap.width() // 2)))

        return point

    def draw_at_point(self, point: QPointF):  # TODO create brush class and do this operation different depending on the brush
        painter = QPainter()
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        painter.begin(self.pixmap)

        point = self.offsetPoint(point)

        self.cur_pos = point

        path = QPainterPath()
        path.addEllipse(point, self.colorMenu.brushSize, self.colorMenu.brushSize)

        if self.colorMenu.brush:
            painter.fillPath(path, self.colorMenu.cur_color)
        else:
            painter.setCompositionMode(QPainter.CompositionMode.CompositionMode_Source)
            painter.fillPath(path, Qt.GlobalColor.transparent)

        self.repaint()

    def drawLine(self, point: list):
        center = self.rect().center()

        painter = QPainter()
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        painter.begin(self.pixmap)

        points = []
        for p in point:
            x = p.position()
            x.setY(x.y() - self.top_margin)
            x.setX(x.x() - (center.x() - (self.pixmap.width() // 2)))
            points.append(x)

        path = QPainterPath()
        path.moveTo(self.cur_pos)
        for p in points:
            path.lineTo(p)
        self.cur_pos = points[-1]

        pen = QPen()
        pen.setWidth(self.colorMenu.brushSize * 2)
        pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        if self.colorMenu.brush:
            pen.setBrush(self.colorMenu.cur_color)
            painter.strokePath(path, pen)
        else:
            painter.setCompositionMode(QPainter.CompositionMode.CompositionMode_Source)
            pen.setColor(Qt.GlobalColor.transparent)
            painter.strokePath(path, pen)

        self.repaint()

    def mousePressEvent(self, a0: QMouseEvent) -> None:
        self.draw_at_point(a0.position())

    def mouseMoveEvent(self, a0: QMouseEvent) -> None:
        self.drawLine(a0.points())
        #self.draw_at_point(a0.position())
        super().mouseMoveEvent(a0)

    def mouseReleaseEvent(self, a0: QMouseEvent) -> None:
        self.cur_pos = None

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
