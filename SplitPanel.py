from Manager import DragManager
from DockPanel import DockPanel
from PyQt5.QtWidgets import QApplication, QWidget, QFrame
from enum import Enum
from PyQt5.QtCore import pyqtSignal, QPoint
from PyQt5.QtCore import QRect, Qt
from PyQt5.QtWidgets import QMainWindow


class SplitType(Enum):
    SPLIT_H = 0
    SPLIT_V = 1


class DragSplitter(QFrame):
    adjustSignal = pyqtSignal(QPoint)

    def __init__(self, split:SplitType, parent:QWidget):
        super(DragSplitter, self).__init__(parent)

        self.setFrameShape(QFrame.Shape.WinPanel)
        self.setFrameShadow(QFrame.Shadow.Raised)

        if split == SplitType.SPLIT_H:
            self.setCursor(Qt.CursorShape.SplitHCursor)
        else:
            self.setCursor(Qt.CursorShape.SplitVCursor)

        pass

    def mouseMoveEvent(self, a0):
        super().mouseMoveEvent(a0)
        up_point = self.mapToParent(a0.pos())
        self.adjustSignal.emit(up_point)


class SplitPanel(QWidget):
    def __init__(self, a: DockPanel, b: DockPanel, split: SplitType, parent:'SplitPanel' = None):
        super(SplitPanel, self).__init__(parent)

        self.splitter_widget = DragSplitter(split, self)
        self.splitter_widget.adjustSignal[QPoint].connect(self.__splitter_adjust)

        self.parent_res = parent

        self.split_member = (a, b)
        self.split_member[0].setParent(self)
        self.split_member[0].parent_res = self
        self.split_member[1].setParent(self)
        self.split_member[1].parent_res = self

        self.split_info = (split, 0.5, 7)
        self.sync_status()
        pass

    def __view_list(self) -> [DockPanel]:
        retval: [DockPanel] = [self.split_member[0], self.split_member[1]]
        return retval

    def set_split_info(self, o: SplitType, pos: float, width: float = 8):
        self.split_info = (o, pos, width)
        self.sync_status()

    def sync_status(self):
        if self.split_info[0] == SplitType.SPLIT_H:
            total_width = self.width()
            width_a = total_width * self.split_info[1]
            width_b = total_width - width_a - self.split_info[2]

            self.split_member[0].setGeometry(0, 0, int(width_a), self.height())
            self.split_member[1].setGeometry(int(width_a + self.split_info[2]), 0, int(width_b), self.height())

            handle_rect = QRect(int(width_a), 0, int(self.split_info[2]), self.height())
            self.splitter_widget.setGeometry(handle_rect)
        else:
            total_height = self.height()
            height_a = total_height * self.split_info[1]
            height_b = total_height - height_a - self.split_info[2]

            self.split_member[0].setGeometry(0, 0, self.width(), int(height_a))
            self.split_member[1].setGeometry(0, int(height_a + self.split_info[2]) - 1, self.width(), int(height_b) + 1)

            handle_rect = QRect(0, int(height_a), self.width(), int(self.split_info[2]))
            self.splitter_widget.setGeometry(handle_rect)

        self.split_member[0].setVisible(True)
        self.split_member[1].setVisible(True)
        pass

    def child(self):
        return self.split_member[0], self.split_member[1], self.split_info[0]

    def resizeEvent(self, a0):
        super().resizeEvent(a0)
        self.sync_status()

    def __splitter_adjust(self, pos: QPoint):
        if self.split_info[0] == SplitType.SPLIT_H:
            leftw = self.split_member[0].minimumWidth()
            rightw = self.split_member[1].minimumWidth()
            if (pos.x() >= leftw) and (pos.x() <= self.width() - rightw):
                self.split_info = (self.split_info[0], pos.x() / self.width(), self.split_info[2])
        else:
            toph = self.split_member[0].minimumHeight()
            bottomh = self.split_member[1].minimumHeight()
            if (pos.y() >= toph) and (pos.y() <= self.height() - bottomh):
                self.split_info = (self.split_info[0], pos.y() / self.height(), self.split_info[2])
        self.sync_status()

    def replace_view(self, new: DockPanel, old: DockPanel):
        if old in self.__view_list() and new not in self.__view_list():
            if self.split_member[0] == old:
                self.split_member = (new, self.split_member[1])
            else:
                self.split_member = (self.split_member[0], new)

            self.split_member[0].setParent(self)
            self.split_member[0].parent_res = self
            self.split_member[1].setParent(self)
            self.split_member[1].parent_res = self

            self.sync_status()
            self.update()
        pass


if __name__ == "__main__":
    app = QApplication([])
    ow = QMainWindow()
    app.installEventFilter(DragManager.instance())

    a = DockPanel("docka", None, None)
    b = DockPanel("dockb", None, None)
    c = DockPanel("dockc", None, None)
    win = SplitPanel(a, b, SplitType.SPLIT_H)
    wino = SplitPanel(win, c, SplitType.SPLIT_V)
    ow.setCentralWidget(wino)

    ow.show()
    app.exec()