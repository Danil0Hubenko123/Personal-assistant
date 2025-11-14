import re
from datetime import datetime

class ContactValidator:
    """Містить статичні методи для валідації полів контакту."""

    @staticmethod
    def validate_phone(phone: str) -> str:
        """Перевірка номера телефону: 10 цифр."""
        if not isinstance(phone, str):
            raise TypeError("Телефон має бути рядком.")
        # Видаляємо всі символи, крім цифр
        cleaned_phone = re.sub(r'[^\d]', '', phone)
        if len(cleaned_phone) != 10:
            raise ValueError("Номер телефону має містити рівно 10 цифр.")
        return cleaned_phone

    @staticmethod
    def validate_email(email: str) -> str:
        """Перевірка формату email."""
        if not isinstance(email, str):
            raise TypeError("Email має бути рядком.")
        # Проста валідація email: user@domain.com
        if not re.fullmatch(r'([a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+)', email):
            raise ValueError("Некоректний формат email. Використовуйте user@domain.com.")
        return email

    @staticmethod
    def validate_birthday(date_str: str) -> datetime.date:
        """Перевірка формату дати народження: ДД.ММ.РРРР."""
        if not isinstance(date_str, str):
            raise TypeError("Дата народження має бути рядком у форматі ДД.ММ.РРРР.")
        try:
            date_obj = datetime.strptime(date_str, "%d.%m.%Y").date()
            return date_obj
        except ValueError:
            raise ValueError("Не дійсний формат дати. Повинен бути 'ДД.ММ.РРРР'.")
        
        
        