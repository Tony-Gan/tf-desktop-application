from dataclasses import dataclass
from typing import Any, List, Optional, Tuple, Dict, Type, Union
from abc import ABC, abstractmethod


class TFValidationRule(ABC):
    @abstractmethod
    def validate(self, value: Any) -> Tuple[bool, str]:
        pass


@dataclass
class TFBasicRule(TFValidationRule):
    type_: Type = str
    required: bool = False
    min_val: Optional[Union[int, float]] = None
    max_val: Optional[Union[int, float]] = None
    pattern: Optional[str] = None
    choices: Optional[List[Any]] = None
    custom: Optional[str] = None
    error_messages: Optional[Dict[str, str]] = None

    def __post_init__(self):
        self.error_messages = {
            'required': "This field is required",
            'type': "Must be of type {type}",
            'min': "Must be greater than or equal to {min}",
            'max': "Must be less than or equal to {max}",
            'pattern': "Invalid format",
            'choices': "Must be one of: {choices}",
            **(self.error_messages or {})
        }

    def validate(self, value: Any) -> Tuple[bool, str]:
        if self.required and (value is None or value == ''):
            return False, self.error_messages['required']
        if not self.required and (value is None or value == ''):
            return True, ""

        try:
            self.type_(value)
        except (ValueError, TypeError):
            return False, self.error_messages['type'].format(type=self.type_.__name__)

        return True, ""


class TFAndRule(TFValidationRule):

    def __init__(self, rules: List[TFValidationRule]):
        self.rules = rules

    def validate(self, value: Any) -> Tuple[bool, str]:
        errors = []
        for rule in self.rules:
            is_valid, message = rule.validate(value)
            if not is_valid:
                errors.append(message)

        return len(errors) == 0, " AND ".join(errors)


class TFOrRule(TFValidationRule):

    def __init__(self, rules: List[TFValidationRule]):
        self.rules = rules

    def validate(self, value: Any) -> Tuple[bool, str]:
        messages = []
        for rule in self.rules:
            is_valid, message = rule.validate(value)
            if is_valid:
                return True, ""
            messages.append(message)

        return False, " OR ".join(messages)


class TFNotRule(TFValidationRule):

    def __init__(self, rule: TFValidationRule):
        self.rule = rule

    def validate(self, value: Any) -> Tuple[bool, str]:
        is_valid, message = self.rule.validate(value)
        return not is_valid, f"NOT ({message})" if is_valid else ""


@dataclass
class TFCustomRule(TFValidationRule):
    validator: callable
    error_message: str = "Validation failed"

    def validate(self, value: Any) -> Tuple[bool, str]:
        try:
            is_valid = self.validator(value)
            return is_valid, "" if is_valid else self.error_message
        except Exception as e:
            return False, str(e)
