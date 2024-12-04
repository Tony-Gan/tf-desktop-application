from ui.components.tf_base_dialog import TFBaseDialog


class TextDisplayDialog(TFBaseDialog):
    def __init__(self, title: str, content: dict, parent=None):
        self.content = content
        button_config = [
            {"text": "OK", "role": "accept"}
        ]
        super().__init__(title, parent, button_config)

        self.setMinimumSize(400, 300)
        self.resize(600, 400)

    def _setup_content(self) -> None:
        if title := self.content.get('title'):
            title_label = self.create_label(title, bold=True)
            title_label.setStyleSheet("font-size: 14px; margin-bottom: 10px;")
            self.content_frame.layout().addWidget(title_label)

        if paragraphs := self.content.get('paragraphs', []):
            for text in paragraphs:
                para_label = self.create_label(text)
                para_label.setWordWrap(True)
                para_label.setMinimumHeight(para_label.sizeHint().height())
                self.content_frame.layout().addWidget(para_label)

        if bullet_points := self.content.get('bullet_points', []):
            for text in bullet_points:
                bullet_label = self.create_label(f"    • {text}")
                bullet_label.setWordWrap(True)
                bullet_label.setMinimumHeight(bullet_label.sizeHint().height())
                self.content_frame.layout().addWidget(bullet_label)

        if sections := self.content.get('sections', []):
            for section in sections:
                if subtitle := section.get('subtitle'):
                    subtitle_label = self.create_label(subtitle, bold=True)
                    subtitle_label.setStyleSheet("font-size: 12px; margin-top: 10px;")
                    self.content_frame.layout().addWidget(subtitle_label)

                if content := section.get('content'):
                    content_label = self.create_label(content)
                    content_label.setWordWrap(True)
                    content_label.setMinimumHeight(content_label.sizeHint().height())
                    self.content_frame.layout().addWidget(content_label)

        self.content_frame.layout().addStretch()

    def _setup_validation_rules(self) -> None:
        pass

    def get_field_values(self) -> dict:
        return {}

    def process_validated_data(self, data: dict) -> None:
        return None

    @classmethod
    def show_text(cls, title: str, content: dict, parent=None) -> None:
        dialog = cls(title, content, parent)
        dialog.exec()
