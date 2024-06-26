from PySide2.QtCore import Qt, QRectF, QRect, QSize
from PySide2.QtGui import QPainter
from PySide2.QtWidgets import QGraphicsView, QGraphicsScene, QGraphicsLineItem, QStyle

from hwmonitor.ui.graphics.graphics_layer import GraphicsLayer
from hwmonitor.ui.widgets.align.items.alignment_line_item import AlignmentLineItem
from hwmonitor.ui.widgets.align.items.control_box_item import ControlBoxItem
from hwmonitor.ui.widgets.align.items.monitor_info_box_item import MonitorInfoBoxItem


class UiAlignWidget:

    def __init__(self, view, model):
        """UI for AlignWidgets

        :type view: PySide2.QtWidgets.QGraphicsView.QGraphicsView
        :type model: hwmonitor.ui.align.models.align_model.AlignModel
        """
        self.view = view
        self.model = model

        view.scale(1, 1)
        view.setWindowFlags(Qt.Tool)
                            # | Qt.WindowStaysOnTopHint)
        view.setStyleSheet('border: 0px; background-color: white')
        view.setViewportMargins(0, 0, 0, 0)
        view.setContentsMargins(0, 0, 0, 0)
        view.resize(*self.model.vscreen_size)
        view.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        view.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        view.setRenderHint(QPainter.Antialiasing, self.model.common_model.antialiasing)
        view.setViewportUpdateMode(QGraphicsView.MinimalViewportUpdate)
        view.setOptimizationFlag(QGraphicsView.DontAdjustForAntialiasing)

        self.graphics_scene = QGraphicsScene(view)
        view.setSceneRect(QRectF(0, 0, self.model.monitor.screen_width, self.model.monitor.screen_height))

        self.diagonal_lines_layer = GraphicsLayer(visible=self.model.common_model.show_diagonal_lines, level=1)
        self.horizontal_lines_layer = GraphicsLayer(visible=self.model.common_model.show_horizontal_lines, level=2)
        self.vertical_lines_layer = GraphicsLayer(visible=self.model.common_model.show_vertical_lines, level=3)
        self.info_box_layer = GraphicsLayer(visible=self.model.common_model.show_info_box, level=4)
        self.control_box_layer = GraphicsLayer(level=5)

        self.model.common_model.changed("show_diagonal_lines").connect(self.diagonal_lines_layer.set_visible)
        self.model.common_model.changed("show_vertical_lines").connect(self.vertical_lines_layer.set_visible)
        self.model.common_model.changed("show_horizontal_lines").connect(self.horizontal_lines_layer.set_visible)
        self.model.common_model.changed("antialiasing").connect(self._toggle_antialiasing)
        self.model.common_model.changed("show_info_box").connect(self.info_box_layer.set_visible)

        self.info_box = MonitorInfoBoxItem(self.model)
        self.control_box = ControlBoxItem(self.model.common_model)
        self.horizontal_lines = AlignmentLineItem(self.model)
        self.vertical_lines = AlignmentLineItem(self.model)

        self.create_diagonal_lines()
        self.create_vertical_lines()
        self.create_info_box()
        self.create_horizontal_lines()
        if self.model.monitor.primary:
            self.create_control_box()
        self._arrange_items()

        view.setScene(self.graphics_scene)

    def create_diagonal_lines(self):
        left_top_right_bottom = QGraphicsLineItem(0, 0,
                                                  self.model.monitor.screen_width, self.model.monitor.screen_height)
        right_top_left_bottom = QGraphicsLineItem(self.model.monitor.screen_width, 0,
                                                  0, self.model.monitor.screen_height)

        self.diagonal_lines_layer.add_to_layer(left_top_right_bottom)
        self.diagonal_lines_layer.add_to_layer(right_top_left_bottom)

        self.graphics_scene.addItem(left_top_right_bottom)
        self.graphics_scene.addItem(right_top_left_bottom)

    def create_info_box(self):
        self.info_box_layer.add_to_layer(self.info_box)
        self.graphics_scene.addItem(self.info_box)

    def create_control_box(self):
        self.control_box_layer.add_to_layer(self.control_box)
        self.graphics_scene.addItem(self.control_box)

    def create_horizontal_lines(self):
        self.horizontal_lines_layer.add_to_layer(self.horizontal_lines)
        self.graphics_scene.addItem(self.horizontal_lines)

    def create_vertical_lines(self):
        center_line = QGraphicsLineItem(self.model.monitor.screen_width/2, 0,
                                         self.model.monitor.screen_width/2, self.model.monitor.screen_height)

        
        self.vertical_lines_layer.add_to_layer(center_line)
        self.graphics_scene.addItem(center_line)

    def _toggle_antialiasing(self, antialiasing):
        self.view.setRenderHint(QPainter.Antialiasing, antialiasing)

    def _arrange_items(self):
        """
        This function is a mess and it is probably easier to achieve what I want,
        but I didn't find any way now. So keep it like this as long you dont find a better solution
        """
        info_box_size = self.info_box.windowFrameRect().toRect().size()
        if self.model.monitor.primary:
            info_box_margin = self.info_box.getWindowFrameMargins()
            control_box_size = self.control_box.windowFrameRect().toRect().size()
            control_box_margin = self.control_box.getWindowFrameMargins()

            rect = QStyle.alignedRect(
                Qt.LeftToRight,
                Qt.AlignCenter,
                self._bounding_box(
                    info_box_size,
                    control_box_size),
                QRect(0, 0,
                      self.model.monitor.screen_width,
                      self.model.monitor.screen_height)
            )
            self.info_box.setPos(rect.left() + info_box_margin[0],
                                 rect.top() + info_box_margin[1])
            self.control_box.setPos(rect.left() + info_box_size.width() + control_box_margin[0],
                                    rect.top() + (info_box_size.height() - control_box_size.height()) / 2 +
                                    control_box_margin[1])
        else:
            self.info_box.setGeometry(
                QStyle.alignedRect(
                    Qt.LeftToRight,
                    Qt.AlignCenter,
                    self.info_box.size().toSize(),
                    QRect(0, 0,
                          self.model.monitor.screen_width,
                          self.model.monitor.screen_height)
                )
            )

    def _bounding_box(self, *sizes: QSize):
        width = 0
        height = 0
        for size in sizes:
            width += size.width() if size.width() > width else 0
            height += size.height() if size.height() > height else 0
        return QSize(width, height)
