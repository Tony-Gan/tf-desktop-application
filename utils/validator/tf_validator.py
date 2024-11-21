from typing import Dict, Any, Tuple

from utils.validator.tf_validation_rules import TFValidationRule


class TFValidator:
    def __init__(self):
        self._rules: Dict[str, TFValidationRule] = {}

    def add_rule(self, field_name: str, rule: TFValidationRule) -> None:
        self._rules[field_name] = rule

    def add_rules(self, rules: Dict[str, TFValidationRule]) -> None:
        self._rules.update(rules)

    def validate_field(self, field_name: str, value: Any) -> Tuple[bool, str]:
        if field_name not in self._rules:
            return True, ""

        return self._rules[field_name].validate(value)

    def validate_fields(self, values: Dict[str, Any]) -> Dict[str, str]:
        errors = {}
        for field_name, value in values.items():
            is_valid, message = self.validate_field(field_name, value)
            if not is_valid:
                errors[field_name] = message
        return errors