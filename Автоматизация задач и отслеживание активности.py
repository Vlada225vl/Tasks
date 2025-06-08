import customtkinter as ctk
from tkinter import ttk, messagebox
from tkcalendar import Calendar
import datetime
import re
import sqlite3
from typing import List, Tuple, Dict, Any

# Инициализация базы данных
def init_db():
    conn = sqlite3.connect('tasks.db')
    cursor = conn.cursor()
    
    # Создаем таблицу пользователей, если ее нет
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        full_name TEXT NOT NULL,
        position TEXT NOT NULL,
        birth_date TEXT,
        phone TEXT,
        email TEXT,
        status TEXT,
        role TEXT,
        password TEXT
    )
    ''')
    
    # Создаем таблицу задач, если ее нет
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS tasks (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        sender_id INTEGER NOT NULL,
        receiver_id INTEGER NOT NULL,
        task_text TEXT NOT NULL,
        deadline TEXT NOT NULL,
        status TEXT NOT NULL,
        comment TEXT,
        FOREIGN KEY (sender_id) REFERENCES users(id),
        FOREIGN KEY (receiver_id) REFERENCES users(id)
    )
    ''')
    
    # Создаем таблицу отделов, если ее нет
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS departments (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL UNIQUE
    )
    ''')
    
    # Добавляем тестовые данные, если их нет
    add_test_data(cursor)
    
    conn.commit()
    conn.close()

def add_test_data(cursor):
    """Добавляет тестовые данные в базу, если их нет"""
    # Проверяем, есть ли уже тестовые отделы
    cursor.execute("SELECT COUNT(*) FROM departments")
    if cursor.fetchone()[0] == 0:
        departments = ["Учителя математики", "Отдел кадров", "Администрация"]
        for dept in departments:
            cursor.execute("INSERT INTO departments (name) VALUES (?)", (dept,))
    
    # Проверяем, есть ли уже тестовые пользователи
    cursor.execute("SELECT COUNT(*) FROM users")
    if cursor.fetchone()[0] == 0:
        test_users = [
            ("Иванов И.И.", "Учителя математики", "15.03.1980", "+7 (123) 456-7890", 
             "ivanov@example.com", "Активен", "Пользователь", "password1"),
            ("Петров П.П.", "Учителя математики", "20.05.1975", "+7 (987) 654-3210", 
             "petrov@example.com", "Активен", "Пользователь", "password2"),
            ("Сидоров С.С.", "Учителя математики", "10.10.1985", "+7 (555) 123-4567", 
             "sidorov@example.com", "Неактивен", "Пользователь", "password3"),
            ("Смирнова А.А.", "Отдел кадров", "05.07.1990", "+7 (111) 222-3333", 
             "smirnova@example.com", "Активен", "Администратор", "password4"),
            ("Кузнецова Е.В.", "Отдел кадров", "25.12.1988", "+7 (444) 555-6666", 
             "kuznetsova@example.com", "Неактивен", "Пользователь", "password5"),
            ("Васильева О.И.", "Администрация", "12.06.1970", "+7 (777) 888-9999", 
             "vasileva@example.com", "Активен", "Администратор", "password6"),
            ("Николаев Д.С.", "Администрация", "30.09.1965", "+7 (999) 888-7777", 
             "nikolaev@example.com", "Активен", "Администратор", "password7"),
            ("Федорова М.К.", "Администрация", "18.02.1978", "+7 (666) 555-4444", 
             "fedorova@example.com", "Неактивен", "Пользователь", "password8"),
            ("Выгузова Влада Михайловна", "Администрация", "01.01.1985", "+7 (123) 456-7890", 
             "vyguzova@example.com", "Активен", "Администратор", "admin")
        ]
        
        for user in test_users:
            cursor.execute('''
            INSERT INTO users (full_name, position, birth_date, phone, email, status, role, password)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', user)
    
    # Проверяем, есть ли уже тестовые задачи
    cursor.execute("SELECT COUNT(*) FROM tasks")
    if cursor.fetchone()[0] == 0:
        # Получаем ID пользователей
        cursor.execute("SELECT id, full_name FROM users")
        users = {name: id for id, name in cursor.fetchall()}
        
        test_tasks = [
            (users["Иванов И.И."], users["Выгузова Влада Михайловна"], 
             "Подготовить материалы к уроку", "15.05.2023 10:00", "В работе", "Нужно к следующей неделе"),
            (users["Смирнова А.А."], users["Выгузова Влада Михайловна"], 
             "Оформить приказ", "10.05.2023 14:00", "Выполнено", ""),
            (users["Васильева О.И."], users["Выгузова Влада Михайловна"], 
             "Подготовить отчет", "20.05.2023 16:00", "Новый", "Срочно!"),
            (users["Выгузова Влада Михайловна"], users["Петров П.П."], 
             "Проверить контрольные", "12.05.2023 11:00", "В работе", ""),
            (users["Выгузова Влада Михайловна"], users["Николаев Д.С."], 
             "Организовать собрание", "18.05.2023 15:00", "Новый", "С участием родителей"),
            (users["Выгузова Влада Михайловна"], users["Федорова М.К."], 
             "Подготовить презентацию", "22.05.2023 12:00", "Новый", "Для педсовета")
        ]
        
        for task in test_tasks:
            cursor.execute('''
            INSERT INTO tasks (sender_id, receiver_id, task_text, deadline, status, comment)
            VALUES (?, ?, ?, ?, ?, ?)
            ''', task)

# Инициализируем базу данных при импорте
init_db()

class DropdownMenu(ctk.CTkToplevel):
    def __init__(self, parent, x, y, commands):
        super().__init__()
        self.parent = parent
        self.commands = commands
        
        # Настройки окна меню
        self.overrideredirect(True)
        self.geometry(f"+{x}+{y}")
        self.attributes("-topmost", True)
        self.focus_set()
        
        # Создаем фрейм для меню
        self.menu_frame = ctk.CTkFrame(self, fg_color="white", border_width=1, border_color="#e0e0e0")
        self.menu_frame.pack(padx=0, pady=0)
        
        # Добавляем кнопку закрытия (крестик)
        close_btn = ctk.CTkButton(self.menu_frame,
                                text="×",
                                font=("Arial", 12, "bold"),
                                width=20,
                                height=20,
                                fg_color="transparent",
                                hover_color="#f5f5f5",
                                text_color="black",
                                command=self.destroy)
        close_btn.pack(anchor="ne", padx=5, pady=5)
        
        # Добавляем кнопки меню
        for text, command in commands.items():
            btn = ctk.CTkButton(self.menu_frame,
                               text=text,
                               font=("Arial", 12),
                               fg_color="transparent",
                               hover_color="#f5f5f5",
                               text_color="black",
                               anchor="w",
                               command=lambda cmd=command: self.execute_command(cmd))
            btn.pack(fill="x", padx=5, pady=2)
    
    def execute_command(self, command):
        self.destroy()  # Сначала закрываем меню
        command()       # Затем выполняем команду

class UserInfoWindow(ctk.CTkToplevel):
    def __init__(self, parent, user_info):
        super().__init__(parent)
        self.title("Информация о пользователе")
        self.geometry("350x300")
        self.configure(fg_color="#d5f5e3")
        
        # Основной фрейм
        main_frame = ctk.CTkFrame(self, fg_color="transparent")
        main_frame.pack(pady=20, padx=20, fill="both", expand=True)
        
        # Отображаем информацию о пользователе
        labels = ["ФИО:", "Должность/отдел:", "Дата рождения:", "Телефон:", "Электронная почта:"]
        
        for i, (label_text, value) in enumerate(zip(labels, user_info)):
            # Фрейм для каждой строки информации
            row_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
            row_frame.pack(fill="x", pady=2)
            
            # Метка с названием поля
            label = ctk.CTkLabel(row_frame, 
                               text=label_text, 
                               font=("Arial", 12, "bold"),
                               width=150,
                               anchor="w")
            label.pack(side="left", padx=(0, 10))
            
            # Значение
            value_label = ctk.CTkLabel(row_frame, 
                                     text=value, 
                                     font=("Arial", 12),
                                     anchor="w")
            value_label.pack(side="left", fill="x", expand=True)
        
        # Кнопка ОК
        ok_button = ctk.CTkButton(main_frame,
                                 text="OK",
                                 fg_color="#007bff",
                                 hover_color="#0056b3",
                                 command=self.destroy)
        ok_button.pack(pady=20)

class TaskInfoWindow(ctk.CTkToplevel):
    """Базовый класс для окон информации о задачах"""
    def __init__(self, parent, task_id: int, task_type: str, app_instance):
        super().__init__(parent)
        self.parent = parent
        self.task_id = task_id
        self.task_type = task_type
        self.app_instance = app_instance
        self.configure(fg_color="#d5f5e3")
        
    def load_task_data(self) -> Tuple[Any, ...]:
        """Загружает данные задачи из базы данных"""
        conn = sqlite3.connect('tasks.db')
        cursor = conn.cursor()
        
        cursor.execute('''
        SELECT 
            s.full_name, 
            s.position, 
            t.task_text, 
            t.deadline, 
            t.status, 
            t.comment,
            t.id,
            t.sender_id,
            t.receiver_id
        FROM tasks t
        JOIN users s ON t.sender_id = s.id
        WHERE t.id = ?
        ''', (self.task_id,))
        
        task_data = cursor.fetchone()
        conn.close()
        return task_data

class MyTaskInfoWindow(TaskInfoWindow):
    """Окно информации о задаче для раздела 'Мои задачи'"""
    def __init__(self, parent, task_id: int, task_type: str, app_instance):
        super().__init__(parent, task_id, task_type, app_instance)
        self.title("Информация о задаче")
        self.geometry("500x330")
        
        self.valid_statuses = ["Новая", "В работе", "Завершена", "Отменена"]
        self.deletable_statuses = ["Завершена", "Отменена"]
        
        self.task_data = self.load_task_data()
        if not self.task_data:
            messagebox.showerror("Ошибка", "Не удалось загрузить данные задачи")
            self.destroy()
            return
        
        main_frame = ctk.CTkFrame(self, fg_color="transparent")
        main_frame.pack(pady=15, padx=20, fill="both", expand=True)
        
        # Отображение информации (только для чтения)
        labels = ["ФИО отправителя:", "Должность/отдел:", "Текст задачи:", "Срок выполнения:"]
        for i, (label_text, value) in enumerate(zip(labels, self.task_data[:4])):
            row_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
            row_frame.pack(fill="x", pady=2)
            
            label = ctk.CTkLabel(row_frame, 
                               text=label_text, 
                               font=("Arial", 12, "bold"),
                               width=150,
                               anchor="w")
            label.pack(side="left", padx=(0, 10))
            
            value_label = ctk.CTkLabel(row_frame, 
                                     text=value, 
                                     font=("Arial", 12),
                                     anchor="w")
            value_label.pack(side="left", fill="x", expand=True)
        
        # Статус задачи
        status_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        status_frame.pack(fill="x", pady=(10, 2))
        
        ctk.CTkLabel(status_frame, 
                    text="Статус задачи:", 
                    font=("Arial", 12, "bold"),
                    width=150,
                    anchor="w").pack(side="left", padx=(0, 10))
        
        self.status_entry = ctk.CTkEntry(status_frame)
        self.status_entry.insert(0, self.task_data[4])
        self.status_entry.pack(side="left", fill="x", expand=True)
        
        # Подсказка о статусах
        status_hint_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        status_hint_frame.pack(fill="x", pady=(0, 2))
        
        ctk.CTkLabel(status_hint_frame, 
                    text="Допустимые статусы:", 
                    font=("Arial", 10),
                    anchor="w").pack(side="left", padx=(0, 10))
        
        ctk.CTkLabel(status_hint_frame, 
                    text=", ".join(self.valid_statuses), 
                    font=("Arial", 10),
                    text_color="#666666",
                    anchor="w").pack(side="left")
        
        # Комментарий
        comment_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        comment_frame.pack(fill="x", pady=(5, 2))
        
        ctk.CTkLabel(comment_frame, 
                    text="Комментарий:", 
                    font=("Arial", 12, "bold"),
                    width=150,
                    anchor="w").pack(side="left", padx=(0, 10))
        
        self.comment_entry = ctk.CTkEntry(comment_frame)
        self.comment_entry.insert(0, self.task_data[5])
        self.comment_entry.pack(side="left", fill="x", expand=True)
        
        # Кнопки
        buttons_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        buttons_frame.pack(fill="x", pady=(10, 0))
        
        # Кнопка удаления
        self.delete_btn = ctk.CTkButton(
            buttons_frame,
            text="Удалить",
            fg_color="#e74c3c",
            hover_color="#c0392b",
            command=self.delete_task
        )
        self.delete_btn.pack(side="left", padx=(0, 10))
        self.update_delete_button_state()
        
        # Кнопка отмены
        cancel_btn = ctk.CTkButton(
            buttons_frame,
            text="Отмена",
            fg_color="#6c757d",
            hover_color="#5a6268",
            command=self.destroy
        )
        cancel_btn.pack(side="left", padx=(0, 10))
        
        # Кнопка применения
        apply_btn = ctk.CTkButton(
            buttons_frame,
            text="Применить",
            fg_color="#28a745",
            hover_color="#218838",
            command=self.apply_changes
        )
        apply_btn.pack(side="right")
        
        self.status_entry.bind("<KeyRelease>", lambda e: self.update_delete_button_state())
    
    def update_delete_button_state(self):
        current_status = self.status_entry.get().strip()
        is_deletable = current_status.lower() in [s.lower() for s in self.deletable_statuses]
        self.delete_btn.configure(state="normal" if is_deletable else "disabled")
    
    def delete_task(self):
        confirm = messagebox.askyesno("Подтверждение", "Вы уверены, что хотите удалить задачу?", parent=self)
        if confirm:
            try:
                conn = sqlite3.connect('tasks.db')
                cursor = conn.cursor()
                cursor.execute("DELETE FROM tasks WHERE id = ?", (self.task_id,))
                conn.commit()
                conn.close()
                
                if self.task_type == "my":
                    self.app_instance.load_my_tasks()
                    self.app_instance.populate_my_tasks()
                messagebox.showinfo("Успех", "Задача удалена")
                self.destroy()
            except sqlite3.Error as e:
                messagebox.showerror("Ошибка", f"Не удалось удалить задачу: {e}")
    
    def is_valid_status(self, status: str) -> bool:
        return status.lower() in [s.lower() for s in self.valid_statuses]
    
    def get_correct_status_case(self, status: str) -> str:
        for valid_status in self.valid_statuses:
            if status.lower() == valid_status.lower():
                return valid_status
        return status
    
    def apply_changes(self):
        new_status = self.status_entry.get().strip()
        new_comment = self.comment_entry.get()
        
        if not self.is_valid_status(new_status):
            messagebox.showerror("Ошибка", f"Недопустимый статус! Допустимые: {', '.join(self.valid_statuses)}")
            return
        
        corrected_status = self.get_correct_status_case(new_status)
        
        try:
            conn = sqlite3.connect('tasks.db')
            cursor = conn.cursor()
            cursor.execute('''
            UPDATE tasks
            SET status = ?, comment = ?
            WHERE id = ?
            ''', (corrected_status, new_comment, self.task_id))
            conn.commit()
            conn.close()
            
            if self.task_type == "my":
                self.app_instance.load_my_tasks()
                self.app_instance.populate_my_tasks()
            messagebox.showinfo("Успех", "Изменения сохранены")
            self.update_delete_button_state()
        except sqlite3.Error as e:
            messagebox.showerror("Ошибка", f"Ошибка сохранения: {e}")

class AssignedTaskInfoWindow(TaskInfoWindow):
    """Окно информации о задаче для раздела 'Выставленные задачи'"""
    def __init__(self, parent, task_id: int, task_type: str, app_instance):
        super().__init__(parent, task_id, task_type, app_instance)
        self.title("Редактирование задачи")
        self.geometry("550x350")
        self.configure(fg_color="#d5f5e3")
        
        self.task_data = self.load_task_data()
        if not self.task_data:
            messagebox.showerror("Ошибка", "Не удалось загрузить данные задачи")
            self.destroy()
            return
        
        # Разбираем срок выполнения на дату и время
        deadline_parts = self.task_data[3].split()
        if len(deadline_parts) == 2:
            self.initial_date, self.initial_time = deadline_parts
        else:
            self.initial_date = deadline_parts[0]
            self.initial_time = ""
        
        # Загружаем список пользователей с их отделами
        self.users = self.load_users_with_departments()
        
        main_frame = ctk.CTkFrame(self, fg_color="transparent")
        main_frame.pack(pady=15, padx=20, fill="both", expand=True)
        
        # Старый исполнитель (только для отображения)
        old_receiver_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        old_receiver_frame.pack(fill="x", pady=2)
        
        ctk.CTkLabel(old_receiver_frame, 
                    text="ФИО прошлого исполнителя:", 
                    font=("Arial", 12, "bold"),
                    width=150,
                    anchor="w").pack(side="left", padx=(0, 10))
        
        old_receiver_label = ctk.CTkLabel(old_receiver_frame, 
                                        text=self.task_data[0],
                                        font=("Arial", 12),
                                        anchor="w")
        old_receiver_label.pack(side="left", fill="x", expand=True)
        
        # Новый исполнитель (выбор из списка)
        new_receiver_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        new_receiver_frame.pack(fill="x", pady=2)
        
        ctk.CTkLabel(new_receiver_frame, 
                    text="ФИО нового исполнителя:", 
                    font=("Arial", 12, "bold"),
                    width=150,
                    anchor="w").pack(side="left", padx=(0, 10))
        
        self.receiver_var = ctk.StringVar(value=self.task_data[0])  # Устанавливаем текущего исполнителя по умолчанию
        self.receiver_combobox = ctk.CTkComboBox(
            new_receiver_frame,
            values=[user[1] for user in self.users],
            variable=self.receiver_var
        )
        self.receiver_combobox.pack(side="left", fill="x", expand=True)
        
        # Текст задачи (редактируемое поле)
        task_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        task_frame.pack(fill="x", pady=2)
        
        ctk.CTkLabel(task_frame, 
                    text="Текст задачи:", 
                    font=("Arial", 12, "bold"),
                    width=150,
                    anchor="w").pack(side="left", padx=(0, 10))
        
        self.task_entry = ctk.CTkEntry(task_frame)
        self.task_entry.insert(0, self.task_data[2])
        self.task_entry.pack(side="left", fill="x", expand=True)
        
        # Старый срок выполнения (только для отображения)
        old_deadline_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        old_deadline_frame.pack(fill="x", pady=2)
        
        ctk.CTkLabel(old_deadline_frame, 
                    text="Старый срок выполнения:", 
                    font=("Arial", 12, "bold"),
                    width=150,
                    anchor="w").pack(side="left", padx=(0, 10))
        
        old_deadline_label = ctk.CTkLabel(old_deadline_frame, 
                                        text=self.task_data[3],
                                        font=("Arial", 12),
                                        anchor="w")
        old_deadline_label.pack(side="left", fill="x", expand=True)
        
        # Новый срок выполнения
        new_deadline_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        new_deadline_frame.pack(fill="x", pady=2)
        
        ctk.CTkLabel(new_deadline_frame, 
                    text="Новый срок выполнения:", 
                    font=("Arial", 12, "bold"),
                    width=150,
                    anchor="w").pack(side="left", padx=(0, 10))
        
        self.date_var = ctk.StringVar(value=self.initial_date)
        self.time_var = ctk.StringVar(value=self.initial_time)
        
        # Дата выполнения
        self.date_entry = ctk.CTkEntry(new_deadline_frame, textvariable=self.date_var, width=120)
        self.date_entry.pack(side="left", padx=(0, 10))
        
        date_btn = ctk.CTkButton(
            new_deadline_frame, 
            text="Выбрать дату",
            width=100,
            command=self.show_calendar
        )
        date_btn.pack(side="left", padx=(0, 20))
        
        # Время выполнения
        self.time_entry = ctk.CTkEntry(new_deadline_frame, textvariable=self.time_var, width=80, placeholder_text="ЧЧ:ММ")
        self.time_entry.pack(side="left")
        
        # Кнопки
        buttons_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        buttons_frame.pack(fill="x", pady=(10, 0))
        
        # Кнопка удаления (всегда активна)
        delete_btn = ctk.CTkButton(
            buttons_frame,
            text="Удалить",
            fg_color="#e74c3c",
            hover_color="#c0392b",
            command=self.delete_task
        )
        delete_btn.pack(side="left", padx=(0, 10))
        
        # Кнопка отмены
        cancel_btn = ctk.CTkButton(
            buttons_frame,
            text="Отмена",
            fg_color="#6c757d",
            hover_color="#5a6268",
            command=self.destroy
        )
        cancel_btn.pack(side="left", padx=(0, 10))
        
        # Кнопка применения
        apply_btn = ctk.CTkButton(
            buttons_frame,
            text="Применить",
            fg_color="#28a745",
            hover_color="#218838",
            command=self.apply_changes
        )
        apply_btn.pack(side="right")
    
    def load_users_with_departments(self) -> List[Tuple[int, str, str]]:
        """Загружает список пользователей с их отделами"""
        conn = sqlite3.connect('tasks.db')
        cursor = conn.cursor()
        cursor.execute("SELECT id, full_name, position FROM users WHERE status = 'Активен'")
        users = cursor.fetchall()
        conn.close()
        return users
    
    def show_calendar(self):
        """Показывает календарь для выбора даты"""
        def set_date():
            selected_date = cal.selection_get().strftime("%d.%m.%Y")
            self.date_var.set(selected_date)
            top.destroy()
        
        top = ctk.CTkToplevel(self)
        top.title("Выберите дату")
        top.geometry("300x300")
        top.grab_set()
        
        cal = Calendar(top, selectmode="day")
        cal.pack(pady=10, padx=10, fill="both", expand=True)
        
        ctk.CTkButton(top, text="Выбрать", command=set_date).pack(pady=10)
    
    def delete_task(self):
        """Удаляет задачу из базы данных"""
        confirm = messagebox.askyesno(
            "Подтверждение удаления",
            "Вы уверены, что хотите полностью удалить эту задачу?",
            parent=self
        )
        
        if not confirm:
            return
        
        try:
            conn = sqlite3.connect('tasks.db')
            cursor = conn.cursor()
            
            cursor.execute("DELETE FROM tasks WHERE id = ?", (self.task_id,))
            conn.commit()
            conn.close()
            
            self.app_instance.load_assigned_tasks()
            self.app_instance.populate_assigned_tasks()
            
            messagebox.showinfo("Успех", "Задача успешно удалена")
            self.destroy()
        except sqlite3.Error as e:
            messagebox.showerror("Ошибка", f"Не удалось удалить задачу: {e}")
    
    def apply_changes(self):
        """Применяет изменения к задаче"""
        new_receiver_name = self.receiver_var.get()
        new_task_text = self.task_entry.get()
        new_date = self.date_var.get()
        new_time = self.time_var.get()
        
        if not new_task_text:
            messagebox.showerror("Ошибка", "Текст задачи не может быть пустым!")
            return
        
        # Проверка формата даты
        if new_date:
            try:
                datetime.datetime.strptime(new_date, "%d.%m.%Y")
            except ValueError:
                messagebox.showerror("Ошибка", "Некорректный формат даты! Используйте ДД.ММ.ГГГГ")
                return
        
        # Проверка формата времени
        if new_time:
            try:
                datetime.datetime.strptime(new_time, "%H:%M")
            except ValueError:
                messagebox.showerror("Ошибка", "Некорректный формат времени! Используйте ЧЧ:ММ")
                return
        
        # Формируем срок выполнения
        if new_date and new_time:
            deadline = f"{new_date} {new_time}"
        elif new_date:
            deadline = new_date
        elif new_time:
            deadline = f"{self.initial_date} {new_time}" if self.initial_date else new_time
        else:
            deadline = self.task_data[3]
        
        try:
            # Находим ID нового получателя
            receiver_id = None
            position = None
            for user_id, name, user_position in self.users:
                if name == new_receiver_name:
                    receiver_id = user_id
                    position = user_position
                    break
            
            if not receiver_id:
                messagebox.showerror("Ошибка", "Не удалось определить исполнителя")
                return
            
            # Обновляем задачу в базе данных
            conn = sqlite3.connect('tasks.db')
            cursor = conn.cursor()
            
            cursor.execute('''
            UPDATE tasks
            SET receiver_id = ?, task_text = ?, deadline = ?
            WHERE id = ?
            ''', (receiver_id, new_task_text, deadline, self.task_id))
            
            conn.commit()
            conn.close()
            
            # Обновляем данные в приложении
            self.app_instance.load_assigned_tasks()
            self.app_instance.populate_assigned_tasks()
            
            messagebox.showinfo("Успех", "Изменения сохранены")
            self.destroy()
        except sqlite3.Error as e:
            messagebox.showerror("Ошибка", f"Не удалось сохранить изменения: {e}")

class AddTaskWindow(ctk.CTkToplevel):
    def __init__(self, parent, app_instance):
        super().__init__()
        self.parent = parent
        self.app_instance = app_instance
        self.title("Добавить задачу")
        self.geometry("500x350")
        self.configure(fg_color="#d5f5e3")
        
        # Загружаем список пользователей из базы данных
        self.users = self.load_users()
        if not self.users:
            messagebox.showerror("Ошибка", "Не удалось загрузить список пользователей")
            self.destroy()
            return
        
        # Переменные для хранения данных
        self.employee_var = ctk.StringVar()
        self.task_text_var = ctk.StringVar()
        self.date_var = ctk.StringVar()
        self.time_var = ctk.StringVar()
        
        # Основной фрейм
        main_frame = ctk.CTkFrame(self, fg_color="transparent")
        main_frame.pack(pady=20, padx=20, fill="both", expand=True)
        
        # Выбор сотрудника
        ctk.CTkLabel(main_frame, text="Выберите сотрудника:", anchor="w").pack(fill="x", pady=(0, 5))
        self.employee_combobox = ctk.CTkComboBox(main_frame, 
                                               values=[user[1] for user in self.users],
                                               variable=self.employee_var)
        self.employee_combobox.pack(fill="x", pady=(0, 15))
        
        # Текст задачи
        ctk.CTkLabel(main_frame, text="Текст задачи:", anchor="w").pack(fill="x", pady=(0, 5))
        self.task_text_entry = ctk.CTkEntry(main_frame, textvariable=self.task_text_var)
        self.task_text_entry.pack(fill="x", pady=(0, 15))
        
        # Дата и время выполнения
        datetime_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        datetime_frame.pack(fill="x", pady=(0, 15))
        
        # Дата выполнения
        ctk.CTkLabel(datetime_frame, text="Дата выполнения:", anchor="w").grid(row=0, column=0, sticky="w")
        self.date_entry = ctk.CTkEntry(datetime_frame, textvariable=self.date_var, width=120)
        self.date_entry.grid(row=1, column=0, padx=(0, 10), sticky="w")
        
        # Кнопка выбора даты
        date_btn = ctk.CTkButton(datetime_frame, 
                                text="Выбрать дату",
                                width=100,
                                command=self.show_calendar)
        date_btn.grid(row=1, column=1, padx=(0, 20), sticky="w")
        
        # Время выполнения
        ctk.CTkLabel(datetime_frame, text="Время выполнения:", anchor="w").grid(row=0, column=2, sticky="w")
        self.time_entry = ctk.CTkEntry(datetime_frame, textvariable=self.time_var, width=80, placeholder_text="ЧЧ:ММ")
        self.time_entry.grid(row=1, column=2, sticky="w")
        
        # Кнопки действия
        buttons_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        buttons_frame.pack(fill="x", pady=(20, 0))
        
        cancel_btn = ctk.CTkButton(buttons_frame, 
                                  text="Отмена",
                                  fg_color="#e74c3c",
                                  hover_color="#c0392b",
                                  command=self.destroy)
        cancel_btn.pack(side="left", padx=(0, 10))
        
        add_btn = ctk.CTkButton(buttons_frame, 
                               text="Добавить",
                               fg_color="#28a745",
                               hover_color="#218838",
                               command=self.add_task)
        add_btn.pack(side="right")
    
    def load_users(self) -> List[Tuple[int, str]]:
        """Загружает список пользователей из базы данных"""
        conn = sqlite3.connect('tasks.db')
        cursor = conn.cursor()
        
        cursor.execute("SELECT id, full_name FROM users WHERE status = 'Активен' AND id != ?", 
                      (self.app_instance.current_user_id,))
        users = cursor.fetchall()
        conn.close()
        
        return users
    
    def show_calendar(self):
        """Показать календарь для выбора даты"""
        def set_date():
            self.date_var.set(cal.selection_get().strftime("%d.%m.%Y"))
            top.destroy()
        
        top = ctk.CTkToplevel(self)
        top.title("Выберите дату")
        top.geometry("300x300")
        top.grab_set()
        
        cal = Calendar(top, selectmode="day")
        cal.pack(pady=10, padx=10, fill="both", expand=True)
        
        ctk.CTkButton(top, text="Выбрать", command=set_date).pack(pady=10)
    
    def add_task(self):
        """Добавить задачу в базу данных"""
        employee_name = self.employee_var.get()
        task_text = self.task_text_var.get()
        date = self.date_var.get()
        time = self.time_var.get()
        
        if not all([employee_name, task_text, date, time]):
            messagebox.showerror("Ошибка", "Не все поля заполнены!")
            return
        
        try:
            # Проверка формата даты и времени
            datetime.datetime.strptime(date, "%d.%m.%Y")
            datetime.datetime.strptime(time, "%H:%M")
            
            # Получаем ID выбранного пользователя
            employee_id = None
            for user_id, name in self.users:
                if name == employee_name:
                    employee_id = user_id
                    break
            
            if not employee_id:
                messagebox.showerror("Ошибка", "Не удалось определить выбранного пользователя")
                return
            
            # Добавляем задачу в базу данных
            conn = sqlite3.connect('tasks.db')
            cursor = conn.cursor()
            
            cursor.execute('''
            INSERT INTO tasks (sender_id, receiver_id, task_text, deadline, status, comment)
            VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                self.app_instance.current_user_id,
                employee_id,
                task_text,
                f"{date} {time}",
                "Новый",
                ""
            ))
            
            conn.commit()
            conn.close()
            
            # Обновляем данные в приложении
            self.app_instance.load_assigned_tasks()
            self.app_instance.populate_assigned_tasks()
            
            messagebox.showinfo("Успех", "Задача успешно добавлена")
            self.destroy()
        except ValueError:
            messagebox.showerror("Ошибка", "Некорректный формат даты или времени!")
        except sqlite3.Error as e:
            messagebox.showerror("Ошибка", f"Не удалось добавить задачу: {e}")

class CreateFolderWindow(ctk.CTkToplevel):
    def __init__(self, parent, app_instance):
        super().__init__()
        self.parent = parent
        self.app_instance = app_instance
        self.title("Создать папку")
        self.geometry("350x160")
        self.configure(fg_color="#d5f5e3")
        
        main_frame = ctk.CTkFrame(self, fg_color="transparent")
        main_frame.pack(pady=20, padx=20, fill="both", expand=True)
        
        ctk.CTkLabel(main_frame, text="Введите название папки:").pack(pady=(0, 10))
        
        self.folder_name_entry = ctk.CTkEntry(main_frame)
        self.folder_name_entry.pack(fill="x", pady=(0, 20))
        
        buttons_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        buttons_frame.pack(fill="x")
        
        cancel_btn = ctk.CTkButton(buttons_frame, 
                                  text="Отмена",
                                  fg_color="#e74c3c",
                                  hover_color="#c0392b",
                                  command=self.destroy)
        cancel_btn.pack(side="left", padx=(0, 10))
        
        add_btn = ctk.CTkButton(buttons_frame, 
                               text="Добавить",
                               fg_color="#28a745",
                               hover_color="#218838",
                               command=self.create_folder)
        add_btn.pack(side="right")
    
    def create_folder(self):
        folder_name = self.folder_name_entry.get()
        if folder_name:
            try:
                conn = sqlite3.connect('tasks.db')
                cursor = conn.cursor()
                
                # Добавляем новый отдел в базу данных
                cursor.execute("INSERT INTO departments (name) VALUES (?)", (folder_name,))
                
                conn.commit()
                conn.close()
                
                # Обновляем данные в приложении
                self.app_instance.load_departments()
                self.app_instance.populate_activity_tree()
                
                messagebox.showinfo("Успех", f"Папка '{folder_name}' успешно создана")
                self.destroy()
            except sqlite3.IntegrityError:
                messagebox.showerror("Ошибка", "Папка с таким названием уже существует!")
            except sqlite3.Error as e:
                messagebox.showerror("Ошибка", f"Не удалось создать папку: {e}")

class CreateAccountWindow(ctk.CTkToplevel):
    def __init__(self, parent, app_instance):
        super().__init__()
        self.parent = parent
        self.app_instance = app_instance
        self.title("Создать аккаунт")
        self.geometry("500x650")
        self.configure(fg_color="#d5f5e3")
        
        # Загружаем список отделов из базы данных
        self.departments = self.load_departments()
        if not self.departments:
            messagebox.showerror("Ошибка", "Не удалось загрузить список отделов")
            self.destroy()
            return
        
        main_frame = ctk.CTkFrame(self, fg_color="transparent")
        main_frame.pack(pady=20, padx=20, fill="both", expand=True)
        
        # ФИО
        ctk.CTkLabel(main_frame, text="ФИО:").pack(anchor="w", pady=(0, 5))
        self.fio_entry = ctk.CTkEntry(main_frame)
        self.fio_entry.pack(fill="x", pady=(0, 10))
        
        # Должность/отдел (выбор папки)
        ctk.CTkLabel(main_frame, text="Должность/отдел:").pack(anchor="w", pady=(0, 5))
        self.position_combobox = ctk.CTkComboBox(main_frame, 
                                              values=self.departments)
        self.position_combobox.pack(fill="x", pady=(0, 10))
        
        # Дата рождения с календарем
        birth_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        birth_frame.pack(fill="x", pady=(0, 10))
        
        ctk.CTkLabel(birth_frame, text="Дата рождения:").grid(row=0, column=0, sticky="w")
        self.birth_entry = ctk.CTkEntry(birth_frame, width=120)
        self.birth_entry.grid(row=1, column=0, sticky="w", padx=(0, 10))
        
        birth_btn = ctk.CTkButton(birth_frame, 
                                 text="Выбрать дату",
                                 width=100,
                                 command=self.show_birth_calendar)
        birth_btn.grid(row=1, column=1, sticky="w")
        
        # Номер телефона
        ctk.CTkLabel(main_frame, text="Номер телефона:").pack(anchor="w", pady=(0, 5))
        self.phone_entry = ctk.CTkEntry(main_frame)
        self.phone_entry.pack(fill="x", pady=(0, 10))
        
        # Роль пользователя
        ctk.CTkLabel(main_frame, text="Роль пользователя:").pack(anchor="w", pady=(0, 5))
        self.role_combobox = ctk.CTkComboBox(main_frame, 
                                           values=["Пользователь", "Администратор"])
        self.role_combobox.pack(fill="x", pady=(0, 10))
        
        # Электронная почта
        ctk.CTkLabel(main_frame, text="Электронная почта:").pack(anchor="w", pady=(0, 5))
        self.email_entry = ctk.CTkEntry(main_frame)
        self.email_entry.pack(fill="x", pady=(0, 10))
        
        # Пароль
        ctk.CTkLabel(main_frame, text="Пароль:").pack(anchor="w", pady=(0, 5))
        self.password_entry = ctk.CTkEntry(main_frame, show="*")
        self.password_entry.pack(fill="x", pady=(0, 10))
        
        # Повторите пароль
        ctk.CTkLabel(main_frame, text="Повторите пароль:").pack(anchor="w", pady=(0, 5))
        self.repeat_password_entry = ctk.CTkEntry(main_frame, show="*")
        self.repeat_password_entry.pack(fill="x", pady=(0, 15))
        
        # Кнопки
        buttons_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        buttons_frame.pack(fill="x", pady=(10, 0))
        
        cancel_btn = ctk.CTkButton(buttons_frame, 
                                  text="Отмена",
                                  fg_color="#e74c3c",
                                  hover_color="#c0392b",
                                  command=self.destroy)
        cancel_btn.pack(side="left", padx=(0, 10))
        
        add_btn = ctk.CTkButton(buttons_frame, 
                               text="Добавить",
                               fg_color="#28a745",
                               hover_color="#218838",
                               command=self.create_account)
        add_btn.pack(side="right")
    
    def load_departments(self) -> List[str]:
        """Загружает список отделов из базы данных"""
        conn = sqlite3.connect('tasks.db')
        cursor = conn.cursor()
        
        cursor.execute("SELECT name FROM departments")
        departments = [row[0] for row in cursor.fetchall()]
        conn.close()
        
        return departments
    
    def show_birth_calendar(self):
        """Показать календарь для выбора даты рождения"""
        def set_date():
            self.birth_entry.delete(0, "end")
            self.birth_entry.insert(0, cal.selection_get().strftime("%d.%m.%Y"))
            top.destroy()
        
        top = ctk.CTkToplevel(self)
        top.title("Выберите дату рождения")
        top.geometry("300x300")
        top.grab_set()
        
        cal = Calendar(top, selectmode="day")
        cal.pack(pady=10, padx=10, fill="both", expand=True)
        
        ctk.CTkButton(top, text="Выбрать", command=set_date).pack(pady=10)
    
    def create_account(self):
        """Создать аккаунт в базе данных"""
        fio = self.fio_entry.get()
        position = self.position_combobox.get()
        birth_date = self.birth_entry.get()
        phone = self.phone_entry.get()
        role = self.role_combobox.get()
        email = self.email_entry.get()
        password = self.password_entry.get()
        repeat_password = self.repeat_password_entry.get()
        
        if not all([fio, position, birth_date, phone, role, email, password, repeat_password]):
            messagebox.showerror("Ошибка", "Не все поля заполнены!")
            return
        
        if password != repeat_password:
            messagebox.showerror("Ошибка", "Пароли не совпадают!")
            return
        
        try:
            # Проверка формата даты
            datetime.datetime.strptime(birth_date, "%d.%m.%Y")
            
            # Проверка номера телефона
            if not re.match(r'^\+?[0-9\s\-]+$', phone):
                messagebox.showerror("Ошибка", "Некорректный формат номера телефона!")
                return
            
            # Проверка email
            if not re.match(r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$', email):
                messagebox.showerror("Ошибка", "Некорректный формат email!")
                return
            
            # Добавляем пользователя в базу данных
            conn = sqlite3.connect('tasks.db')
            cursor = conn.cursor()
            
            cursor.execute('''
            INSERT INTO users (full_name, position, birth_date, phone, email, status, role, password)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                fio,
                position,
                birth_date,
                phone,
                email,
                "Неактивен",  # По умолчанию новый пользователь неактивен
                role,
                password
            ))
            
            conn.commit()
            conn.close()
            
            # Обновляем данные в приложении
            self.app_instance.load_departments()
            self.app_instance.populate_activity_tree()
            
            messagebox.showinfo("Успех", f"Аккаунт {fio} успешно создан")
            self.destroy()
        except ValueError:
            messagebox.showerror("Ошибка", "Некорректный формат даты рождения!")
        except sqlite3.Error as e:
            messagebox.showerror("Ошибка", f"Не удалось создать аккаунт: {e}")

class MainApplication:
    def __init__(self, auth_window, current_user_id: int):
        self.auth_window = auth_window
        self.current_user_id = current_user_id
        
        # Загружаем данные из базы данных
        self.load_departments()
        self.load_user_details()
        self.load_my_tasks()
        self.load_assigned_tasks()
        
        # Текущий статус пользователя (активен/неактивен)
        self.current_user_active = True
        
        # Создаем главное окно приложения
        self.main_app = ctk.CTk()
        self.main_app.title("Главное окно")
        self.main_app.geometry("1200x800")
        self.main_app.configure(fg_color="#d5f5e3")
        
        # Центральный фрейм для содержимого
        center_frame = ctk.CTkFrame(self.main_app, fg_color="transparent")
        center_frame.pack(expand=True, fill="both", padx=50, pady=20)
        
        # Создаем верхнюю панель с вкладками (по центру)
        self.tabs_frame = ctk.CTkFrame(center_frame, fg_color="transparent")
        self.tabs_frame.pack(pady=10, fill="x")
        
        # Фреймы для разных разделов
        self.activity_frame = ctk.CTkFrame(center_frame, fg_color="transparent")
        self.my_tasks_frame = ctk.CTkFrame(center_frame, fg_color="transparent")
        self.assigned_tasks_frame = ctk.CTkFrame(center_frame, fg_color="transparent")
        
        # Вкладки (по центру)
        self.tab_buttons = []
        for i, tab_name in enumerate(["Активность", "Мои задачи", "Выставленные задачи"]):
            tab = ctk.CTkButton(self.tabs_frame, 
                              text=tab_name,
                              fg_color="#28a745" if i == 0 else "transparent",
                              hover=False,
                              text_color="black",
                              font=("Arial", 14, "bold") if i == 0 else ("Arial", 14),
                              command=lambda name=tab_name: self.wrapped_show_tab(name))
            tab.pack(side="left", padx=5, expand=True)
            self.tab_buttons.append(tab)
        
        # ============= ОБЩИЕ ЭЛЕМЕНТЫ =============
        # Верхняя правая панель с ФИО пользователя
        user_info_frame = ctk.CTkFrame(center_frame, fg_color="transparent")
        user_info_frame.pack(anchor="ne", pady=5)
        
        # Получаем ФИО текущего пользователя
        current_user_name = self.get_current_user_name()
        
        user_name_label = ctk.CTkLabel(user_info_frame, 
                                     text=current_user_name,
                                     font=("Arial", 14, "bold"),
                                     text_color="black")
        user_name_label.pack(side="left", padx=10)
        
        # Панель поиска и иконок
        self.search_frame = ctk.CTkFrame(center_frame, fg_color="transparent")
        self.search_frame.pack(pady=10, fill="x")
        
        # Правая часть - иконки (общие для всех разделов)
        self.right_frame = ctk.CTkFrame(self.search_frame, fg_color="transparent")
        self.right_frame.pack(side="right")
        
        # Кнопка "+" (только для выставленных задач)
        self.plus_button = ctk.CTkButton(self.right_frame, 
                                       text="+",
                                       text_color="black",
                                       font=("Arial", 24),
                                       width=30,
                                       height=30,
                                       fg_color="transparent",
                                       hover_color="#c8e6c9",
                                       command=self.show_add_task_window)
        
        # Иконка меню (три точки)
        def show_menu(event=None):
            x = self.menu_button.winfo_rootx()
            y = self.menu_button.winfo_rooty() + self.menu_button.winfo_height()
            
            commands = {
                "Отметить неактивность": self.mark_inactive,
                "Создать аккаунт": self.create_account,
                "Создать папку": self.create_folder,
                "Выйти из аккаунта": self.logout
            }
            
            DropdownMenu(self.main_app, x, y, commands)
        
        self.menu_button = ctk.CTkButton(self.right_frame, 
                                       text="⋮",
                                       text_color="black",
                                       font=("Arial", 24),
                                       width=30,
                                       height=30,
                                       fg_color="transparent",
                                       hover_color="#c8e6c9",
                                       command=show_menu)
        self.menu_button.pack(side="right", padx=5)
        
        # Иконка активности (звезда/крестик)
        self.status_icon = ctk.CTkLabel(self.right_frame, 
                                      text="★", 
                                      text_color="#28a745",
                                      font=("Arial", 24))
        self.status_icon.pack(side="right", padx=10)
        
        # ============= РАЗДЕЛ "АКТИВНОСТЬ" =============
        # Левая часть - поиск (только для активности)
        self.activity_search_frame = ctk.CTkFrame(self.search_frame, fg_color="transparent")
        
        # Поле поиска для активности (самое левое)
        self.activity_search_entry = ctk.CTkEntry(self.activity_search_frame, 
                                                width=400, 
                                                placeholder_text="Поиск по ФИО",
                                                text_color="black",
                                                fg_color="white")
        
        # Фильтр активных пользователей
        self.active_users_var = ctk.BooleanVar(value=False)
        self.active_users_filter = ctk.CTkCheckBox(self.activity_search_frame, 
                                                  text="Только активные",
                                                  variable=self.active_users_var,
                                                  text_color="black",
                                                  command=lambda: self.filter_active_users())
        
        # Таблица Treeview для активности
        self.activity_tree_frame = ctk.CTkFrame(self.activity_frame, fg_color="transparent")
        self.activity_tree_frame.pack(fill="both", expand=True, pady=10)
        
        self.activity_style = ttk.Style()
        self.activity_style.configure("Activity.Treeview", 
                                    background="white",
                                    foreground="black",
                                    fieldbackground="white",
                                    font=("Arial", 12))
        self.activity_style.configure("Activity.Treeview.Heading", 
                                    font=("Arial", 12, "bold"))
        self.activity_style.map("Activity.Treeview", background=[("selected", "#28a745")])
        
        # Создаем Treeview с двумя столбцами (второй для статуса активности)
        self.activity_tree = ttk.Treeview(self.activity_tree_frame, 
                                        columns=("status",), 
                                        show="tree headings", 
                                        selectmode="browse", 
                                        style="Activity.Treeview")
        self.activity_tree.heading("#0", text="ФИО", anchor="w")
        self.activity_tree.heading("status", text="Статус", anchor="w")
        self.activity_tree.column("status", width=80, stretch=False)
        
        # Привязываем обработчик двойного клика
        self.activity_tree.bind("<Double-1>", self.show_user_info)
        
        # Изначально заполняем дерево
        self.populate_activity_tree()
        
        self.activity_tree.pack(fill="both", expand=True)
        
        # ============= РАЗДЕЛ "МОИ ЗАДАЧИ" =============
        # Левая часть - поиск для задач
        self.tasks_search_frame = ctk.CTkFrame(self.search_frame, fg_color="transparent")
        
        self.tasks_search_label = ctk.CTkLabel(self.tasks_search_frame, text="Поиск по:", text_color="black")
        self.tasks_search_by_var = ctk.StringVar(value="ФИО отправителя")
        self.tasks_search_by = ctk.CTkComboBox(self.tasks_search_frame, 
                                              values=["ФИО отправителя", "Должность/отдел", "Текст задачи", "Срок выполнения", "Статус задачи", "Комментарий"],
                                              variable=self.tasks_search_by_var,
                                              width=150)
        
        self.tasks_search_entry = ctk.CTkEntry(self.tasks_search_frame, 
                                             width=400, 
                                             placeholder_text="Введите текст для поиска",
                                             text_color="black",
                                             fg_color="white")
        
        # Таблица для задач
        self.tasks_tree_frame = ctk.CTkFrame(self.my_tasks_frame, fg_color="transparent")
        self.tasks_tree_frame.pack(fill="both", expand=True, pady=10)
        
        self.tasks_style = ttk.Style()
        self.tasks_style.configure("Tasks.Treeview", 
                                 background="white",
                                 foreground="black",
                                 fieldbackground="white",
                                 font=("Arial", 12))
        self.tasks_style.configure("Tasks.Treeview.Heading", 
                                 font=("Arial", 12, "bold"))
        self.tasks_style.map("Tasks.Treeview", background=[("selected", "#28a745")])
        
        self.tasks_tree = ttk.Treeview(self.tasks_tree_frame, 
                                     columns=("sender", "position", "task", "deadline", "status", "comment"),
                                     show="headings",
                                     style="Tasks.Treeview")
        
        # Настройка столбцов
        self.tasks_tree.heading("sender", text="ФИО отправителя")
        self.tasks_tree.heading("position", text="Должность/отдел")
        self.tasks_tree.heading("task", text="Текст задачи")
        self.tasks_tree.heading("deadline", text="Срок выполнения")
        self.tasks_tree.heading("status", text="Статус задачи")
        self.tasks_tree.heading("comment", text="Комментарий")
        
        # Установка ширины столбцов
        self.tasks_tree.column("sender", width=150)
        self.tasks_tree.column("position", width=150)
        self.tasks_tree.column("task", width=250)
        self.tasks_tree.column("deadline", width=120)
        self.tasks_tree.column("status", width=120)
        self.tasks_tree.column("comment", width=200)
        
        # Привязываем обработчик двойного клика
        self.tasks_tree.bind("<Double-1>", self.show_task_info)
        
        # Изначально заполняем таблицу
        self.populate_my_tasks()
        
        self.tasks_tree.pack(fill="both", expand=True)
        
        # ============= РАЗДЕЛ "ВЫСТАВЛЕННЫЕ ЗАДАЧИ" =============
        # Левая часть - поиск для выставленных задач
        self.assigned_search_frame = ctk.CTkFrame(self.search_frame, fg_color="transparent")
        
        self.assigned_search_label = ctk.CTkLabel(self.assigned_search_frame, text="Поиск по:", text_color="black")
        self.assigned_search_by_var = ctk.StringVar(value="ФИО исполнителя")
        self.assigned_search_by = ctk.CTkComboBox(self.assigned_search_frame, 
                                                values=["ФИО исполнителя", "Должность/отдел", "Текст задачи", "Срок выполнения", "Статус задачи", "Комментарий"],
                                                variable=self.assigned_search_by_var,
                                                width=150)
        
        self.assigned_search_entry = ctk.CTkEntry(self.assigned_search_frame, 
                                                width=400, 
                                                placeholder_text="Введите текст для поиска",
                                                text_color="black",
                                                fg_color="white")
        
        # Таблица для выставленных задач
        self.assigned_tree_frame = ctk.CTkFrame(self.assigned_tasks_frame, fg_color="transparent")
        self.assigned_tree_frame.pack(fill="both", expand=True, pady=10)
        
        self.assigned_style = ttk.Style()
        self.assigned_style.configure("Assigned.Treeview", 
                                   background="white",
                                   foreground="black",
                                   fieldbackground="white",
                                   font=("Arial", 12))
        self.assigned_style.configure("Assigned.Treeview.Heading", 
                                   font=("Arial", 12, "bold"))
        self.assigned_style.map("Assigned.Treeview", background=[("selected", "#28a745")])
        
        self.assigned_tree = ttk.Treeview(self.assigned_tree_frame, 
                                        columns=("receiver", "position", "task", "deadline", "status", "comment"),
                                        show="headings",
                                        style="Assigned.Treeview")
        
        # Настройка столбцов
        self.assigned_tree.heading("receiver", text="ФИО исполнителя")
        self.assigned_tree.heading("position", text="Должность/отдел")
        self.assigned_tree.heading("task", text="Текст задачи")
        self.assigned_tree.heading("deadline", text="Срок выполнения")
        self.assigned_tree.heading("status", text="Статус задачи")
        self.assigned_tree.heading("comment", text="Комментарий")
        
        # Установка ширины столбцов
        self.assigned_tree.column("receiver", width=150)
        self.assigned_tree.column("position", width=150)
        self.assigned_tree.column("task", width=250)
        self.assigned_tree.column("deadline", width=120)
        self.assigned_tree.column("status", width=120)
        self.assigned_tree.column("comment", width=200)
        
        # Привязываем обработчик двойного клика
        self.assigned_tree.bind("<Double-1>", self.show_task_info)
        
        # Изначально заполняем таблицу
        self.populate_assigned_tasks()
        
        self.assigned_tree.pack(fill="both", expand=True)
        
        # Показываем активность по умолчанию
        self.update_ui("Активность")
        self.wrapped_show_tab("Активность")
        
        # Запускаем главное окно
        self.main_app.mainloop()
    
    def get_current_user_name(self) -> str:
        """Возвращает ФИО текущего пользователя"""
        conn = sqlite3.connect('tasks.db')
        cursor = conn.cursor()
        
        cursor.execute("SELECT full_name FROM users WHERE id = ?", (self.current_user_id,))
        result = cursor.fetchone()
        conn.close()
        
        return result[0] if result else "Неизвестный пользователь"
    
    def load_departments(self):
        """Загружает отделы из базы данных"""
        conn = sqlite3.connect('tasks.db')
        cursor = conn.cursor()
        
        cursor.execute("SELECT name FROM departments")
        self.departments = [row[0] for row in cursor.fetchall()]
        
        conn.close()
    
    def load_user_details(self):
        """Загружает детали пользователей из базы данных"""
        conn = sqlite3.connect('tasks.db')
        cursor = conn.cursor()
        
        cursor.execute('''
        SELECT 
            u.full_name, 
            u.position, 
            u.birth_date, 
            u.phone, 
            u.email, 
            u.status
        FROM users u
        ''')
        
        self.user_details = {}
        for row in cursor.fetchall():
            self.user_details[row[0]] = {
                "position": row[1],
                "birth_date": row[2],
                "phone": row[3],
                "email": row[4],
                "status": row[5]
            }
        
        conn.close()
    
    def load_my_tasks(self):
        """Загружает задачи текущего пользователя из базы данных"""
        conn = sqlite3.connect('tasks.db')
        cursor = conn.cursor()
        
        cursor.execute('''
        SELECT 
            s.full_name, 
            s.position, 
            t.task_text, 
            t.deadline, 
            t.status, 
            t.comment,
            t.id
        FROM tasks t
        JOIN users s ON t.sender_id = s.id
        WHERE t.receiver_id = ?
        ''', (self.current_user_id,))
        
        self.my_tasks_data = cursor.fetchall()
        conn.close()
    
    def load_assigned_tasks(self):
        """Загружает задачи, созданные текущим пользователем, из базы данных"""
        conn = sqlite3.connect('tasks.db')
        cursor = conn.cursor()
        
        cursor.execute('''
        SELECT 
            r.full_name,
            r.position, 
            t.task_text, 
            t.deadline, 
            t.status, 
            t.comment,
            t.id
        FROM tasks t
        JOIN users r ON t.receiver_id = r.id
        WHERE t.sender_id = ?
        ''', (self.current_user_id,))
        
        self.assigned_tasks_data = cursor.fetchall()
        conn.close()
    
    def show_user_info(self, event):
        """Показывает информацию о пользователе при двойном клике"""
        item = self.activity_tree.selection()[0]
        item_text = self.activity_tree.item(item, "text")
        
        # Проверяем, кликнули ли по пользователю (а не по папке)
        if "★" in item_text or "✗" in item_text:
            # Удаляем символы активности/неактивности
            user_name = item_text.replace("★ ", "").replace("✗ ", "")
            
            # Получаем информацию о пользователе
            if user_name in self.user_details:
                user_info = self.user_details[user_name]
                
                # Создаем список для передачи в окно информации
                info_list = [
                    user_name,
                    user_info["position"],
                    user_info["birth_date"],
                    user_info["phone"],
                    user_info["email"]
                ]
                
                # Показываем окно с информацией
                UserInfoWindow(self.main_app, info_list)
            else:
                messagebox.showwarning("Информация", "Дополнительная информация о пользователе отсутствует")
    
    def show_task_info(self, event):
        tree = event.widget
        selection = tree.selection()
    
        if not selection:  # Проверяем, что есть выбранный элемент
            return
    
        item = selection[0]
        item_values = tree.item(item, "values")
    
        if not item_values or len(item_values) < 7:  # Проверяем, что у элемента есть значения и их достаточно
            return
    
        task_id = item_values[6]  # ID задачи находится в 7-м столбце (индекс 6)
    
        if tree == self.tasks_tree:  # Мои задачи
            MyTaskInfoWindow(self.main_app, task_id, "my", self)
        else:  # Выставленные задачи
            AssignedTaskInfoWindow(self.main_app, task_id, "assigned", self)
    
    def populate_activity_tree(self, show_all=True, query=None):
        """Заполняет дерево активностей с учетом фильтра и поиска"""
        self.activity_tree.delete(*self.activity_tree.get_children())
        
        conn = sqlite3.connect('tasks.db')
        cursor = conn.cursor()
        
        # Получаем всех пользователей сгруппированных по отделам
        cursor.execute('''
        SELECT 
            d.name as department,
            u.full_name,
            u.status
        FROM users u
        JOIN departments d ON u.position = d.name
        ORDER BY d.name, u.full_name
        ''')
        
        users_by_department = {}
        for row in cursor.fetchall():
            department, full_name, status = row
            if department not in users_by_department:
                users_by_department[department] = []
            
            # Добавляем символ активности/неактивности
            prefix = "★ " if status == "Активен" else "✗ "
            users_by_department[department].append((prefix + full_name, status))
        
        conn.close()
        
        for department, users in users_by_department.items():
            # Проверяем, есть ли в этом отделе подходящие пользователи
            matching_users = []
            has_active_users = False
            
            for user, status in users:
                user_name = user.replace("★ ", "").replace("✗ ", "")
                if (show_all or "★" in user) and (query is None or query.lower() in user_name.lower()):
                    matching_users.append((user, status))
                    if "★" in user:
                        has_active_users = True
            
            # Если фильтр "Только активные" включен и в отделе нет активных пользователей - пропускаем
            if not show_all and not has_active_users:
                continue
            
            # Если есть подходящие пользователи или запрос пустой, показываем отдел
            if matching_users or query is None or query == "":
                department_id = self.activity_tree.insert("", "end", text=department, values=("",))
                for user, status in matching_users:
                    # Вставляем пользователя с тегом для цвета символа
                    if "★" in user:
                        self.activity_tree.insert(department_id, "end", text=user, values=(status,), tags=("active",))
                    else:
                        self.activity_tree.insert(department_id, "end", text=user, values=(status,), tags=("inactive",))
                # Раскрываем все папки автоматически
                self.activity_tree.item(department_id, open=True)
        
        # Настраиваем теги для цветов символов
        self.activity_tree.tag_configure("active", foreground="#28a745")  # Зеленый цвет для активных
        self.activity_tree.tag_configure("inactive", foreground="#FF0000")  # Красный цвет для неактивных
    
    def filter_active_users(self):
        """Фильтрует пользователей по активности"""
        query = self.activity_search_entry.get().strip()
        show_all = not self.active_users_var.get()
        self.populate_activity_tree(show_all, query if query != "" else None)
    
    def search_activity_fio(self, event=None):
        """Поиск по ФИО в активности"""
        query = self.activity_search_entry.get().strip()
        show_all = not self.active_users_var.get()
        self.populate_activity_tree(show_all, query if query != "" else None)
    
    def populate_my_tasks(self):
        """Заполняет таблицу моих задач с учетом поиска"""
        self.tasks_tree.delete(*self.tasks_tree.get_children())
        
        query = self.tasks_search_entry.get().strip()
        search_by = self.tasks_search_by_var.get()
        
        # Создаем словарь для соответствия названий столбцов индексам
        column_mapping = {
            "ФИО отправителя": 0,
            "Должность/отдел": 1,
            "Текст задачи": 2,
            "Срок выполнения": 3,
            "Статус задачи": 4,
            "Комментарий": 5
        }
        
        col_index = column_mapping[search_by]
        
        for task in self.my_tasks_data:
            if query == "" or query.lower() in str(task[col_index]).lower():
                self.tasks_tree.insert("", "end", values=task)
    
    def populate_assigned_tasks(self):
        """Заполняет таблицу выставленных задач с учетом поиска"""
        self.assigned_tree.delete(*self.assigned_tree.get_children())
        
        query = self.assigned_search_entry.get().strip()
        search_by = self.assigned_search_by_var.get()
        
        # Создаем словарь для соответствия названий столбцов индексам
        column_mapping = {
            "ФИО исполнителя": 0,
            "Должность/отдел": 1,
            "Текст задачи": 2,
            "Срок выполнения": 3,
            "Статус задачи": 4,
            "Комментарий": 5
        }
        
        col_index = column_mapping[search_by]
        
        for task in self.assigned_tasks_data:
            if query == "" or query.lower() in str(task[col_index]).lower():
                self.assigned_tree.insert("", "end", values=task)
    
    def update_ui(self, tab_name):
        """Обновляет элементы интерфейса при смене раздела"""
        # Скрываем все поисковые фреймы
        self.activity_search_frame.pack_forget()
        self.tasks_search_frame.pack_forget()
        self.assigned_search_frame.pack_forget()
        
        # Очищаем левые фреймы
        for widget in self.activity_search_frame.winfo_children():
            widget.pack_forget()
        for widget in self.tasks_search_frame.winfo_children():
            widget.pack_forget()
        for widget in self.assigned_search_frame.winfo_children():
            widget.pack_forget()
        
        # Скрываем/показываем кнопку "+"
        self.plus_button.pack_forget()
        if tab_name == "Выставленные задачи":
            self.plus_button.pack(side="right", padx=10)
        
        # Показываем нужный поисковый фрейм
        if tab_name == "Активность":
            self.activity_search_entry.pack(side="left", padx=5)
            self.active_users_filter.pack(side="left", padx=5)
            self.activity_search_frame.pack(side="left", fill="x", expand=True)
            
            # Привязываем обработчики событий
            self.activity_search_entry.bind("<KeyRelease>", lambda e: self.search_activity_fio())
        elif tab_name == "Мои задачи":
            self.tasks_search_label.pack(side="left", padx=5)
            self.tasks_search_by.pack(side="left", padx=5)
            self.tasks_search_entry.pack(side="left", padx=5)
            self.tasks_search_frame.pack(side="left", fill="x", expand=True)
            
            # Привязываем обработчики событий
            self.tasks_search_entry.bind("<KeyRelease>", lambda e: self.populate_my_tasks())
            self.tasks_search_by_var.trace_add("write", lambda *args: self.populate_my_tasks())
        elif tab_name == "Выставленные задачи":
            self.assigned_search_label.pack(side="left", padx=5)
            self.assigned_search_by.pack(side="left", padx=5)
            self.assigned_search_entry.pack(side="left", padx=5)
            self.assigned_search_frame.pack(side="left", fill="x", expand=True)
            
            # Привязываем обработчики событий
            self.assigned_search_entry.bind("<KeyRelease>", lambda e: self.populate_assigned_tasks())
            self.assigned_search_by_var.trace_add("write", lambda *args: self.populate_assigned_tasks())
    
    def wrapped_show_tab(self, tab_name):
        """Обертка для функции show_tab с обновлением UI"""
        if tab_name == "Активность":
            self.activity_frame.pack(fill="both", expand=True)
            self.my_tasks_frame.pack_forget()
            self.assigned_tasks_frame.pack_forget()
            
            for btn in self.tab_buttons:
                btn.configure(fg_color="transparent", font=("Arial", 14))
            self.tab_buttons[0].configure(fg_color="#28a745", font=("Arial", 14, "bold"))
        elif tab_name == "Мои задачи":
            self.activity_frame.pack_forget()
            self.my_tasks_frame.pack(fill="both", expand=True)
            self.assigned_tasks_frame.pack_forget()
            
            for btn in self.tab_buttons:
                btn.configure(fg_color="transparent", font=("Arial", 14))
            self.tab_buttons[1].configure(fg_color="#28a745", font=("Arial", 14, "bold"))
        elif tab_name == "Выставленные задачи":
            self.activity_frame.pack_forget()
            self.my_tasks_frame.pack_forget()
            self.assigned_tasks_frame.pack(fill="both", expand=True)
            
            for btn in self.tab_buttons:
                btn.configure(fg_color="transparent", font=("Arial", 14))
            self.tab_buttons[2].configure(fg_color="#28a745", font=("Arial", 14, "bold"))
        
        self.update_ui(tab_name)
    
    def mark_inactive(self):
        """Переключает статус активности текущего пользователя"""
        try:
            conn = sqlite3.connect('tasks.db')
            cursor = conn.cursor()
            
            if self.current_user_active:
                # Меняем на неактивность
                cursor.execute("UPDATE users SET status = 'Неактивен' WHERE id = ?", (self.current_user_id,))
                self.status_icon.configure(text="✗", text_color="#FF0000")
                self.current_user_active = False
            else:
                # Возвращаем активность
                cursor.execute("UPDATE users SET status = 'Активен' WHERE id = ?", (self.current_user_id,))
                self.status_icon.configure(text="★", text_color="#28a745")
                self.current_user_active = True
            
            conn.commit()
            conn.close()
            
            # Обновляем данные в приложении
            self.load_user_details()
            self.populate_activity_tree()
        except sqlite3.Error as e:
            messagebox.showerror("Ошибка", f"Не удалось изменить статус: {e}")
    
    def create_account(self):
        CreateAccountWindow(self.main_app, self)
    
    def create_folder(self):
        CreateFolderWindow(self.main_app, self)
    
    def logout(self):
        self.main_app.destroy()
        self.auth_window.deiconify()
    
    def show_add_task_window(self):
        AddTaskWindow(self.main_app, self)

def create_auth_window():
    # Создаем окно авторизации
    ctk.set_appearance_mode("light")
    ctk.set_default_color_theme("green")

    auth_window = ctk.CTk()
    auth_window.title("Авторизация")
    auth_window.geometry("400x300")
    auth_window.configure(fg_color="#d5f5e3")

    # Элементы авторизации
    label = ctk.CTkLabel(auth_window, 
                        text="АВТОРИЗАЦИЯ", 
                        font=("Arial", 20, "bold"),
                        text_color="black")
    label.pack(pady=20)

    login_label = ctk.CTkLabel(auth_window, 
                              text="Введите логин:",
                              text_color="black")
    login_label.pack()

    login_entry = ctk.CTkEntry(auth_window, 
                              width=250,
                              text_color="black",
                              fg_color="white")
    login_entry.pack(pady=5)

    password_label = ctk.CTkLabel(auth_window, 
                                 text="Введите пароль:",
                                 text_color="black")
    password_label.pack()

    password_entry = ctk.CTkEntry(auth_window, 
                                 width=250, 
                                 show="*",
                                 text_color="black",
                                 fg_color="white")
    password_entry.pack(pady=5)

    def authenticate():
        """Условная аутентификация - сразу входит под Выгузовой Владой Михайловной"""
        try:
            conn = sqlite3.connect('tasks.db')
            cursor = conn.cursor()
            
            # Получаем ID пользователя "Выгузова Влада Михайловна"
            cursor.execute("SELECT id FROM users WHERE full_name = 'Выгузова Влада Михайловна'")
            result = cursor.fetchone()
            conn.close()
            
            if result:
                user_id = result[0]
                show_main_window(auth_window, user_id)
            else:
                messagebox.showerror("Ошибка", "Тестовый пользователь не найден в базе данных")
        except sqlite3.Error as e:
            messagebox.showerror("Ошибка", f"Ошибка при аутентификации: {e}")

    continue_button = ctk.CTkButton(
        auth_window, 
        text="Продолжить", 
        command=authenticate,  # При нажатии сразу авторизуемся
        fg_color="#28a745",
        hover_color="#218838",
        text_color="white",
        font=("Arial", 14)
    )
    continue_button.pack(pady=20)

    # Опционально: можно сразу заполнить поля для демонстрации
    login_entry.insert(0, "vyguzova@example.com")
    password_entry.insert(0, "admin")

    return auth_window

def show_main_window(auth_window, current_user_id: int):
    # Скрываем окно авторизации
    auth_window.withdraw()
    
    # Создаем и запускаем главное приложение
    app = MainApplication(auth_window, current_user_id)

# Создаем и запускаем окно авторизации
auth_window = create_auth_window()
auth_window.mainloop()
