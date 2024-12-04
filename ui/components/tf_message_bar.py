from PyQt6.QtWidgets import QLabel
from PyQt6.QtCore import QTimer, Qt, QPropertyAnimation, QPoint, QEasingCurve
from PyQt6.QtGui import QFontMetrics

from ui.components.tf_font import NotoSerifNormal

class TFMessageBar(QLabel):
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.parent = parent
        
        self.setObjectName("message_toast")
        self.setAlignment(Qt.AlignmentFlag.AlignLeft)
        self.setWordWrap(True)
        
        self.setFont(NotoSerifNormal)
        
        self.setMinimumWidth(100)
        self.setMaximumWidth(400)

        self.setStyleSheet("""
            QLabel#message_toast {
                border-radius: 8px;
                padding: 10px;
            }
        """)
        
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)

        self.slide_in_animation = QPropertyAnimation(self, b"pos")
        self.slide_in_animation.setEasingCurve(QEasingCurve.Type.OutCubic)
        self.slide_in_animation.setDuration(300)
        
        self.slide_out_animation = QPropertyAnimation(self, b"pos")
        self.slide_out_animation.setEasingCurve(QEasingCurve.Type.InCubic)
        self.slide_out_animation.setDuration(300)

        self.slide_out_animation.finished.connect(self.hide)
        
        self.hide()

    def calculate_size(self, message: str) -> tuple:
        font_metrics = QFontMetrics(self.font())
        
        single_line_width = font_metrics.horizontalAdvance(message) + 40
        
        target_width = min(single_line_width, self.maximumWidth())
        target_width = max(target_width, self.minimumWidth())
        
        text_rect = font_metrics.boundingRect(
            0, 0, target_width - 20,
            2000,
            Qt.TextFlag.TextWordWrap | Qt.TextFlag.TextExpandTabs,
            message
        )
        
        return target_width, text_rect.height() + 20
    
    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.start_slide_out()

    def enterEvent(self, event):
        current_style = self.styleSheet()
        self.setStyleSheet(current_style + """
            QLabel#message_toast {
                opacity: 0.9;
            }
        """)

    def leaveEvent(self, event):
        current_style = self.styleSheet()
        self.setStyleSheet(current_style.replace("opacity: 0.9;", ""))

    def start_slide_out(self):
        if self.parent:
            current_pos = self.pos()
            target_x = self.parent.width()
            
            self.slide_out_animation.setStartValue(current_pos)
            self.slide_out_animation.setEndValue(QPoint(target_x, current_pos.y()))
            
            self.slide_out_animation.start()

    def show_message(self, message: str, display_time=2000, colour='green') -> None:
        if self.slide_out_animation.state() == QPropertyAnimation.State.Running:
            self.slide_out_animation.stop()
        
        self.setText(message)

        width, height = self.calculate_size(message)
        self.setFixedSize(width, height)
        
        if colour == 'yellow':
            self.setStyleSheet("""
                QLabel#message_toast {
                    background-color: #FFF3CD;
                    color: #856404;
                    border: 1px solid #FFEEBA;
                    border-radius: 8px;
                    padding: 10px;
                }
            """)
        elif colour == 'green':
            self.setStyleSheet("""
                QLabel#message_toast {
                    background-color: #D4EDDA;
                    color: #155724;
                    border: 1px solid #C3E6CB;
                    border-radius: 8px;
                    padding: 10px;
                }
            """)
        else:
            self.setStyleSheet(f"""
                QLabel#message_toast {{
                    background-color: {colour};
                    border-radius: 8px;
                    padding: 10px;
                }}
            """)

        if self.parent:
            parent_width = self.parent.width()
            target_x = parent_width - self.width() - 20
            target_y = 50
            
            start_x = parent_width
            self.move(start_x, target_y)
            
            self.slide_in_animation.setStartValue(QPoint(start_x, target_y))
            self.slide_in_animation.setEndValue(QPoint(target_x, target_y))
            
            self.show()
            self.raise_()
            self.slide_in_animation.start()
        
        QTimer.singleShot(display_time, self.start_slide_out)
