from setting import AddressBook, Record, Note, Phone, Email, Address, Tag, DataManager
from typing import Callable
from datetime import datetime

# --- ДЕКОРАТОР та ПАРСЕР ---

def input_error(func: Callable) -> Callable:
    """Декоратор для обробки стандартних помилок введення."""
    def inner(*args, **kwargs) -> str:
        try:
            return func(*args, **kwargs)
        except (ValueError, IndexError, TypeError) as e:
            # Обробка валідації полів (Phone, Birthday, Email)
            if "Номер телефону має містити" in str(e) or "Не дійсний формат дати" in str(e) or "Некоректний формат email" in str(e):
                return f"Помилка валідації: {e}"
            if "Старий номер телефону" in str(e) or "Поле" in str(e):
                return str(e)
                
            # Обробка IndexError для команд, де не вистачає аргументів
            command = func.__name__.replace('_', '-')
            if 'note' in command:
                return f"Не вистачає аргументів для {command}. Зверніться до help."

            if command == 'add-contact' or command == 'add':
                 return "Вкажіть ім'я і телефон, а також опціонально email/адресу/д.н. (add [ім'я] [телефон] [email/None] [адреса/None] [ДД.ММ.РРРР/None])"
            elif command == 'change-contact':
                 return "Вкажіть: change [ім'я] [поле] [нове_значення] (або [старий_тел] [новий_тел] для phone)"
            elif command == 'phone':
                return "Введіть ім'я користувача. (phone [ім'я])"
            elif command == 'add-birthday' or command == 'show-birthday':
                return "Вкажіть ім'я та дату. (add-birthday [ім'я] [ДД.ММ.РРРР] | show-birthday [ім'я])"
            return f"Помилка вводу: {e}"
        except KeyError as e:
            name_to_report = e.args[0]
            return f"{name_to_report} не знайдено."
        except Exception as e:
            return f"Сталася неочікувана помилка: {e}"
    return inner

def parse_input(user_input: str) -> tuple[str, list[str]]:
    """Розбиває ввід на команду та аргументи з урахуванням багатослівних аргументів."""
    try:
        parts = user_input.split()
        if not parts:
            return "", []

        cmd = parts[0].strip().lower()
        args = parts[1:]

        # Спеціальна обробка для нотаток, де вміст може бути довгим рядком
        if cmd == "add-note" and len(args) >= 1:
            # Якщо останній аргумент схожий на теги (містить кому), відділяємо його
            if ',' in args[-1]:
                content = " ".join(args[:-1])
                tags = args[-1]
                return cmd, [content, tags]
            # Якщо тегів немає, все інше — вміст
            content = " ".join(args)
            return cmd, [content]
        
        # Обробка edit-note: [ID] [новий вміст]
        if cmd == "edit-note" and len(args) >= 2:
            note_id = args[0]
            new_content = " ".join(args[1:])
            return cmd, [note_id, new_content]

        return cmd, args
    except Exception:
        return "", []

# --- ФУНКЦІЇ-ОБРОБНИКИ КОМАНД (Contacts) ---

@input_error
def add_contact(args: list[str], dm: DataManager) -> str:
    """Додає новий контакт. add [ім'я] [телефон] [email/None] [адреса/None] [ДД.ММ.РРРР/None]"""
    if len(args) < 2:
        raise IndexError 

    name = args[0].capitalize()
    phone = args[1]
    
    # Визначаємо опціональні поля (замінюємо 'None' на None)
    email = args[2] if len(args) > 2 and args[2].lower() != 'none' else None
    address = args[3] if len(args) > 3 and args[3].lower() != 'none' else None
    birthday = args[4] if len(args) > 4 and args[4].lower() != 'none' else None

    record = dm.address_book.find(name)
    
    if record is None:
        record = Record(name, address=address, email=email, birthday=birthday)
        dm.address_book.add_record(record)
        message = f"Контакт {name} додано."
    else:
        # Оновлення існуючого контакту
        if email: record.edit_field('email', email)
        if address: record.edit_field('address', address)
        if birthday: record.add_birthday(birthday) # add_birthday оновлює, якщо існує
        message = f"Контакт {name} оновлено."

    record.add_phone(phone)
    return message


@input_error
def change_contact(args: list[str], dm: DataManager) -> str:
    """Змінює поле контакту. change [ім'я] [поле] [нове_значення] (або [старий_тел] [новий_тел])"""
    if len(args) < 3:
        raise IndexError 

    name = args[0].capitalize()
    field = args[1].lower()
    record = dm.address_book.find(name)
    
    if not record:
        raise KeyError(name)

    if field == "phone":
        if len(args) != 4:
             raise IndexError
        old_phone = args[2]
        new_phone = args[3]
        record.edit_phone(old_phone, new_phone)
        return f"Номер {old_phone} контакту {name} змінено на {new_phone}."
    elif field in ["email", "address", "birthday"]:
        new_value = args[2]
        record.edit_field(field, new_value)
        return f"Поле {field} контакту {name} змінено на {new_value}."
    else:
        return f"Поле '{field}' не підтримується для редагування."

@input_error
def show_phone(args: list[str], dm: DataManager) -> str:
    """Показує повну інформацію про контакт. phone [ім'я]"""
    if not args:
        raise IndexError

    name = args[0].capitalize()
    record = dm.address_book.find(name)
    if not record:
        raise KeyError(name)

    return str(record)

def show_all(args: list[str], dm: DataManager) -> str:
    """Показує всі контакти."""
    if not dm.address_book.data:
        return "Книга контактів порожня."
    
    result = "Усі контакти:\n"
    # Сортуємо та виводимо
    sorted_records = sorted(dm.address_book.data.values(), key=lambda r: r.name.value)
    result += "\n".join(str(record) for record in sorted_records)
    return result

@input_error
def delete_contact(args: list[str], dm: DataManager) -> str:
    """Видаляє контакт. delete-contact [ім'я]"""
    name = args[0].capitalize()
    dm.address_book.delete(name)
    return f"Контакт {name} видалено."

@input_error
def search_contacts(args: list[str], dm: DataManager) -> str:
    """Пошук контактів. search [запит]"""
    query = args[0]
    results = dm.address_book.search(query)
    if results:
        return "\n".join(str(record) for record in results)
    else:
        return f"Контакти за запитом '{query}' не знайдено."

@input_error
def add_birthday(args: list[str], dm: DataManager) -> str:
    """Додає/оновлює день народження. add-birthday [ім'я] [ДД.ММ.РРРР]"""
    if len(args) < 2:
        raise IndexError 

    name, date_str, *_ = args
    name = name.capitalize()

    record = dm.address_book.find(name)
    if not record:
        raise KeyError(name) 

    record.add_birthday(date_str)
    return f"День народження {name} додано/оновлено."

@input_error
def show_birthday(args: list[str], dm: DataManager) -> str:
    """Показує день народження. show-birthday [ім'я]"""
    if not args:
        raise IndexError

    name = args[0].capitalize()
    record = dm.address_book.find(name)
    if not record:
        raise KeyError(name)

    if record.birthday:
        return f"День народження {name}: {record.birthday}"
    else:
        return f"Для контакту {name} день народження не вказано."

@input_error
def show_birthdays(args: list[str], dm: DataManager) -> str:
    """Виводить список контактів з днем народження протягом N днів. birthdays [N] (за замовчуванням 7)"""
    days = 7
    if args:
        days = int(args[0])
        if days < 0:
            raise ValueError("Кількість днів не може бути від'ємною.")
            
    return dm.address_book.get_upcoming_birthdays(days)


# --- ФУНКЦІЇ-ОБРОБНИКИ КОМАНД (Notes) ---

@input_error
def add_note(args: list[str], dm: DataManager) -> str:
    """Додає нову нотатку. add-note [вміст] [тег1,тег2,.../None]"""
    if not args:
        raise IndexError("Вкажіть вміст нотатки.")
        
    content = args[0]
    tags = []
    
    if len(args) > 1 and args[1].lower() != 'none':
        tags = [t.strip() for t in args[1].split(',')]

    note = Note(content, tags)
    note_id = dm.note_book.add_note(note)
    return f"Нотатку додано. ID: {note_id}. Теги: {', '.join(tags)}"

@input_error
def edit_note(args: list[str], dm: DataManager) -> str:
    """Редагує вміст нотатки. edit-note [ID] [новий_вміст]"""
    if len(args) < 2:
        raise IndexError("Синтаксис: edit-note [ID] [новий_вміст]")
        
    note_id = args[0]
    new_content = args[1]
    note = dm.note_book.find(note_id)
    
    if not note:
        raise KeyError(f"Нотатку з ID {note_id}")
        
    note.edit_content(new_content)
    return f"Нотатку ID {note_id} змінено."

@input_error
def delete_note(args: list[str], dm: DataManager) -> str:
    """Видаляє нотатку. delete-note [ID]"""
    note_id = args[0]
    dm.note_book.delete(note_id)
    return f"Нотатку ID {note_id} видалено."

@input_error
def search_notes(args: list[str], dm: DataManager) -> str:
    """Пошук нотаток за вмістом або тегами. search-note [запит]"""
    query = args[0]
    results = dm.note_book.search_notes(query)
    
    if results:
        output = [f"Результати пошуку за '{query}':"]
        for note_id, note in results:
            output.append(f"ID {note_id}: {str(note)}")
        return "\n".join(output)
    else:
        return f"Нотаток за запитом '{query}' не знайдено."

@input_error
def sort_notes(args: list[str], dm: DataManager) -> str:
    """Сортування/пошук нотаток за тегами. sort-notes [тег]"""
    tag = args[0]
    results = dm.note_book.sort_notes_by_tag(tag)
    
    if results:
        output = [f"Нотатки, відсортовані за тегом '{tag}':"]
        for note_id, note in results:
            output.append(f"ID {note_id}: {str(note)}")
        return "\n".join(output)
    else:
        return f"Нотаток з тегом '{tag}' не знайдено."
        
def show_all_notes(args: list[str], dm: DataManager) -> str:
    """Показує всі нотатки."""
    if not dm.note_book:
        return "Книга нотаток порожня."
    output = ["Книга нотаток:"]
    for note_id, note in dm.note_book.items():
        output.append(f"ID {note_id}: {str(note)}")
    return "\n".join(output)
