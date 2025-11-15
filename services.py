from .models import Contact, AddressBook
from typing import Callable

# ДЕКОРАТОР input_error 

def input_error(func: Callable) -> Callable:
    """Декоратор для обробки стандартних помилок введення та валідації."""
    def inner(*args, **kwargs) -> str:
        try:
            return func(*args, **kwargs)
        except (ValueError, TypeError) as e:
            # Обробка помилок валідації
            if "Номер телефону має містити" in str(e) or "Не дійсний формат дати" in str(e) or "Некоректний формат email" in str(e) or "Дата народження не може бути" in str(e):
                return f"Помилка валідації: {e}"
            if "Старий номер телефону" in str(e) or "Поле" in str(e) or "Телефон має бути рядком" in str(e) or "Ім'я має бути рядком" in str(e):
                return str(e)
            
            command = func.__name__.replace('_', '-')
            return f"Не вистачає аргументів для {command}. Перевірте синтаксис."
        except KeyError as e:
            return f"{e.args[0]} не знайдено."
        except IndexError:
            return f"Не вистачає аргументів. Перевірте синтаксис."
        except Exception as e:
            return f"Сталася неочікувана помилка: {e}"
    return inner

# ФУНКЦІЇ-ОБРОБНИКИ КОМАНД 
# (Тут розміщено функції, які викликатимуться з main.py)

@input_error
def add_contact(args: list[str], book: AddressBook) -> str:
    """add [ім'я] [телефон] [email/None] [адреса/None] [ДД.ММ.РРРР/None]"""
    # ... (логіка додавання контакту та телефону)
    if len(args) < 2: raise IndexError 

    name = args[0].capitalize()
    phone = args[1]
    
    email = args[2] if len(args) > 2 and args[2].lower() != 'none' else None
    address = args[3] if len(args) > 3 and args[3].lower() != 'none' else None
    birthday = args[4] if len(args) > 4 and args[4].lower() != 'none' else None

    record = book.find(name)
    
    if record is None:
        record = Contact(name, address=address, email=email, birthday=birthday)
        book.add_record(record)
        message = f"Контакт {name} додано."
    else:
        if email: record.edit_field('email', email)
        if address: record.edit_field('address', address)
        if birthday: record.edit_field('birthday', birthday)
        message = f"Контакт {name} оновлено."

    record.add_phone(phone)
    return message

@input_error
def change_contact(args: list[str], book: AddressBook) -> str:
    """change [ім'я] [поле] [нове_значення] (або [старий_тел] [новий_тел])"""
    # ... (логіка редагування контакту)
    if len(args) < 3: raise IndexError 

    name = args[0].capitalize()
    field = args[1].lower()
    record = book.find(name)
    
    if not record: raise KeyError(name)

    if field == "phone":
        if len(args) != 4: raise IndexError("Для телефону: change [ім'я] phone [старий_тел] [новий_тел]")
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
def search_contacts(args: list[str], book: AddressBook) -> str:
    """Здійснює пошук контактів за ім'ям, email або номером телефону. search [запит]"""
    query = args[0]
    results = book.search(query)
    if results:
        output = [f"Результати пошуку за '{query}' ({len(results)} збігів):"]
        output.extend(str(record) for record in results)
        return "\n".join(output)
    else:
        return "Контакт не знайдено."

@input_error
def show_birthdays(args: list[str], book: AddressBook) -> str:
    """Виводить список контактів з днем народження протягом N днів. birthdays [N] (за замовчуванням 7)"""
    days = 7
    if args:
        try:
            days = int(args[0])
        except ValueError:
            raise ValueError("N (кількість днів) має бути цілим числом.")
            
        if days < 0:
            raise ValueError("Кількість днів не може бути від'ємною.")
            
    return book.get_upcoming_birthdays(days)

# Додайте інші функції-обробники (show_contact_info, show_all, delete_contact, add_birthday) за необхідності.

