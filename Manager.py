from PyQt5.QtWidgets import QWidget, QApplication
from PyQt5.QtCore import QObject, QEvent, QRect, QMargins, Qt
from PyQt5.QtGui import QPainter, QColor
from enum import Enum


class AcceptPanel(QWidget):

    def __init__(self, parent):
        super(AcceptPanel, self).__init__(parent)
        self.left_rect = QRect()
        self.right_rect = QRect()
        self.top_rect = QRect()
        self.bottom_rect = QRect()
        self.center_rect = QRect()
        self.hover_rect = QRect()
        self.setMouseTracking(True)
        self.setAcceptDrops(True)

    def resizeEvent(self, a0):
        total_rect = self.rect()
        total_rect = total_rect - QMargins(5, 5, 5, 5)
        anchor_width = 30

        self.left_rect = QRect(int(total_rect.left()), int(total_rect.center().y() - anchor_width / 2), int(anchor_width), int(anchor_width))
        self.right_rect = QRect(int(total_rect.right() - anchor_width), int(total_rect.center().y() - anchor_width / 2), int(anchor_width), int(anchor_width))
        self.top_rect = QRect(int(total_rect.center().x() - anchor_width / 2), int(total_rect.top()), int(anchor_width), int(anchor_width))
        self.bottom_rect = QRect(int(total_rect.center().x() - anchor_width / 2), int(total_rect.bottom() - anchor_width), int(anchor_width), int(anchor_width))
        self.center_rect = QRect(int(total_rect.center().x() - anchor_width / 2), int(total_rect.center().y() - anchor_width / 2), int(anchor_width), int(anchor_width))

    def async_with(self, target_view: QWidget):
        self.resize(target_view.size())

    def paintEvent(self, a0):
        super(AcceptPanel, self).paintEvent(a0)
        painter = QPainter(self)
        painter.fillRect(self.rect(), Qt.lightGray)

        painter.fillRect(self.hover_rect, Qt.gray)

        painter.fillRect(self.top_rect, Qt.green)
        painter.fillRect(self.bottom_rect, Qt.green)
        painter.fillRect(self.left_rect, Qt.green)
        painter.fillRect(self.right_rect, Qt.green)
        painter.fillRect(self.center_rect, Qt.green)

    def mouseMoveEvent(self, a0):
        self.hover_rect = self.rect()
        print(a0.pos())

        if self.left_rect.contains(a0.pos()):
            self.hover_rect.setWidth(int(self.hover_rect.width() / 3))
        elif self.right_rect.contains(a0.pos()):
            self.hover_rect.setWidth(int(self.hover_rect.width() / 3))
            self.hover_rect.moveLeft(int(self.rect().right() - self.hover_rect.width()))
        elif self.top_rect.contains(a0.pos()):
            self.hover_rect.setHeight(int(self.hover_rect.height() / 3))
        elif self.center_rect.contains(a0.pos()):
            pass
        elif self.bottom_rect.contains(a0.pos()):
            self.hover_rect.setHeight(int(self.hover_rect.height() / 3))
            self.hover_rect.moveTop(int(self.rect().bottom() - self.hover_rect.height()))
        else:
            self.hover_rect = QRect()

        self.update()


class DragManager(QObject):
    __unique_inst: 'DragManager' = None

    def __init__(self):
        super(DragManager, self).__init__()
        self.__dock_map = {}

    @classmethod
    def instance(cls):
        if cls.__unique_inst is None:
            cls.__unique_inst = DragManager()
        return cls.__unique_inst

    def __peak_window(self, obj: QWidget):
        if obj is None:
            return None

        if obj.__class__.__name__ == "QMainWindow":
            return obj

        return self.__peak_window(obj.parent())

    def eventFilter(self, sender: QObject | None, event: QEvent | None):
        if event.type() == QEvent.Type.DragMove:
            if sender.isWindowType():
                sender.requestActivate()

            for ip in self.__dock_map:
                view_inst: QWidget = self.get_dockpanel(ip)
                if view_inst is None:
                    return False

                gpos = sender.mapToGlobal(event.pos())
                point = view_inst.mapFromGlobal(gpos)
                if (view_inst.rect().contains(point)) and (self.__peak_window(view_inst).isActiveWindow()):
                    print(view_inst.rect())

            pass

        return super(DragManager, self).eventFilter(sender, event)

    def register_dockpanel(self, view):
        self.__dock_map[str(view.__hash__())] = view

    def remove_dockpanel(self, view):
        if str(view.__hash__()) in self.__dock_map:
            self.__dock_map.pop(str(view.__hash__()))

    def get_dockpanel(self, address: str):
        if address in self.__dock_map:
            return self.__dock_map[address]
        return None


if __name__ == "__main__":
    app = QApplication([])
    accept = AcceptPanel(None)
    accept.show()
    app.exec()
