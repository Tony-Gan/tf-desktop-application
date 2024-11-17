from typing import Dict, List
from PyQt6.QtWidgets import QVBoxLayout, QFrame

from ui.components.tf_computing_dialog import TFComputingDialog

class OccupationListDialog(TFComputingDialog):
    def __init__(self, parent, occupation_list):
        self.occupation_list = occupation_list
        button_config = [{"text": "OK", "role": "accept"}]
        super().__init__("Occupation List", parent, button_config=button_config)
        self.setup_content()

    def setup_validation_rules(self):
        pass
        
    def get_field_values(self):
        return {}
        
    def process_validated_data(self, data):
        return None
    
    def setup_content(self):
        scroll_area, container, layout = self.create_scroll_area()
        
        categories: Dict[str, List] = {}
        for occupation in self.occupation_list:
            if occupation.category not in categories:
                categories[occupation.category] = []
            categories[occupation.category].append(occupation)
        
        sorted_categories = sorted(categories.keys())
        
        for category in sorted_categories:
            category_label = self.create_label(category, bold=True)
            layout.addWidget(category_label)
            
            category_frame = QFrame()
            category_layout = QVBoxLayout(category_frame)
            category_layout.setSpacing(10)
            category_layout.setContentsMargins(10, 10, 10, 10)
            
            for occupation in sorted(categories[category], key=lambda x: x.name):
                occ_frame = QFrame()
                occ_layout = QVBoxLayout(occ_frame)
                occ_layout.setSpacing(5)
                occ_layout.setContentsMargins(10, 10, 10, 10)
                
                name_label = self.create_label(occupation.name, bold=True)
                occ_layout.addWidget(name_label)
                
                formula_text = f"Skill Points: {occupation.format_formula_for_display()}"
                formula_label = self.create_label(formula_text)
                occ_layout.addWidget(formula_label)
                
                credit_text = f"Credit Rating: {occupation.credit_rating}"
                credit_label = self.create_label(credit_text)
                occ_layout.addWidget(credit_label)
                
                skills_text = f"Skills: {occupation.format_skills()}"
                skills_label = self.create_label(skills_text)
                skills_label.setWordWrap(True)
                occ_layout.addWidget(skills_label)
                
                category_layout.addWidget(occ_frame)
            
            layout.addWidget(category_frame)
        
        main_layout = QVBoxLayout(self.content_frame)
        main_layout.addWidget(scroll_area)
        
        self.set_dialog_size(600, 800)
