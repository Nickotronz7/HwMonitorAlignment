from PySide2.QtCore import Qt
from PySide2.QtGui import QMouseEvent
from PySide2.QtWidgets import QToolTip

from hwmonitor.ui.widgets.align.align_widget import AlignWidget
from hwmonitor.ui.dialogs.rollback_changes_dialog import RollbackChangesDialog
from hwmonitor.ui.widgets.align.models.align_model import AlignModel
from hwmonitor.ui.widgets.align.models.view_model import AlignViewModel


class AlignController:

    def __init__(self, vscreen):
        """Controller for the widgets on the different monitors.

        The internal model and controller is shared among all other
        widgets on the different monitors

                                Controller
            ┌─────────────   modifies models    <────────────┐
            │             and common properties              │ common
         ViewModel         │                                 │ properties
        common UI  ───┐    │                                 │ change
        properties    │    │                                 │ or general
                      ├──> ├────>   Model  ────────>  View ──┤ settings
                      │    │                                 │
                      ├──> ├────>   Model  ────────>  View ──┤
                      │    │                                 │
                      └──> └────>   Model  ────────>  View ──┘
                                 specific UI        displays
                                properties and      specific
                                     data            data


        :type vscreen: hwmonitor.vscreen.vscreen.VScreen
        """
        self.device_model = {}
        self.device_widget = {}
        self.vscreen = vscreen
        self.common_model = None

    def key_pressed(self, model: AlignModel, key):
        if key == Qt.Key_Escape:
            self.stop()
        elif key == Qt.Key_Up and not model.monitor.primary:
            model.monitor.position_y += 1
        elif key == Qt.Key_Down and not model.monitor.primary:
            model.monitor.position_y -= 1
        elif key == Qt.Key_Left and not model.monitor.primary:
            model.monitor.position_x -= 1
        elif key == Qt.Key_Right and not model.monitor.primary:
            model.monitor.position_x += 1
        elif key == Qt.Key_PageUp and not model.monitor.primary:
            model.monitor.position_y += 10
        elif key == Qt.Key_PageDown and not model.monitor.primary:
            model.monitor.position_y -= 10
        else:
            return True

    def wheel_event(self, model, event):
        return False

    def mouse_move_event(self, model, event: QMouseEvent):
        if self.common_model.show_cursor_position:
            QToolTip.showText(event.globalPos(),
                              f"{event.globalPos().x()}, {event.globalPos().y()}")
        return True

    def start(self):
        self.common_model = AlignViewModel()
        for monitor in self.vscreen.monitors:
            model = AlignModel(monitor, self.common_model, self.vscreen)
            widget = AlignWidget(self, model)
            widget.showFullScreen()

            self.device_model[monitor.device_name] = model
            self.device_widget[monitor.device_name] = widget

    def stop(self):
        for widget, model in zip(self.device_widget.values(), self.device_model.values()):
            widget.close()
            model.rollback()
        self.common_model = None
        self.device_model.clear()
        self.device_widget.clear()

    def button_apply(self, checked=False):
        """Align Widget Control Box Dialog Buttons Apply"""
        for model in self.device_model.values():
            model.apply_offset()
        self.vscreen.apply_changes()

        # Reset logic
        dialog = RollbackChangesDialog(timeout=15)
        rst = dialog.exec_()
        if rst == RollbackChangesDialog.No:
            for model in self.device_model.values():
                model.rollback()
                model.apply_offset()
            self.vscreen.apply_changes()

        for widget in self.device_widget.values():
            widget.close()

    def button_close(self, checked=False):
        """Align Widget Control Box Dialog Buttons Close"""
        self.stop()

    def button_reset(self, checked=False):
        """Align Widget Control Box Dialog Buttons Reset"""
        for model in self.device_model.values():
            model.rollback()
