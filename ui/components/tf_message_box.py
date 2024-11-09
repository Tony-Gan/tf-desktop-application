# ui/components/tf_message_box.py

from PyQt6.QtWidgets import QMessageBox
from typing import List

class TFMessageBox:
    """
    A customized message box wrapper for the application.
    
    This class provides a consistent interface for showing different types of
    message boxes throughout the application.
    """
    
    @staticmethod
    def question(
        parent,
        title: str,
        message: str,
        buttons: List[str] = None,
        default_button: str = None
    ) -> str:
        """Show a question message box with custom buttons.
        
        Args:
            parent: Parent widget
            title (str): Window title
            message (str): Message to display
            buttons (List[str], optional): List of button texts. 
                Defaults to ["Yes", "No", "Cancel"].
            default_button (str, optional): Text of the default button.
                Must be one of the buttons in the buttons list.
        
        Returns:
            str: Text of the clicked button
        """
        if buttons is None:
            buttons = ["Yes", "No", "Cancel"]
            
        msg_box = QMessageBox(parent)
        msg_box.setWindowTitle(title)
        msg_box.setText(message)
        
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
        """Show a warning message box.
        
        Args:
            parent: Parent widget
            title (str): Window title
            message (str): Message to display
            buttons (List[str], optional): List of button texts. 
                Defaults to ["OK"].
        
        Returns:
            str: Text of the clicked button
        """
        if buttons is None:
            buttons = ["OK"]
            
        msg_box = QMessageBox(parent)
        msg_box.setIcon(QMessageBox.Icon.Warning)
        msg_box.setWindowTitle(title)
        msg_box.setText(message)
        
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
        """Show an information message box.
        
        Args:
            parent: Parent widget
            title (str): Window title
            message (str): Message to display
            buttons (List[str], optional): List of button texts. 
                Defaults to ["OK"].
        
        Returns:
            str: Text of the clicked button
        """
        if buttons is None:
            buttons = ["OK"]
            
        msg_box = QMessageBox(parent)
        msg_box.setIcon(QMessageBox.Icon.Information)
        msg_box.setWindowTitle(title)
        msg_box.setText(message)
        
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
        """Show an error message box.
        
        Args:
            parent: Parent widget
            title (str): Window title
            message (str): Message to display
            buttons (List[str], optional): List of button texts. 
                Defaults to ["OK"].
        
        Returns:
            str: Text of the clicked button
        """
        if buttons is None:
            buttons = ["OK"]
            
        msg_box = QMessageBox(parent)
        msg_box.setIcon(QMessageBox.Icon.Critical)
        msg_box.setWindowTitle(title)
        msg_box.setText(message)
        
        button_refs = {}
        for button_text in buttons:
            button = msg_box.addButton(button_text, QMessageBox.ButtonRole.AcceptRole)
            button_refs[button] = button_text
        
        msg_box.exec()
        
        clicked_button = msg_box.clickedButton()
        return button_refs.get(clicked_button, "")
