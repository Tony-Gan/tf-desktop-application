from PyQt6.QtWidgets import QFrame

class TFSeparator(QFrame):
    
    def __init__(self, 
                 orientation='horizontal',
                 margin_left=20,
                 margin_right=20,
                 margin_top=0,
                 margin_bottom=0,
                 height=1,
                 parent=None):
        super().__init__(parent)
        
        if orientation == 'horizontal':
            self.setFrameShape(QFrame.Shape.HLine)
            self.setMaximumHeight(height)
        else:
            self.setFrameShape(QFrame.Shape.VLine)
            self.setMaximumWidth(height)
        
        self.setFrameShadow(QFrame.Shadow.Sunken)
        
        self.setContentsMargins(margin_left, margin_top, 
                              margin_right, margin_bottom)
        
    @classmethod
    def horizontal(cls, parent=None):
        return cls(orientation='horizontal', parent=parent)
    
    @classmethod
    def vertical(cls, parent=None):
        return cls(orientation='vertical', 
                  margin_left=0, margin_right=0,
                  margin_top=20, margin_bottom=20,
                  parent=parent)
    
    @classmethod
    def compact(cls, parent=None):
        return cls(orientation='horizontal',
                  margin_left=0, margin_right=0,
                  margin_top=0, margin_bottom=0,
                  parent=parent)