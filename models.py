from collections import UserDict
from datetime import datetime, timedelta
from typing import Optional, List
from .validators import ContactValidator
import re

# ПОЛЯ (Field)

class Field:
    #Базовий клас для полів контакту.
    def __init__(self, value):
        self._value = value 
    
    def __str__(self):
        return str(self._value)
    
    @property
    def value(self):
        return self._value
    
    @value.setter
    def value(self, new_value):
        self._value = new_value

class Name(Field):
    pass

class Phone(Field):
    def __init__(self, value):
        super().__init__(ContactValidator.validate_phone(value))

class Email(Field):
    def __init__(self, value):
        super().__init__(ContactValidator.validate_email(value))

class Address(Field):
    pass

class Birthday(Field):
    def __init__(self, value):
        super().__init__(ContactValidator.validate_birthday(value))

    def __str__(self):
        return self._value.strftime("%d.%m.%Y")

# ЗАПИС (Contact)

class Contact:
    def __init__(self, name: str, address: Optional[str] = None, email: Optional[str] = None, birthday: Optional[str] = None):
        if not isinstance(name, str): raise TypeError("Ім'я має бути рядком.")
        
        self.name = Name(name)
        self.phones: List[Phone] = [] 
        
        self.address: Optional[Address] = Address(address) if address else None
        self.email: Optional[Email] = Email(email) if email else None
        self.birthday: Optional[Birthday] = Birthday(birthday) if birthday else None

    def add_phone(self, phone: str):
        self.phones.append(Phone(phone))

    def edit_phone(self, old_phone: str, new_phone: str):
        for phone_obj in self.phones:
            if phone_obj.value == old_phone:
                phone_obj.value = Phone(new_phone).value
                return
        raise ValueError(f"Старий номер телефону {old_phone} не знайдено.")
    
    def edit_field(self, field_name: str, new_value: str):
        if field_name == 'email':
            self.email = Email(new_value)
        elif field_name == 'address':
            self.address = Address(new_value)
        elif field_name == 'birthday':
            self.birthday = Birthday(new_value)
        else:
            raise ValueError(f"Поле '{field_name}' не підтримується для прямого редагування.")

    def __str__(self):
        #Виведення контакту у зручному форматі.
        phone_strings = '; '.join(str(p) for p in self.phones)
        bday_str = f" | ДН: {self.birthday}" if self.birthday else ""
        email_str = f" | Email: {self.email}" if self.email else ""
        address_str = f" | Адреса: {self.address}" if self.address else ""
        
        info = f"Ім'я: {self.name.value}, Телефон: {phone_strings}{email_str}{address_str}{bday_str}"
        return info

# КНИГА (AddressBook)

class AddressBook(UserDict):
    """Адресна книга для контактів."""
    
    #  (add_record, find, delete методи) 

    def search(self, query: str) -> List[Contact]:
        """Пошук за ім'ям, email або номером телефону (case-insensitive)."""
        query = query.lower()
        results = []
        for record in self.data.values():
            match = False
            
            # 1. Пошук за ім'ям (case-insensitive)
            if query in record.name.value.lower():
                match = True
            
            # 2. Пошук за телефоном (шукаємо в очищеному від символів рядку)
            for phone in record.phones:
                cleaned_phone = re.sub(r'[^\d]', '', phone.value)
                if query in cleaned_phone:
                    match = True
                    break
            
            # 3. Пошук за email (case-insensitive)
            if record.email and query in record.email.value.lower():
                match = True

            if match:
                results.append(record)
        return list(set(results))

    def get_upcoming_birthdays(self, days: int = 7) -> str:
        #Виводить список контактів, у яких день народження настане через N днів.
        today = datetime.now().date()
        upcoming = []
        
        for record in self.data.values():
            if record.birthday is None: continue

            bday_date = record.birthday.value
            bday_this_year = bday_date.replace(year=today.year)
            
            if bday_this_year < today:
                bday_this_year = bday_date.replace(year=today.year + 1)
            
            days_left = (bday_this_year - today).days

            if 0 <= days_left <= days:
                congrats_date = bday_this_year
                day_of_week = congrats_date.weekday()
                
                # Перенесення з вихідних на наступний понеділок
                if day_of_week >= 5: 
                    days_to_monday = 7 - day_of_week
                    congrats_date += timedelta(days=days_to_monday)

                upcoming.append((congrats_date, record.name.value))
        
        if not upcoming:
            return f"Жодного дня народження протягом {days} днів."

        upcoming.sort(key=lambda x: x[0])
        
        result = [f"Дні народження протягом {days} днів (з урахуванням перенесення на робочі дні):"]
        for date, name in upcoming:
            result.append(f"{name}: {date.strftime('%d.%m.%Y')} ({date.strftime('%A')})")
        
        return "\n".join(result)
    
    