from typing import Any, Dict, List, Tuple

from utils.validator.tf_validation_rules import TFValidationRule

class TFValidator:
    """
    A validator class that manages and applies validation rules to field values.

    This class serves as a container and executor for validation rules. It can validate
    individual fields or entire data dictionaries against defined rules, including support
    for nested fields and custom validation functions.

    Attributes:
        _rules (Dict[str, TFValidationRule]): Mapping of field names to their validation rules.
        _custom_validators (Dict[str, callable]): Mapping of custom validator names to their functions.

    Example:
        >>> validator = TFValidator()
        >>> validator.add_rule('age', TFValidationRule(type_=int, min_val=0))
        >>> validator.add_custom_validator('check_email', email_validator_func)
    """
    def __init__(self):
        self._rules: Dict[str, TFValidationRule] = {}
        self._custom_validators: Dict[str, callable] = {}
    
    def add_rule(self, field_name: str, rule: TFValidationRule) -> None:
        """
        Add a validation rule for a field.

        Args:
            field_name (str): Name of the field to validate. Can be nested using dot notation
                (e.g., 'user.email').
            rule (TFValidationRule): Validation rule to apply to the field.
        """
        self._rules[field_name] = rule
    
    def add_rules(self, rules: Dict[str, TFValidationRule]) -> None:
        """
        Add multiple validation rules at once.

        Args:
            rules (Dict[str, TFValidationRule]): Mapping of field names to their validation rules.
        """
        self._rules.update(rules)
    
    def add_custom_validator(self, name: str, validator: callable) -> None:
        """
        Add a custom validation function.

        Args:
            name (str): Name to identify the custom validator.
            validator (callable): Function that takes a value and returns (bool, str) tuple
                indicating validation result and error message.
        """
        self._custom_validators[name] = validator
    
    def validate_field(self, field_name: str, value: Any) -> Tuple[bool, str]:
        """
        Validate a single field value against its rule.

        Args:
            field_name (str): Name of the field to validate.
            value (Any): Value to validate.

        Returns:
            Tuple[bool, str]: (is_valid, error_message) tuple. If valid, error_message is empty.
        """
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
        """
        Validate a dictionary of values against defined rules.

        Supports nested field validation using dot notation and special handling for
        skill validations using '_any_' key.

        Args:
            data (Dict): Dictionary of values to validate.
            is_new (bool): Whether this is new data (affects required field validation).

        Returns:
            List[str]: List of error messages. Empty list if all validations pass.
        """
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
