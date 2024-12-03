from PyQt6.QtWidgets import QHBoxLayout

from implements.components.base_card import BaseCard
from ui.components.tf_base_frame import TFBaseFrame


class Card3(BaseCard):
    def __init__(self, parent=None):
        super().__init__(parent=parent)

    def _setup_content(self):
        self.upper_frame = UpperFrame(self)
        self.items_frame = ItemsFrame(self)

        self.add_child('upper_frame', self.upper_frame)
        self.add_child('items_frame', self.items_frame)

    def load_data(self, p_data):
        pass

    def save_data(self, p_data):
        pass

    def enable_edit(self):
        pass


class UpperFrame(TFBaseFrame):
    def __init__(self, parent=None):
        super().__init__(level=1, radius=5, layout_type=QHBoxLayout, parent=parent)

    def _setup_content(self):
        self.weapons_frame = WeaponsFrame()
        self.upper_right_frame = UpperRightFrame()

        self.add_child('weapons_frame', self.weapons_frame)
        self.add_child('upper_right_frame', self.upper_right_frame)


class WeaponsFrame(TFBaseFrame):
    def __init__(self, parent=None):
        super().__init__(level=1, radius=5, parent=parent)

    def _setup_content(self):
        pass


class WeaponEntry(TFBaseFrame):
    def __init__(self, parent=None):
        super().__init__(level=1, radius=5, layout_type=QHBoxLayout, parent=parent)

    def _setup_content(self):
        pass


class UpperRightFrame(TFBaseFrame):
    def __init__(self, parent=None):
        super().__init__(level=1, radius=5, parent=parent)

    def _setup_content(self):
        self.armour_frame = ArmourFrame(self)
        self.deposit_frame = DepositFrame(self)

        self.add_child('armour_frame', self.armour_frame)
        self.add_child('deposit_frame', self.deposit_frame)


class ArmourFrame(TFBaseFrame):
    def __init__(self, parent=None):
        super().__init__(level=1, radius=5, parent=parent)

    def _setup_content(self):
        pass


class DepositFrame(TFBaseFrame):
    def __init__(self, parent=None):
        super().__init__(level=1, radius=5, parent=parent)

    def _setup_content(self):
        pass


class ItemsFrame(TFBaseFrame):
    def __init__(self, parent=None):
        super().__init__(level=1, radius=5, parent=parent)

    def _setup_content(self):
        pass
