from PyQt6 import QtCore, QtGui, QtWidgets
from .config import AppConfig


class SnipOverlay(QtWidgets.QWidget):
    selectionMade = QtCore.pyqtSignal(QtCore.QRect)
    canceled = QtCore.pyqtSignal()

    def __init__(self, config: AppConfig):
        super().__init__()
        self._config = config
        self.setWindowFlags(
            QtCore.Qt.WindowType.FramelessWindowHint
            | QtCore.Qt.WindowType.WindowStaysOnTopHint
            | QtCore.Qt.WindowType.Tool
        )
        self.setAttribute(QtCore.Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setCursor(QtCore.Qt.CursorShape.CrossCursor)
        self._origin = None
        self._current = None
        self._last_pos = None
        self._cancel_btn = QtWidgets.QPushButton("Cancel", self)
        self._cancel_btn.setObjectName("CancelButton")
        self._cancel_btn.clicked.connect(self._cancel)
        self._cancel_btn.hide()

    def start(self):
        # Cover the entire virtual desktop (all monitors)
        virtual_geo = QtGui.QGuiApplication.primaryScreen().virtualGeometry()
        self.setGeometry(virtual_geo)
        self._origin = None
        self._current = None
        self._last_pos = None
        self._cancel_btn.show()
        self.show()
        self.raise_()
        self.activateWindow()

    def paintEvent(self, event):
        painter = QtGui.QPainter(self)
        painter.setRenderHint(QtGui.QPainter.RenderHint.Antialiasing)
        # Darken the background
        painter.fillRect(self.rect(), QtGui.QColor(0, 0, 0, 120))

        if self._last_pos:
            # Crosshair
            pen = QtGui.QPen(QtGui.QColor(0, 200, 255, 180), 1, QtCore.Qt.PenStyle.DashLine)
            painter.setPen(pen)
            painter.drawLine(0, self._last_pos.y(), self.width(), self._last_pos.y())
            painter.drawLine(self._last_pos.x(), 0, self._last_pos.x(), self.height())

        if self._origin and self._current:
            rect = QtCore.QRect(self._origin, self._current).normalized()
            # Clear the selection area
            painter.setCompositionMode(QtGui.QPainter.CompositionMode.CompositionMode_Clear)
            painter.fillRect(rect, QtCore.Qt.GlobalColor.transparent)
            painter.setCompositionMode(QtGui.QPainter.CompositionMode.CompositionMode_SourceOver)
            # Draw selection border
            pen = QtGui.QPen(QtGui.QColor(0, 200, 255), 2)
            painter.setPen(pen)
            painter.drawRect(rect)

            # Size label
            label = f"{rect.width()} x {rect.height()}"
            metrics = painter.fontMetrics()
            label_rect = metrics.boundingRect(label).adjusted(-6, -3, 6, 3)
            label_rect.moveTopLeft(rect.topLeft() + QtCore.QPoint(6, -label_rect.height() - 6))
            if label_rect.top() < 0:
                label_rect.moveTop(rect.topLeft().y() + 6)
            painter.fillRect(label_rect, QtGui.QColor(0, 0, 0, 160))
            painter.setPen(QtGui.QColor(230, 230, 230))
            painter.drawText(label_rect, QtCore.Qt.AlignmentFlag.AlignCenter, label)

    def mousePressEvent(self, event):
        if event.button() == QtCore.Qt.MouseButton.LeftButton:
            self._origin = event.position().toPoint()
            self._current = self._origin
            self.update()

    def mouseMoveEvent(self, event):
        self._last_pos = event.position().toPoint()
        if self._origin:
            self._current = event.position().toPoint()
            self.update()
        else:
            self.update()

    def mouseReleaseEvent(self, event):
        if event.button() == QtCore.Qt.MouseButton.LeftButton and self._origin:
            self._current = event.position().toPoint()
            rect = QtCore.QRect(self._origin, self._current).normalized()
            self.hide()
            self._cancel_btn.hide()
            if rect.width() > self._config.min_selection_px and rect.height() > self._config.min_selection_px:
                # Convert to global coordinates
                global_rect = QtCore.QRect(
                    self.mapToGlobal(rect.topLeft()),
                    rect.size(),
                )
                self.selectionMade.emit(global_rect)
            self._origin = None
            self._current = None
            self._last_pos = None

    def keyPressEvent(self, event):
        event.ignore()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        margin = 16
        size = self._cancel_btn.sizeHint()
        self._cancel_btn.move(self.width() - size.width() - margin, margin)

    def _cancel(self):
        self.hide()
        self._cancel_btn.hide()
        self.canceled.emit()
