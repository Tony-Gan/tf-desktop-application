from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import QLabel, QVBoxLayout, QHBoxLayout, QFrame

from implements.coc_tools.pc_builder_helper.pc_builder_phase import PCBuilderPhase
from implements.coc_tools.pc_builder_helper.phase_status import PhaseStatus


class PhaseProgressItem(QFrame):
    clicked = pyqtSignal(PCBuilderPhase)

    def __init__(self, phase: PCBuilderPhase, parent=None):
        super().__init__(parent)
        self.phase = phase
        self.setObjectName(f"phase_{phase.value}_progress")
        self.setCursor(Qt.CursorShape.PointingHandCursor)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(10)

        self.number_label = QLabel(str(phase.value))
        self.number_label.setFixedSize(24, 24)
        self.number_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.number_label.setStyleSheet("""
            QLabel {
                border: 1px solid black;
                border-radius: 12px;
                background: transparent;
            }
        """)
        layout.addWidget(self.number_label)

        info_layout = QVBoxLayout()
        info_layout.setSpacing(2)

        self.name_label = QLabel(f"Phase {phase.value}")
        name_font = QFont("Inconsolata")
        name_font.setPointSize(12)
        self.name_label.setFont(name_font)

        self.status_label = QLabel("Not Started")
        status_font = QFont("Inconsolata Light")
        status_font.setPointSize(10)
        self.status_label.setFont(status_font)

        info_layout.addWidget(self.name_label)
        info_layout.addWidget(self.status_label)
        layout.addLayout(info_layout)

        layout.addStretch()

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.clicked.emit(self.phase)

    def set_active(self, is_active: bool):
        if is_active:
            font = self.name_label.font()
            font.setBold(True)
            self.name_label.setFont(font)
        else:
            self.setStyleSheet(self.styleSheet().replace(
                "background-color: rgba(0, 0, 0, 0.1);", ""
            ))
            font = self.name_label.font()
            font.setBold(False)
            self.name_label.setFont(font)

    def set_status(self, status: PhaseStatus):
        status_styles = {
            PhaseStatus.NOT_START: ("Not Started", "#666"),
            PhaseStatus.COMPLETING: ("In Progress", "#1a73e8"),
            PhaseStatus.COMPLETED: ("Completed", "#0f9d58")
        }
        text, color = status_styles.get(status, ("Unknown", "#666"))
        self.status_label.setText(text)
        self.status_label.setStyleSheet(f"color: {color};")