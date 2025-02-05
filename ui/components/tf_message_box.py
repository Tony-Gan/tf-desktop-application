from typing import List

from PyQt6.QtWidgets import QMessageBox

from ui.components.tf_font import NotoSerifNormal

class TFMessageBox:
    @staticmethod
    def custom(
            parent,
            title: str,
            message: str,
            icon=None,
            button_text: str = "OK"
    ) -> None:
        msg_box = QMessageBox(parent)
        msg_box.setWindowTitle(title)
        msg_box.setText(message)
        msg_box.setFont(NotoSerifNormal)

        if icon is not None:
            if isinstance(icon, QMessageBox.Icon):
                msg_box.setIcon(icon)
            elif isinstance(icon, str):
                from PyQt6.QtGui import QPixmap
                pixmap = QPixmap(icon)
                if not pixmap.isNull():
                    scaled_pixmap = pixmap.scaled(32, 32)
                    msg_box.setIconPixmap(scaled_pixmap)

        msg_box.addButton(button_text, QMessageBox.ButtonRole.AcceptRole)

        msg_box.exec()
    
    @staticmethod
    def question(
        parent,
        title: str,
        message: str,
        buttons: List[str] = None,
        default_button: str = None
    ) -> str:
        if buttons is None:
            buttons = ["Yes", "No", "Cancel"]
            
        msg_box = QMessageBox(parent)
        msg_box.setWindowTitle(title)
        msg_box.setText(message)
        msg_box.setFont(NotoSerifNormal)
        
        button_refs = {}
        
        for button_text in buttons:
            if button_text.lower() in ["cancel", "关闭", "取消"]:
                role = QMessageBox.ButtonRole.RejectRole
            elif button_text.lower() in ["no", "don't save", "否", "不保存"]:
                role = QMessageBox.ButtonRole.DestructiveRole
            else:
                role = QMessageBox.ButtonRole.AcceptRole
            
            button = msg_box.addButton(button_text, role)
            button_refs[button] = button_text
            
            if default_button and button_text == default_button:
                msg_box.setDefaultButton(button)
        
        msg_box.exec()
        
        clicked_button = msg_box.clickedButton()
        return button_refs.get(clicked_button, "")

    @staticmethod
    def warning(
        parent,
        title: str,
        message: str,
        buttons: List[str] = None
    ) -> str:
        if buttons is None:
            buttons = ["OK"]
            
        msg_box = QMessageBox(parent)
        msg_box.setIcon(QMessageBox.Icon.Warning)
        msg_box.setWindowTitle(title)
        msg_box.setText(message)
        msg_box.setFont(NotoSerifNormal)
        
        button_refs = {}
        for button_text in buttons:
            button = msg_box.addButton(button_text, QMessageBox.ButtonRole.AcceptRole)
            button_refs[button] = button_text
        
        msg_box.exec()
        
        clicked_button = msg_box.clickedButton()
        return button_refs.get(clicked_button, "")

    @staticmethod
    def information(
        parent,
        title: str,
        message: str,
        buttons: List[str] = None
    ) -> str:
        if buttons is None:
            buttons = ["OK"]
            
        msg_box = QMessageBox(parent)
        msg_box.setIcon(QMessageBox.Icon.Information)
        msg_box.setWindowTitle(title)
        msg_box.setText(message)
        msg_box.setFont(NotoSerifNormal)
        
        button_refs = {}
        for button_text in buttons:
            button = msg_box.addButton(button_text, QMessageBox.ButtonRole.AcceptRole)
            button_refs[button] = button_text
        
        msg_box.exec()
        
        clicked_button = msg_box.clickedButton()
        return button_refs.get(clicked_button, "")

    @staticmethod
    def error(
        parent,
        title: str,
        message: str,
        buttons: List[str] = None
    ) -> str:
        if buttons is None:
            buttons = ["OK"]
            
        msg_box = QMessageBox(parent)
        msg_box.setIcon(QMessageBox.Icon.Critical)
        msg_box.setWindowTitle(title)
        msg_box.setText(message)
        msg_box.setFont(NotoSerifNormal)
        
        button_refs = {}
        for button_text in buttons:
            button = msg_box.addButton(button_text, QMessageBox.ButtonRole.AcceptRole)
            button_refs[button] = button_text
        
        msg_box.exec()
        
        clicked_button = msg_box.clickedButton()
        return button_refs.get(clicked_button, "")
