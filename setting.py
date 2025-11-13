import re
from collections import UserDict
from datetime import datetime, timedelta

# -----------------------------------------------------------------
# СУТНОСТІ: ПОЛЯ (З ВАЛІДАЦІЄЮ)
# -----------------------------------------------------------------

class Field:
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
        super().__init__(self._validate_phone(value))

    @staticmethod
    def _validate_phone(phone: str) -> str:
        # Видаляємо всі символи, крім цифр
        cleaned_phone = re.sub(r'[^\d]', '', phone)
        
        # Вимога: рівно 10 цифр (наприклад, 0971234567)
        if len(cleaned_phone) != 10:
            raise ValueError("Номер телефону має містити рівно 10 цифр.")
        return cleaned_phone
    
    @Field.value.setter
    def value(self, new_value):
        # Перевизначаємо сеттер для валідації
        self._value = self._validate_phone(new_value)

class Email(Field):
    def __init__(self, value):
        super().__init__(self._validate_email(value))

    @staticmethod
    def _validate_email(email: str) -> str:
        # Регулярний вираз для перевірки email
        if not re.fullmatch(r'([a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+)', email):
            raise ValueError("Некоректний формат email.")
        return email

    @Field.value.setter
    def value(self, new_value):
        self._value = self._validate_email(new_value)

class Address(Field):
    pass
    
class Birthday(Field):
    def __init__(self, value):
        date_obj = self._validate_birthday(value)
        super().__init__(date_obj)

    @staticmethod
    def _validate_birthday(date_str: str) -> datetime.date:
        try:
            date_obj = datetime.strptime(date_str, "%d.%m.%Y").date()
            return date_obj
        except ValueError:
            raise ValueError("Не дійсний формат дати. Повинен бути 'DD.MM.YYYY'.")

    def __str__(self):
        return self._value.strftime("%d.%m.%Y")
    
    @Field.value.setter
    def value(self, new_date_str):
        self._value = self._validate_birthday(new_date_str)

class Tag(Field):
    """Поле для тегів нотаток."""
    pass

# -----------------------------------------------------------------
# СУТНОСТІ: ЗАПИСИ
# -----------------------------------------------------------------

class Record:
    """Запис контакту."""
    def __init__(self, name: str, address=None, email=None, birthday=None):
        self.name = Name(name)
        self.phones: list[Phone] = []
        self.address = Address(address) if address else None
        self.email = Email(email) if email else None
        self.birthday: Birthday | None = None
        if birthday:
            self.add_birthday(birthday)

    def add_phone(self, phone: str):
        if phone in [p.value for p in self.phones]:
            print(f"Попередження: Телефон {phone} вже існує для {self.name}.")
            return
        phone_obj = Phone(phone)
        self.phones.append(phone_obj)

    def edit_phone(self, old_phone: str, new_phone: str):
        for phone_obj in self.phones:
            if phone_obj.value == old_phone:
                phone_obj.value = new_phone 
                return
        raise ValueError(f"Старий номер телефону {old_phone} не знайдено для контакту {self.name}.")
    
    def add_birthday(self, birthday: str):
        self.birthday = Birthday(birthday)

    # Додано для підтримки Email та Address (для функції change)
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
        phone_strings = '; '.join(str(p) for p in self.phones)
        bday_str = f", ДН: {self.birthday}" if self.birthday else ""
        email_str = f", Email: {self.email}" if self.email else ""
        address_str = f", Адреса: {self.address}" if self.address else ""
        return f"Ім'я: {self.name.value}, Телефон: {phone_strings}{bday_str}{email_str}{address_str}"

class Note:
    """Запис нотатки з тегами."""
    def __init__(self, content: str, tags: list[str] = None):
        self.content = content
        self.tags: set[Tag] = set()
        if tags:
            self.add_tags(tags)
            
    def add_tags(self, tags_list: list[str]):
        for tag_str in tags_list:
            self.tags.add(Tag(tag_str.lower()))

    def edit_content(self, new_content: str):
        self.content = new_content
        
    def __str__(self):
        tags_str = ', '.join(str(t) for t in self.tags)
        return f"Вміст: '{self.content[:50]}{'...' if len(self.content) > 50 else ''}' (Теги: {tags_str})"

# -----------------------------------------------------------------
# СУТНОСТІ: КНИГИ (КОНТЕЙНЕРИ)
# -----------------------------------------------------------------

class AddressBook(UserDict):
    """Адресна книга для контактів."""
    def add_record(self, record: Record):
        self.data[record.name.value] = record
        
    def find(self, name: str) -> Record | None:
        return self.data.get(name.capitalize()) 
    
    def delete(self, name: str):
        capitalized_name = name.capitalize()
        if capitalized_name in self.data:
            del self.data[capitalized_name]
        else:
            raise KeyError(f"Контакт {capitalized_name} не знайдено.")

    def search(self, query: str) -> list[Record]:
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
        return list(set(results)) # Унікальні результати

    def get_upcoming_birthdays(self, days=7) -> str:
        """Виводить список контактів з днем народження протягом N днів."""
        today = datetime.now().date()
        upcoming = []
        
        for record in self.data.values():
            if record.birthday is None:
                continue

            bday_date = record.birthday.value
            bday_this_year = bday_date.replace(year=today.year)

            # Якщо ДН вже минув, переносимо на наступний рік
            if bday_this_year < today:
                bday_this_year = bday_date.replace(year=today.year + 1)
            
            # Різниця у днях
            days_left = (bday_this_year - today).days

            if 0 <= days_left <= days:
                congrats_date = bday_this_year
                day_of_week = congrats_date.weekday()
                
                # Перенесення з вихідних на наступний понеділок
                if day_of_week >= 5: # Субота (5) або Неділя (6)
                    days_to_monday = 7 - day_of_week
                    congrats_date += timedelta(days=days_to_monday)

                upcoming.append((congrats_date, record.name.value))
        
        if not upcoming:
            return f"Жодного дня народження протягом {days} днів."

        # Сортування за датою привітання
        upcoming.sort(key=lambda x: x[0])
        
        result = [f"Дні народження протягом {days} днів:"]
        for date, name in upcoming:
            result.append(f"{name}: {date.strftime('%d.%m.%Y')} ({date.strftime('%A')})")
        
        return "\n".join(result)

class NoteBook(UserDict):
    """Книга для нотаток."""
    def add_note(self, note: Note) -> int:
        note_id = str(len(self.data) + 1)
        self.data[note_id] = note
        return note_id

    def find(self, note_id: str) -> Note | None:
        return self.data.get(note_id)

    def delete(self, note_id: str):
        if note_id in self.data:
            del self.data[note_id]
        else:
            raise KeyError(f"Нотатку з ID {note_id} не знайдено.")

    def search_notes(self, query: str) -> list[tuple[str, Note]]:
        """Пошук за вмістом або тегами."""
        query = query.lower()
        results = []
        for note_id, note in self.data.items():
            if query in note.content.lower():
                results.append((note_id, note))
                continue
            for tag in note.tags:
                if query in tag.value.lower():
                    results.append((note_id, note))
                    break
        return results

    def sort_notes_by_tag(self, tag_query: str) -> list[tuple[str, Note]]:
        """Сортування/пошук нотаток лише за точним тегом."""
        tag_query = tag_query.lower()
        results = []
        for note_id, note in self.data.items():
            if Tag(tag_query) in note.tags:
                results.append((note_id, note))
        return results

# -----------------------------------------------------------------
# КОНТЕЙНЕР ДЛЯ ВСІХ ДАНИХ
# -----------------------------------------------------------------

class DataManager:
    """Клас для зберігання AddressBook та NoteBook."""
    def __init__(self):
        self.address_book = AddressBook()
        self.note_book = NoteBook()