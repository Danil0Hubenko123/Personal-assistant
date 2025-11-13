

"""
3. Зберігання даних:

Усі дані (контакти, нотатки) повинні зберігатися на жорсткому диску в папці користувача.
Помічник може бути перезапущений без втрати даних.
"""

"""Вся логіка збереження даних інформації"""
import pickle
import os
from setting import DataManager # Імпортуємо клас-контейнер з setting.py

# Визначаємо шлях до файлу для збереження
DATA_FILE = "personal_assistant_data.pkl"

def save_data(data_manager: DataManager, filename=DATA_FILE):
    """Зберігає об'єкт DataManager до файлу за допомогою pickle."""
    try:
        with open(filename, "wb") as f:
            pickle.dump(data_manager, f)
        # print(f"Дані успішно збережено у {filename}")
    except Exception as e:
        print(f"Помилка при збереженні даних: {e}")

def load_data(filename=DATA_FILE) -> DataManager:
    """Завантажує об'єкт DataManager з файлу. Якщо файл не знайдено, створює новий."""
    if os.path.exists(filename):
        try:
            with open(filename, "rb") as f:
                return pickle.load(f)
        except Exception as e:
            print(f"Помилка при завантаженні даних, створюю новий менеджер: {e}")
            return DataManager()
    else:
        # print(f"Файл {filename} не знайдено. Створюю новий менеджер.")
        return DataManager()
    
    