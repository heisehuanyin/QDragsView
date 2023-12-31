from PyQt5.QtWidgets import QWidget, QApplication, QMainWindow, QMessageBox
from PyQt5.QtCore import QObject, QEvent, QRect, QMargins, Qt, QMimeData
from PyQt5.QtGui import QPainter, QColor, QDragEnterEvent, QDropEvent
from enum import Enum
import re


class PlaceArea(Enum):
    LeftArea = 0,
    RightArea = 1,
    TopArea = 2,
    BottomArea = 3,
    CenterArea = 4,
    UndefineArea = 5,


class AcceptPanel(QWidget):

    def __init__(self, mgr):
        super(AcceptPanel, self).__init__(None)
        self.left_rect = QRect()
        self.right_rect = QRect()
        self.top_rect = QRect()
        self.bottom_rect = QRect()
        self.center_rect = QRect()
        self.hover_rect = QRect()
        self.setMouseTracking(True)
        self.setAcceptDrops(True)

        self.mgr_inst = mgr
        self.target_anchor :QWidget = None
        self.target_area = PlaceArea.UndefineArea

    def resizeEvent(self, a0):
        total_rect = self.rect()
        total_rect = total_rect - QMargins(5, 5, 5, 5)
        anchor_width = 30
        self.target_area = PlaceArea.UndefineArea

        self.left_rect = QRect(int(total_rect.left()), int(total_rect.center().y() - anchor_width / 2), int(anchor_width), int(anchor_width))
        self.right_rect = QRect(int(total_rect.right() - anchor_width), int(total_rect.center().y() - anchor_width / 2), int(anchor_width), int(anchor_width))
        self.top_rect = QRect(int(total_rect.center().x() - anchor_width / 2), int(total_rect.top()), int(anchor_width), int(anchor_width))
        self.bottom_rect = QRect(int(total_rect.center().x() - anchor_width / 2), int(total_rect.bottom() - anchor_width), int(anchor_width), int(anchor_width))
        self.center_rect = QRect(int(total_rect.center().x() - anchor_width / 2), int(total_rect.center().y() - anchor_width / 2), int(anchor_width), int(anchor_width))

    def async_with(self, target_view: QWidget):
        self.resize(target_view.size())
        self.target_anchor = target_view

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

    def dragMoveEvent(self, a0):
        self.hover_rect = self.rect()

        if self.left_rect.contains(a0.pos()):
            self.hover_rect.setWidth(int(self.hover_rect.width() / 3))
            self.target_area = PlaceArea.LeftArea
        elif self.right_rect.contains(a0.pos()):
            self.target_area = PlaceArea.RightArea
            self.hover_rect.setWidth(int(self.hover_rect.width() / 3))
            self.hover_rect.moveLeft(int(self.rect().right() - self.hover_rect.width()))
        elif self.top_rect.contains(a0.pos()):
            self.target_area = PlaceArea.TopArea
            self.hover_rect.setHeight(int(self.hover_rect.height() / 3))
        elif self.center_rect.contains(a0.pos()):
            self.target_area = PlaceArea.CenterArea
            pass
        elif self.bottom_rect.contains(a0.pos()):
            self.target_area = PlaceArea.BottomArea
            self.hover_rect.setHeight(int(self.hover_rect.height() / 3))
            self.hover_rect.moveTop(int(self.rect().bottom() - self.hover_rect.height()))
        else:
            self.hover_rect = QRect()
            self.target_area = PlaceArea.UndefineArea

        self.update()

    def dragEnterEvent(self, a0: QDragEnterEvent):
        if a0.mimeData().hasFormat("text/plain"):
            content = a0.mimeData().text()
            regex = re.compile("view-drags\\(([^\\(\\)]+)\\)")
            if regex.match(content):
                a0.acceptProposedAction()

    def dropEvent(self, a0: QDropEvent):
        regex = re.compile("view-drags\\(([^\\(\\)]+)\\)")
        result = regex.match(a0.mimeData().text())
        if result:
            from SplitPanel import SplitPanel, SplitType
            from DockPanel import DockPanel
            view_id = result.group(1)
            adjust_view: DockPanel = self.mgr_inst.get_dockpanel(view_id)
            abandon_frame = adjust_view.parent_res
            if abandon_frame is None:
                QMessageBox.critical(self, "操作无效", "视图不能与自身进行替换和拼接操作！");
                self.setVisible(False)
                self.setParent(self.__peak_window(self.target_anchor))
                return

            remains_attach_frame = abandon_frame.parent_res
            target_view: DockPanel = self.target_anchor

            if self.target_area == PlaceArea.CenterArea and not target_view.can_replace:
                self.setVisible(False)
                return
            if self.target_area == PlaceArea.UndefineArea:
                self.setVisible(False)
                return

            # 移除源视图
            self_siblings = abandon_frame.child()
            if remains_attach_frame is None:
                main_window:QMainWindow = abandon_frame.parent()
                views = [self_siblings[0], self_siblings[1]]
                views.pop(views.index(adjust_view))
                main_window.setCentralWidget(views[0])
                views[0].setParent(main_window)
                views[0].parent_res = None
            else:
                if self_siblings[0] == adjust_view:
                    remains_attach_frame.replace_view(self_siblings[1], abandon_frame)
                else:
                    remains_attach_frame.replace_view(self_siblings[0], abandon_frame)

            abandon_frame.setParent(None)
            abandon_frame.parent_res = None
            del abandon_frame

            place_frame = target_view.parent_res
            split_group:QWidget = None # 声明类型
            if self.target_area == PlaceArea.LeftArea:
                split_group = SplitPanel(adjust_view, target_view, SplitType.SPLIT_H)
                split_group.set_split_info(SplitType.SPLIT_H, 1/3)
            elif self.target_area == PlaceArea.RightArea:
                split_group = SplitPanel(target_view, adjust_view, SplitType.SPLIT_H)
                split_group.set_split_info(SplitType.SPLIT_H, 2/3)
            elif self.target_area == PlaceArea.TopArea:
                split_group = SplitPanel(adjust_view, target_view, SplitType.SPLIT_V)
                split_group.set_split_info(SplitType.SPLIT_V, 1/3)
            elif self.target_area == PlaceArea.BottomArea:
                split_group = SplitPanel(target_view, adjust_view, SplitType.SPLIT_V)
                split_group.set_split_info(SplitType.SPLIT_V, 2/3)
            elif self.target_area == PlaceArea.CenterArea:
                split_group = adjust_view

            if place_frame is None:
                main_window = target_view.parent()
                main_window.setCentralWidget(split_group)
                split_group.parent_res = None
                target_view.setVisible(False)
                self.mgr_inst.remove_dockpanel(target_view)
                del target_view
            else:
                place_frame.replace_view(split_group, target_view)

            self.setVisible(False)
            self.setParent(self.__peak_window(self.target_anchor))

    def __peak_window(self, obj: QWidget):
        if obj is None:
            return None

        if obj.__class__.__name__ == "QMainWindow":
            return obj

        return self.__peak_window(obj.parent())


class DragManager(QObject):
    __unique_inst: 'DragManager' = None

    def __init__(self):
        super(DragManager, self).__init__()
        self.__dock_map = {}
        self.__accept_panel = AcceptPanel(self)
        self.__accept_panel.setVisible(False)

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
                    self.__accept_panel.setParent(view_inst)
                    self.__accept_panel.raise_()
                    self.__accept_panel.async_with(view_inst)
                    self.__accept_panel.setVisible(True)
                    pass
                pass
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
