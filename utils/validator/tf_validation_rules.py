import re
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Type, Union, Tuple

@dataclass
class TFValidationRule:
    """Validation rule class"""
    type_: Type = str
    required: bool = False
    min_val: Optional[Union[int, float]] = None
    max_val: Optional[Union[int, float]] = None
    pattern: Optional[str] = None
    choices: Optional[List[Any]] = None
    custom: Optional[str] = None
    error_messages: Optional[Dict[str, str]] = None

    def __post_init__(self):
        default_messages = {
            'required': "This field is required",
            'type': "Must be of type {type}",
            'min': "Must be greater than or equal to {min}",
            'max': "Must be less than or equal to {max}",
            'min_length': "Must be at least {min} characters",
            'max_length': "Cannot exceed {max} characters",
            'pattern': "Invalid format",
            'choices': "Must be one of: {choices}"
        }
        self.error_messages = {**default_messages, **(self.error_messages or {})}

    def validate(self, value: Any, is_new: bool = False) -> Tuple[bool, str]:
        """Validate value against the rule
        
        Args:
            value: Value to validate
            is_new: Whether this is a new value (if False, skip required check)
            
        Returns:
            (is_valid, error_message): Validation result and error message
        """
        # Check required only if it's a new value
        if is_new and self.required and not value:
            return False, self.error_messages['required']
        
        # If not required and empty, it's valid
        if not value and not self.required:
            return True, ""
        
        # Skip other validations if value is empty
        if not value:
            return True, ""
        
        # Type check
        try:
            value = self.type_(value)
        except (ValueError, TypeError):
            return False, self.error_messages['type'].format(type=self.type_.__name__)
        
        # String specific rules
        if isinstance(value, str):
            if self.min_val is not None and len(value) < self.min_val:
                return False, self.error_messages['min_length'].format(min=self.min_val)
            if self.max_val is not None and len(value) > self.max_val:
                return False, self.error_messages['max_length'].format(max=self.max_val)
            if self.pattern and not re.match(self.pattern, value):
                return False, self.error_messages['pattern']
        
        # Number specific rules
        if isinstance(value, (int, float)):
            if self.min_val is not None and value < self.min_val:
                return False, self.error_messages['min'].format(min=self.min_val)
            if self.max_val is not None and value > self.max_val:
                return False, self.error_messages['max'].format(max=self.max_val)
        
        # Choices check
        if self.choices is not None and value not in self.choices:
            choices_str = ', '.join(str(c) for c in self.choices)
            return False, self.error_messages['choices'].format(choices=choices_str)
        
        return True, ""
