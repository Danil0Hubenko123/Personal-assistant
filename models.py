from collections import UserDict
from datetime import datetime, timedelta
from typing import Optional, List
from .validators import ContactValidator

# ПОЛЯ (Field)

class Field:
    """Базовий клас для полів контакту."""
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
        # Використовуємо валідатор
        super().__init__(ContactValidator.validate_phone(value))

class Email(Field):
    def __init__(self, value):
        # Використовуємо валідатор
        super().__init__(ContactValidator.validate_email(value))

class Address(Field):
    pass

class Birthday(Field):
    def __init__(self, value):
        # Використовуємо валідатор
        super().__init__(ContactValidator.validate_birthday(value))

    def __str__(self):
        return self._value.strftime("%d.%m.%Y")

# ЗАПИС (Contact)

class Contact:
    """Запис контакту з ім'ям, телефонами, email, адресою та днем народження."""
    def __init__(self, name: str, address=None, email=None, birthday=None):
        self.name = Name(name)
        self.phones: List[Phone] = []
        self.address: Optional[Address] = Address(address) if address else None
        self.email: Optional[Email] = Email(email) if email else None
        self.birthday: Optional[Birthday] = Birthday(birthday) if birthday else None

    def add_phone(self, phone: str):
        # Phone клас гарантує валідацію
        self.phones.append(Phone(phone))

    def edit_phone(self, old_phone: str, new_phone: str):
        for phone_obj in self.phones:
            if phone_obj.value == old_phone:
                phone_obj.value = Phone(new_phone).value # Валідація нового номеру
                return
        raise ValueError(f"Старий номер телефону {old_phone} не знайдено.")
    
    def edit_field(self, field_name: str, new_value: str):
        # Дозволяє редагувати інші поля з валідацією
        if field_name == 'email':
            self.email = Email(new_value)
        elif field_name == 'address':
            self.address = Address(new_value)
        elif field_name == 'birthday':
            self.birthday = Birthday(new_value)
        else:
            raise ValueError(f"Поле '{field_name}' не підтримується для прямого редагування.")

    def __str__(self):
        phone_strings = '; '.join(str(p) for p in self.phones)
        bday_str = f", ДН: {self.birthday}" if self.birthday else ""
        email_str = f", Email: {self.email}" if self.email else ""
        address_str = f", Адреса: {self.address}" if self.address else ""
        return f"Ім'я: {self.name.value}, Телефон: {phone_strings}{bday_str}{email_str}{address_str}"

# КНИГА (AddressBook)

class AddressBook(UserDict):
    """Адресна книга для контактів."""
    def add_record(self, record: Contact):
        self.data[record.name.value.capitalize()] = record
        
    def find(self, name: str) -> Optional[Contact]:
        return self.data.get(name.capitalize()) 
    
    def delete(self, name: str):
        capitalized_name = name.capitalize()
        if capitalized_name in self.data:
            del self.data[capitalized_name]
        else:
            raise KeyError(f"Контакт {capitalized_name}")

    def search(self, query: str) -> List[Contact]:
        """Пошук за будь-яким полем: ім'я, телефон, email, адреса."""
        query = query.lower()
        results = []
        for record in self.data.values():
            if query in record.name.value.lower():
                results.append(record)
                continue
            for phone in record.phones:
                if query in phone.value:
                    results.append(record)
                    break
            if record.email and query in record.email.value.lower():
                results.append(record)
                continue
            if record.address and query in record.address.value.lower():
                results.append(record)
                continue
        return list(set(results))

    def get_upcoming_birthdays(self, days=7) -> str:
        """Виводить список контактів з днем народження протягом N днів, з урахуванням вихідних."""
        # ... (логіка обчислення днів народження)
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
        
        result = [f"Дні народження протягом {days} днів:"]
        for date, name in upcoming:
            result.append(f"{name}: {date.strftime('%d.%m.%Y')} ({date.strftime('%A')})")
        
        return "\n".join(result)
    
    