from django.core.exceptions import ValidationError
import re

class UppercaseValidator:
    def validate(self, password, user=None):
        if not re.search(r'[A-Z]', password):
            raise ValidationError(
                "La contraseña debe contener al menos una letra mayúscula."
            )

    def get_help_text(self):
        return "Tu contraseña debe contener al menos una letra mayúscula."

class NumberValidator:
    def validate(self, password, user=None):
        if not re.search(r'\d', password):
            raise ValidationError(
                "La contraseña debe contener al menos un número."
            )

    def get_help_text(self):
        return "Tu contraseña debe contener al menos un número."

class SpecialCharacterValidator:
    def validate(self, password, user=None):
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            raise ValidationError(
                "La contraseña debe contener al menos un carácter especial (@, #, $, etc.)."
            )

    def get_help_text(self):
        return "Tu contraseña debe contener al menos un carácter especial (@, #, $, etc.)."
