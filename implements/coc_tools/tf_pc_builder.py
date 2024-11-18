from PyQt6 import sip
from PyQt6.QtWidgets import QHBoxLayout, QFrame, QWidget, QLayout, QStackedWidget
from PyQt6.QtCore import pyqtSignal, Qt

from core.windows.tf_draggable_window import TFDraggableWindow
from ui.components.tf_date_entry import TFDateEntry
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
from implements.coc_tools.pc_builder_helper.phase3_ui import Phase3UI
from implements.coc_tools.pc_builder_helper.phase4_ui import Phase4UI
from implements.coc_tools.pc_builder_helper.phase5_ui import Phase5UI


class TFPcBuilder(TFDraggableWindow):
    metadata = TFToolMetadata(
        name="pc_builder",
        menu_path="Tools/COC",
        menu_title="Add PC Builder",
        window_title="PC Builder",
        window_size=(1080, 640),
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

        self.phase_uis = {}
        self.progress_ui = None
        self.stacked_widget = None

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

        self.stacked_widget = QStackedWidget(self)
        self.stacked_widget.setObjectName("section_frame")
        self.stacked_widget.setFrameShape(QFrame.Shape.Box)
        main_layout.addWidget(self.stacked_widget, 4)

        # TODO: REMEMBER TO CHANGE PHASE 3 BACK TO PHASE 1
        self.phase_status[PCBuilderPhase.PHASE3] = PhaseStatus.COMPLETING
        self.progress_ui.set_active_phase(self.current_phase)
        for phase, status in self.phase_status.items():
            self.progress_ui.update_status(phase, status)
        # TODO: REMEMBER TO CHANGE PHASE 3 BACK TO PHASE 1
        initial_phase = self._load_phase(PCBuilderPhase.PHASE3)
        self.stacked_widget.setCurrentWidget(initial_phase)
        initial_phase.on_enter()

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

    def _load_phase(self, phase: PCBuilderPhase) -> QWidget:
        if phase not in self.phase_uis:
            new_phase = self._create_phase_ui(phase)
            self.phase_uis[phase] = new_phase
            self.stacked_widget.addWidget(new_phase)
        return self.phase_uis[phase]

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
            return ui_classes[phase](main_window=self, parent=self.stacked_widget)
        return None

    def _update_progress_display(self):
        if self.progress_ui:
            self.progress_ui.set_active_phase(self.current_phase)
            for phase, status in self.phase_status.items():
                self.progress_ui.update_status(phase, status)

    def get_phase_status(self, phase: PCBuilderPhase) -> PhaseStatus:
        return self.phase_status.get(phase, PhaseStatus.NOT_START)
    
    def set_phase_status(self, phase: PCBuilderPhase, status: PhaseStatus):
        self.phase_status[phase] = status
        self._update_progress_display()

    def can_switch_to_phase(self, target_phase: PCBuilderPhase) -> bool:
        if target_phase.value > self.current_phase.value:
            return self.phase_status[self.current_phase] == PhaseStatus.COMPLETED
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

    def _on_phase_selected(self, phase: PCBuilderPhase):
        if phase == self.current_phase:
            return

        if self.can_switch_to_phase(phase):
            current_ui = self.phase_uis.get(self.current_phase)
            if current_ui:
                current_ui.on_exit()

            target_ui = self._load_phase(phase)

            self.current_phase = phase
            self.stacked_widget.setCurrentWidget(target_ui)
            target_ui.on_enter()

            self.progress_ui.set_active_phase(phase)
        else:
            self._show_cannot_switch_warning(phase)

    def _show_rule_settings(self):
        response = None
        if any(status != PhaseStatus.NOT_START for status in self.phase_status.values()):
            response = self.app.show_warning(
                "Change Creation Rules?",
                "You are about to change the character creation rules. This action will reset all current progress. Do you want to proceed?",
                buttons=["Yes, Reset Progress", "No, Cancel"]
            )
            if response == "No, Cancel":
                return

        confirmed, result = RuleSettingsDialog.get_input(
            self,
            current_settings=self.config.to_dict()
        )

        if confirmed:
            old_mode = self.config.generation_mode
            self.config.update_from_dict(result)

            if response == "Yes, Reset Progress" or old_mode != self.config.generation_mode:
                self._reset_progress()

            self.config_updated.emit()

    def _reset_field(self, field):
        if isinstance(field, TFDateEntry):
            field.date_field.setEnabled(True)
            field.set_value("")
        else:
            field.value_field.setEnabled(True)
            field.set_value("")

    def _reset_progress(self):
        self.pc_data.clear()
        self.phase_status = {phase: PhaseStatus.NOT_START for phase in PCBuilderPhase}
        self.phase_status[PCBuilderPhase.PHASE1] = PhaseStatus.COMPLETING

        for phase_ui in list(self.phase_uis.values()):
            if not sip.isdeleted(phase_ui):
                phase_ui.deleteLater()
        self.phase_uis.clear()

        self.current_phase = PCBuilderPhase.PHASE1
        initial_phase = self._load_phase(PCBuilderPhase.PHASE1)
        self.stacked_widget.setCurrentWidget(initial_phase)
        initial_phase.on_enter()

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

            print(f"{indent}{widget_class} {name_str} ({widget.size().width()}x{widget.size().height()}) "
                  f"{'visible' if widget.isVisible() else 'hidden'}")

            layout = widget.layout()
            if layout and not isinstance(widget, (TFValueEntry, TFOptionEntry)):
                self._print_layout_info(layout, level + 1, processed)

            for child in widget.findChildren(QWidget, options=Qt.FindChildOption.FindDirectChildrenOnly):
                if child and child.parent() is widget:
                    self._print_widget_info(child, level + 1, processed)

        except Exception as e:
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
