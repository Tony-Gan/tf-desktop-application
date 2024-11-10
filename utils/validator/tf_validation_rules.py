import re
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Type, Union, Tuple

@dataclass
class TFValidationRule:
    """
    A rule specification class for defining field validation requirements.

    This class encapsulates all validation rules for a single field, including type checking,
    range validation, pattern matching, and custom validation rules. It provides a flexible
    way to define validation requirements with customizable error messages.

    Args:
        type_ (Type): Expected data type for the field. Defaults to str.
        required (bool): Whether the field is required. Defaults to False.
        min_val (Union[int, float], optional): Minimum value (for numbers) or length (for strings).
        max_val (Union[int, float], optional): Maximum value (for numbers) or length (for strings).
        pattern (str, optional): Regular expression pattern for string validation.
        choices (List[Any], optional): List of allowed values for the field.
        custom (str, optional): Name of custom validator function to apply.
        error_messages (Dict[str, str], optional): Custom error messages for different validation types.

    Attributes:
        error_messages (Dict[str, str]): Combined default and custom error messages.

    Example:
        >>> rule = TFValidationRule(
        ...     type_=int,
        ...     required=True,
        ...     min_val=0,
        ...     max_val=100,
        ...     error_messages={'min': 'Must be at least {min}'}
        ... )
    """
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
        """
        Validate value against the rule
        
        Args:
            value: Value to validate
            is_new: Whether this is a new value (if False, skip required check)
            
        Returns:
            (is_valid, error_message): Validation result and error message
        """
        if is_new and self.required and not value:
            return False, self.error_messages['required']
        
        if not value and not self.required:
            return True, ""
        
        if not value:
            return True, ""
        
        try:
            value = self.type_(value)
        except (ValueError, TypeError):
            return False, self.error_messages['type'].format(type=self.type_.__name__)
        
        if isinstance(value, str):
            if self.min_val is not None and len(value) < self.min_val:
                return False, self.error_messages['min_length'].format(min=self.min_val)
            if self.max_val is not None and len(value) > self.max_val:
                return False, self.error_messages['max_length'].format(max=self.max_val)
            if self.pattern and not re.match(self.pattern, value):
                return False, self.error_messages['pattern']
        
        if isinstance(value, (int, float)):
            if self.min_val is not None and value < self.min_val:
                return False, self.error_messages['min'].format(min=self.min_val)
            if self.max_val is not None and value > self.max_val:
                return False, self.error_messages['max'].format(max=self.max_val)
        
        if self.choices is not None and value not in self.choices:
            choices_str = ', '.join(str(c) for c in self.choices)
            return False, self.error_messages['choices'].format(choices=choices_str)
        
        return True, ""
