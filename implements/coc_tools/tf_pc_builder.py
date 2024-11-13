from PyQt6.QtWidgets import QHBoxLayout, QVBoxLayout, QFrame, QWidget, QLayout
from PyQt6.QtCore import pyqtSignal, QCoreApplication, Qt

from core.windows.tf_draggable_window import TFDraggableWindow
from ui.components.tf_option_entry import TFOptionEntry
from ui.components.tf_value_entry import TFValueEntry
from utils.registry.tf_tool_matadata import TFToolMetadata
from utils.validator.tf_validator import TFValidator
from ui.components.tf_settings_widget import MenuSection
from implements.coc_tools.pc_builder_helper.pc_builder_config import PCBuilderConfig
from implements.coc_tools.pc_builder_helper.rule_setting_dialog import RuleSettingsDialog
from implements.coc_tools.pc_builder_helper.pc_builder_phase import  PCBuilderPhase
from implements.coc_tools.pc_builder_helper.phase_status import PhaseStatus
from implements.coc_tools.pc_builder_helper.progress_container import ProgressContainer
from implements.coc_tools.pc_builder_helper.phase1_ui import Phase1UI
from implements.coc_tools.pc_builder_helper.phase2_ui import Phase2UI
from implements.coc_tools.pc_builder_helper.phase_ui import Phase3UI, Phase4UI, Phase5UI


class TFPcBuilder(TFDraggableWindow):
    metadata = TFToolMetadata(
        name="pc_builder",
        menu_path="Tools/COC",
        menu_title="Add PC Builder",
        window_title="PC Builder",
        window_size=(960, 600),
        description="PC builder",
        max_instances=1
    )

    config_updated = pyqtSignal()

    def __init__(self, parent=None):
        self.validator = TFValidator()
        PCBuilderConfig.setup_validator(self.validator)
        self.config = PCBuilderConfig()

        self.pc_data = {}

        self.current_phase = PCBuilderPhase.PHASE1
        self.phase_status = {phase: PhaseStatus.NOT_START for phase in PCBuilderPhase}
        self.phase_uis = {phase: None for phase in PCBuilderPhase}

        self.progress_ui = None
        self.phase_container = None

        super().__init__(parent)

        self._setup_menu()
        self._setup_shortcut()

    def initialize_window(self):
        main_layout = QHBoxLayout(self.content_container)
        main_layout.setContentsMargins(5, 5, 5, 5)
        main_layout.setSpacing(10)

        self.progress_ui = ProgressContainer(self)
        self.progress_ui.setObjectName("section_frame")
        self.progress_ui.setFrameShape(QFrame.Shape.Box)
        self.progress_ui.phase_selected.connect(self._on_phase_selected)
        main_layout.addWidget(self.progress_ui, 1)

        self.progress_ui.set_active_phase(self.current_phase)
        for phase, status in self.phase_status.items():
            self.progress_ui.update_status(phase, status)

        self.phase_container = QFrame(self)
        self.phase_container.setObjectName("section_frame")
        self.phase_container.setFrameShape(QFrame.Shape.Box)
        main_layout.addWidget(self.phase_container, 4)
        self.load_phase_ui()

    def get_tooltip_hover_text(self):
        return "Unfinished"

    def _setup_menu(self):
        self.rule_settings_action = self.menu_button.add_action(
            "Rule Settings",
            self._show_rule_settings,
            MenuSection.CUSTOM
        )
        self.debug_layout_action = self.menu_button.add_action(
            "Debug Layouts",
            self._debug_layouts,
            MenuSection.CUSTOM
        )

    def _setup_shortcut(self):
        pass

    def _create_phase_ui(self, phase: PCBuilderPhase):
        ui_classes = {
            PCBuilderPhase.PHASE1: Phase1UI,
            PCBuilderPhase.PHASE2: Phase2UI,
            PCBuilderPhase.PHASE3: Phase3UI,
            PCBuilderPhase.PHASE4: Phase4UI,
            PCBuilderPhase.PHASE5: Phase5UI
        }

        if phase in ui_classes:
            return ui_classes[phase](main_window=self, parent=self.phase_container)
        return None

    def load_phase_ui(self):
        old_widgets = []
        if self.phase_container.layout():
            while self.phase_container.layout().count():
                item = self.phase_container.layout().takeAt(0)
                if item.widget():
                    old_widgets.append(item.widget())

        new_ui = self._create_phase_ui(self.current_phase)
        self.phase_uis[self.current_phase] = new_ui

        if not new_ui:
            return

        new_layout = QVBoxLayout()
        new_layout.setContentsMargins(0, 0, 0, 0)

        if self.phase_container.layout():
            QWidget().setLayout(self.phase_container.layout())
        self.phase_container.setLayout(new_layout)

        self._clear_content_area(self.phase_container)
        new_layout.addWidget(new_ui)

        for widget in old_widgets:
            widget.deleteLater()

        new_ui.show()

        QCoreApplication.processEvents()

    def _clear_content_area(self, widget):
        if widget.objectName() == "content_area" and isinstance(widget, QFrame):
            if widget.layout():
                while widget.layout().count():
                    item = widget.layout().takeAt(0)
                    child_widget = item.widget()
                    if child_widget:
                        child_widget.deleteLater()
                QWidget().setLayout(widget.layout())
            return True 

        for child in widget.findChildren(QWidget):
            if self._clear_content_area(child):
                return True

        return False

    def _update_progress_display(self):
        if self.progress_ui:
            self.progress_ui.set_active_phase(self.current_phase)
            for phase, status in self.phase_status.items():
                self.progress_ui.update_status(phase, status)

    def set_phase_status(self, phase: PCBuilderPhase, status: PhaseStatus):
        self.phase_status[phase] = status
        self._update_progress_display()

    def can_switch_to_phase(self, target_phase: PCBuilderPhase) -> bool:
        if target_phase.value < self.current_phase.value:
            return self.phase_status[target_phase] == PhaseStatus.COMPLETED

        if target_phase.value > self.current_phase.value:
            if self.phase_status[self.current_phase] != PhaseStatus.COMPLETED:
                return False

            phase_list = list(PCBuilderPhase)
            current_idx = phase_list.index(self.current_phase)
            target_idx = phase_list.index(target_phase)

            for idx in range(current_idx + 1, target_idx):
                if self.phase_status[phase_list[idx]] != PhaseStatus.COMPLETED:
                    return False

            return True

        return True

    def _show_cannot_switch_warning(self, target_phase: PCBuilderPhase):
        if target_phase.value > self.current_phase.value:
            self.app.show_warning(
                "Cannot Switch Phase",
                "Please complete all previous phases before proceeding.",
                buttons=["OK"]
            )
        else:
            self.app.show_warning(
                "Cannot Switch Phase",
                "You cannot return to a phase that hasn't been started yet.",
                buttons=["OK"]
            )

    def can_proceed_to_next_phase(self):
        # TODO: TEMP DEBUG
        return self.phase_status[self.current_phase] == PhaseStatus.COMPLETED or 1 == 1

    def proceed_to_next_phase(self) -> bool:
        if not self.can_proceed_to_next_phase():
            return False

        current_idx = list(PCBuilderPhase).index(self.current_phase)
        if current_idx < len(PCBuilderPhase) - 1:
            next_phase = list(PCBuilderPhase)[current_idx + 1]

            self.current_phase = next_phase
            self.load_phase_ui()
            return True
        return False

    def get_current_phase_number(self):
        return self.current_phase.value

    def _on_phase_selected(self, phase: PCBuilderPhase):
        if phase != self.current_phase:

            if self.can_switch_to_phase(phase):
                if self.phase_status[phase] == PhaseStatus.NOT_START:
                    self.phase_status[phase] = PhaseStatus.COMPLETING
                self.current_phase = phase
                self.load_phase_ui()
            else:
                self._show_cannot_switch_warning(phase)

    def _show_rule_settings(self):
        if any(status != PhaseStatus.NOT_START for status in self.phase_status.values()):
            response = self.app.show_warning(
                "Change Creation Rules?",
                "You are about to change the character creation rules. This action will reset all current progress. Do you want to proceed?",
                buttons=["Yes, Reset Progress", "No, Cancel"]
            )
            if response == "No, Cancel":
                return
            elif response == "Yes, Reset Progress":
                self._reset_progress()

        confirmed, result = RuleSettingsDialog.get_input(
            self,
            current_settings=self.config.to_dict()
        )

        if confirmed:
            self.config.update_from_dict(result)
            self.config_updated.emit()

    def _reset_progress(self):
        self.pc_data.clear()

        self.phase_status = {
            phase: PhaseStatus.NOT_START for phase in PCBuilderPhase
        }
        self.phase_status[PCBuilderPhase.PHASE1] = PhaseStatus.COMPLETING
        if self.current_phase != PCBuilderPhase.PHASE1:
            self.current_phase = PCBuilderPhase.PHASE1
            if self.phase_uis[PCBuilderPhase.PHASE1]:
                self.phase_uis[PCBuilderPhase.PHASE1]._reset_content()
                self.phase_container.layout().addWidget(self.phase_uis[PCBuilderPhase.PHASE1])
        else:
            if self.phase_uis[PCBuilderPhase.PHASE1]:
                self.phase_uis[PCBuilderPhase.PHASE1]._reset_content()

        self._update_progress_display()

    def closeEvent(self, event):
        self.closed.emit(self)
        super().closeEvent(event)

    def _debug_layouts(self):
        try:
            print("\n=== Layout Debug ===")
            self._print_widget_info(self.content_container, 0)
            print("==================\n")
        except Exception as e:
            print(f"Debug Error: {str(e)}")

    def _print_widget_info(self, widget: QWidget, level: int, processed=None):
        if processed is None:
            processed = set()

        if widget is None or not isinstance(widget, QWidget):
            return

        widget_id = id(widget)
        if widget_id in processed:
            return
        processed.add(widget_id)

        try:
            indent = "  " * level
            obj_name = widget.objectName()
            name_str = f'"{obj_name}"' if obj_name else "no name"
            widget_class = widget.__class__.__name__

            # 只打印核心信息
            print(f"{indent}{widget_class} {name_str} ({widget.size().width()}x{widget.size().height()}) "
                  f"{'visible' if widget.isVisible() else 'hidden'}")

            # 处理布局
            layout = widget.layout()
            if layout and not isinstance(widget, (TFValueEntry, TFOptionEntry)):  # 跳过这些组件的布局打印
                self._print_layout_info(layout, level + 1, processed)

            # 处理子部件
            for child in widget.findChildren(QWidget, options=Qt.FindChildOption.FindDirectChildrenOnly):
                if child and child.parent() is widget:
                    self._print_widget_info(child, level + 1, processed)

        except Exception as e:
            # 忽略特定类型的错误
            if "'QHBoxLayout' object is not callable" not in str(e):
                print(f"{indent}Error: {str(e)}")

    def _print_layout_info(self, layout: QLayout, level: int, processed):
        if layout is None:
            return

        try:
            indent = "  " * level
            obj_name = layout.objectName()
            name_str = f'"{obj_name}"' if obj_name else "no name"
            print(f"{indent}[{layout.__class__.__name__}] {name_str} {layout.count()} items")

        except Exception as e:
            if "'QHBoxLayout' object is not callable" not in str(e):
                print(f"{indent}Layout Error: {str(e)}")
