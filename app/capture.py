from PyQt6 import QtCore, QtGui


class CaptureManager:
    def grab_rect(self, rect: QtCore.QRect) -> QtGui.QPixmap:
        # Compose from all screens so multi-monitor and negative coords work.
        result = QtGui.QPixmap(rect.size())
        result.fill(QtCore.Qt.GlobalColor.black)
        painter = QtGui.QPainter(result)
        for screen in QtGui.QGuiApplication.screens():
            s_geo = screen.geometry()
            intersect = rect.intersected(s_geo)
            if intersect.isEmpty():
                continue
            # Convert global coords to screen-local
            local_x = intersect.x() - s_geo.x()
            local_y = intersect.y() - s_geo.y()
            part = screen.grabWindow(0, local_x, local_y, intersect.width(), intersect.height())
            if not part.isNull():
                dest_x = intersect.x() - rect.x()
                dest_y = intersect.y() - rect.y()
                painter.drawPixmap(dest_x, dest_y, part)
        painter.end()
        return result
