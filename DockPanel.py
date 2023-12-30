from PyQt5.QtWidgets import QWidget
from PyQt5.QtWidgets import QApplication
from PyQt5.QtWidgets import QLabel
from PyQt5.QtWidgets import QVBoxLayout
from PyQt5.QtWidgets import QHBoxLayout
from PyQt5.QtWidgets import QFrame
from PyQt5.QtWidgets import QPushButton
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtCore import QSize, QPoint, QMimeData
from PyQt5.QtGui import QDrag
from Manager import DragManager


class DragHeader(QFrame):
    close_request = pyqtSignal(QWidget)
    retrieve_request = pyqtSignal(QWidget)
    adjust_request = pyqtSignal(QWidget, QPoint)

    def __init__(self, title: str, parent: 'DockPanel'):
        super().__init__(parent)

        self.__place_cube = parent
        self.__pressed_mark = (False, QPoint)

        self.layout_inst = QHBoxLayout(self)
        self.layout_inst.setSpacing(0)
        self.layout_inst.setContentsMargins(0,0,0,0)

        self.show_label=QLabel(title, self)
        self.show_label.setContentsMargins(2, 0, 0, 0)
        self.layout_inst.addWidget(self.show_label, stretch=1, alignment=Qt.AlignLeft)

        self.min_button=QPushButton("-")
        self.min_button.clicked.connect(lambda : self.retrieve_request[QWidget].emit(parent))
        self.min_button.setMaximumSize(22,22)
        self.min_button.setMaximumSize(22,22)
        self.layout_inst.addWidget(self.min_button,stretch=0, alignment=Qt.AlignRight)
        self.close_button=QPushButton("x")
        self.close_button.clicked.connect(lambda : self.close_request[QWidget].emit(parent))
        self.close_button.setMaximumSize(22,22)
        self.close_button.setMaximumSize(22,22)
        self.layout_inst.addWidget(self.close_button, stretch=0, alignment=Qt.AlignRight)
        pass

    def mousePressEvent(self, a0):
        super(DragHeader, self).mousePressEvent(a0)
        self.__pressed_mark = (True, self.__place_cube.mapToParent(a0.pos()))
        pass

    def mouseReleaseEvent(self, a0):
        super(DragHeader, self).mouseReleaseEvent(a0)
        self.__pressed_mark = (False, QPoint())
        pass

    def mouseMoveEvent(self, a0):
        super(DragHeader, self).mouseMoveEvent(a0)
        if self.__pressed_mark[0]:
            self.adjust_request[QWidget,QPoint].emit(self, self.__place_cube.mapToParent(a0.pos()))


class DockPanel(QWidget):

    def __init__(self, title:str, show_inst:QWidget|None, pinst:QWidget):
        super(DockPanel, self).__init__(pinst)

        self.setMinimumSize(60, 40)
        self.setWindowTitle(title)
        self.parent_res = pinst

        self.layout_inst = QVBoxLayout(self)
        self.layout_inst.setSpacing(0)
        self.layout_inst.setContentsMargins(0,2,0,0)

        self.drag_header = DragHeader(title, self)
        self.layout_inst.addWidget(self.drag_header)
        self.drag_header.setMinimumHeight(26)
        self.drag_header.setMaximumHeight(26)
        self.drag_header.setFrameShape(QFrame.Shape.Panel)
        self.drag_header.setFrameShadow(QFrame.Shadow.Raised)
        self.drag_header.setLineWidth(3)
        self.drag_header.adjust_request[QWidget,QPoint].connect(self.__adjust_accept)

        if show_inst is not None:
            self.layout_inst.addWidget(show_inst)
        else:
            self.layout_inst.addWidget(QWidget())

        self.default_header = True
        self.can_replace = True
        self.can_retrieve = True
        self.can_close = True

        DragManager.instance().register_dockpanel(self)
    pass

    def reset_parent_res(self, pinst):
        self.parent_res = pinst

    def setParent(self, a0):
        self.drag_header.setParent(self)
        super(DockPanel, self).setParent(a0)

    def __adjust_accept(self, view: QWidget, pt: QPoint):
        drag_trans = QDrag(self)
        mine_data = QMimeData()
        mine_data.setText("view-drags(" + str(self.__hash__()) + ")")
        drag_trans.setMimeData(mine_data)
        drag_trans.setPixmap(self.grab(self.rect()))
        drag_trans.setHotSpot(QPoint(5,5))
        drag_trans.exec()

    def __del__(self):
        DragManager.instance().remove_dockpanel(self)

    def sync_status(self):
        self.drag_header.setVisible(self.default_header)


if __name__ == "__main__":
    app=QApplication([])
    app.installEventFilter(DragManager())
    win=DockPanel("empty-window",None,None)
    win.show()
    app.exec()