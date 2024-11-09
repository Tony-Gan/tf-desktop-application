from typing import Any, Dict, List, Tuple

from utils.validator.tf_validation_rules import TFValidationRule

class TFValidator:

    def __init__(self):
        self._rules: Dict[str, TFValidationRule] = {}
        self._custom_validators: Dict[str, callable] = {}
    
    def add_rule(self, field_name: str, rule: TFValidationRule) -> None:
        self._rules[field_name] = rule
    
    def add_rules(self, rules: Dict[str, TFValidationRule]) -> None:
        self._rules.update(rules)
    
    def add_custom_validator(self, name: str, validator: callable) -> None:
        self._custom_validators[name] = validator
    
    def validate_field(self, field_name: str, value: Any) -> Tuple[bool, str]:
        if field_name not in self._rules:
            return True, ""
            
        rule = self._rules[field_name]
        is_valid, message = rule.validate(value)
        
        if is_valid and rule.custom:
            validator = self._custom_validators.get(rule.custom)
            if validator:
                is_valid, message = validator(value)
                
        return is_valid, message
    
    def validate_dict(self, data: Dict, is_new: bool = False) -> List[str]:
        errors = []
        
        for field_name, rule in self._rules.items():
            if '.' not in field_name:
                continue
                
            section, key = field_name.split('.', 1)
            if section not in data:
                continue

            if section == 'skills' and key == '_any_':
                for skill_name, value in data[section].items():
                    is_valid, message = rule.validate(value, is_new)
                    if not is_valid:
                        errors.append(f"Skill '{skill_name}': {message}")
                continue
                
            value = data[section].get(key)
            is_valid, message = rule.validate(value, is_new)
            if not is_valid:
                errors.append(f"Field '{field_name}': {message}")
        
        return errors
