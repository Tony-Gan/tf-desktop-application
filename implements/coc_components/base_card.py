from ui.components.tf_base_frame import TFBaseFrame
from ui.tf_application import TFApplication


class BaseCard(TFBaseFrame):
    def __init__(self, parent=None):
        self.parent = parent
        super().__init__(radius=5, parent=parent)

    def _setup_content(self):
        self.main_layout.setContentsMargins(10, 10, 10, 10)

    def load_data(self, p_data):
        TFApplication.instance().show_message('你忘记继承重写load_data了', 5000, 'red')

    def save_data(self, p_data):
        TFApplication.instance().show_message('你忘记继承重写save_data了', 5000, 'red')

    def enable_edit(self):
        TFApplication.instance().show_message('你忘记继承重写enable_edit了', 5000, 'red')
