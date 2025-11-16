import re
from datetime import datetime

class ContactValidator:
    # Містить статичні методи для валідації полів контакту.

    @staticmethod
    def validate_phone(phone: str) -> str:
        """Перевірка номера телефону: 10-13 цифр, без букв."""
        if not isinstance(phone, str):
            raise TypeError("Телефон має бути рядком.")
        
        # Видаляємо всі символи, крім цифр
        cleaned_phone = re.sub(r'[^\d]', '', phone)

        # Вимога: від 10 до 13 цифр (включно)
        if not (10 <= len(cleaned_phone) <= 13):
            raise ValueError(f"Номер телефону має містити від 10 до 13 цифр. Отримано: {len(cleaned_phone)}.")
        return cleaned_phone

    @staticmethod
    def validate_email(email: str) -> str:
        # Перевірка формату email (використовуючи re).
        if not isinstance(email, str):
            raise TypeError("Email має бути рядком.")
        # Базова валідація структури email
        if not re.fullmatch(r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$', email):
            raise ValueError("Некоректний формат email. Використовуйте user@domain.com.")

        # Додаткова перевірка: заборона послідовних крапок
        if '..' in email:
            raise ValueError("Email не повинен містити послідовні крапки (..).")

        # Перевірка доменної частини: не повинна починатися або закінчуватися крапкою
        domain = email.split('@')[1]
        if domain.startswith('.') or domain.endswith('.'):
            raise ValueError("Доменна частина не може починатися або закінчуватися крапкою.")

        return email

    @staticmethod
    def validate_birthday(date_str: str) -> datetime.date:
        # Перевірка формату дати народження: ДД.ММ.РРРР. 
        if not isinstance(date_str, str):
            raise TypeError("Дата народження має бути рядком у форматі ДД.ММ.РРРР.")
        try:
            date_obj = datetime.strptime(date_str, "%d.%m.%Y").date()
            if date_obj > datetime.now().date():
                raise ValueError("Дата народження не може бути у майбутньому.")
            return date_obj
        except ValueError as e:
            if "not in range" in str(e) or "unconverted data remains" in str(e):
                raise ValueError("Не дійсний формат дати. Повинен бути 'ДД.ММ.РРРР'.")
            raise e
        
        