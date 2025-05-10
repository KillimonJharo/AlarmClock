import tkinter as tk
from tkinter import messagebox, filedialog, ttk
import time
import winsound
from datetime import datetime
import threading
import re
import os
import json


class AlarmClock:
    def __init__(self, root):
        self.root = root
        self.root.title("Продвинутый будильник")
        self.root.geometry("500x550")

        # Загрузка сохраненных настроек
        self.settings_file = "alarm_settings.json"
        self.settings = self.load_settings()

        # Переменные
        self.alarm_time = tk.StringVar(value=self.settings.get("alarm_time", ""))
        self.alarm_sound = tk.StringVar(value=self.settings.get("alarm_sound", "стандартный"))
        self.custom_sound_path = tk.StringVar(value=self.settings.get("custom_sound_path", ""))
        self.alarm_message = tk.StringVar(value=self.settings.get("alarm_message", "Пора вставать!"))
        self.alarm_active = False
        self.days_vars = {
            "Пн": tk.BooleanVar(value=self.settings.get("days", {}).get("Пн", False)),
            "Вт": tk.BooleanVar(value=self.settings.get("days", {}).get("Вт", False)),
            "Ср": tk.BooleanVar(value=self.settings.get("days", {}).get("Ср", False)),
            "Чт": tk.BooleanVar(value=self.settings.get("days", {}).get("Чт", False)),
            "Пт": tk.BooleanVar(value=self.settings.get("days", {}).get("Пт", False)),
            "Сб": tk.BooleanVar(value=self.settings.get("days", {}).get("Сб", False)),
            "Вс": tk.BooleanVar(value=self.settings.get("days", {}).get("Вс", False))
        }

        # Создание интерфейса
        self.create_widgets()

    def create_widgets(self):
        # Вкладки
        tab_control = ttk.Notebook(self.root)

        # Основная вкладка
        main_tab = ttk.Frame(tab_control)
        tab_control.add(main_tab, text="Основные настройки")

        # Вкладка дней недели
        days_tab = ttk.Frame(tab_control)
        tab_control.add(days_tab, text="Дни недели")

        tab_control.pack(expand=1, fill="both")

        # Основные настройки (вкладка 1)
        tk.Label(main_tab, text="Установите время будильника (ЧЧММ или ЧЧ:ММ):").pack(pady=5)

        vcmd = (self.root.register(self.validate_time_input), '%P')
        self.time_entry = tk.Entry(main_tab, textvariable=self.alarm_time,
                                   font=('Arial', 14), validate='key', validatecommand=vcmd)
        self.time_entry.pack()
        tk.Label(main_tab, text="Пример: 730 или 07:30").pack()

        # Выбор звука
        tk.Label(main_tab, text="Выберите звук будильника:").pack(pady=5)

        sound_frame = tk.Frame(main_tab)
        sound_frame.pack()

        sound_options = ["стандартный", "мелодия", "свой звук"]
        for i, option in enumerate(sound_options):
            tk.Radiobutton(sound_frame, text=option, variable=self.alarm_sound,
                           value=option, command=self.update_sound_options).grid(row=0, column=i, padx=5)

        # Кнопка выбора файла
        self.sound_file_btn = tk.Button(main_tab, text="Выбрать файл",
                                        command=self.choose_sound_file, state='disabled')
        self.sound_file_btn.pack(pady=5)

        if self.alarm_sound.get() == "свой звук" and self.custom_sound_path.get():
            self.sound_file_btn.config(state='normal')
            tk.Label(main_tab, text=f"Выбран: {os.path.basename(self.custom_sound_path.get())}").pack()

        # Поле для сообщения
        tk.Label(main_tab, text="Сообщение будильника:").pack(pady=5)
        tk.Entry(main_tab, textvariable=self.alarm_message, font=('Arial', 12)).pack()

        # Кнопки управления
        btn_frame = tk.Frame(main_tab)
        btn_frame.pack(pady=10)

        tk.Button(btn_frame, text="Установить будильник", command=self.set_alarm).pack(side='left', padx=5)
        tk.Button(btn_frame, text="Выключить будильник", command=self.stop_alarm).pack(side='left', padx=5)

        # Текущее время
        self.time_label = tk.Label(main_tab, text="", font=('Arial', 16))
        self.time_label.pack(pady=10)

        # Дни недели (вкладка 2)
        tk.Label(days_tab, text="Выберите дни срабатывания будильника:").pack(pady=10)

        days_frame = tk.Frame(days_tab)
        days_frame.pack()

        for i, (day, var) in enumerate(self.days_vars.items()):
            tk.Checkbutton(days_frame, text=day, variable=var).grid(row=i // 4, column=i % 4, padx=10, pady=5,
                                                                    sticky='w')

        # Обновление времени
        self.update_time()

    def update_sound_options(self):
        if self.alarm_sound.get() == "свой звук":
            self.sound_file_btn.config(state='normal')
        else:
            self.sound_file_btn.config(state='disabled')

    def choose_sound_file(self):
        file_path = filedialog.askopenfilename(
            title="Выберите звуковой файл",
            filetypes=(("WAV файлы", "*.wav"), ("MP3 файлы", "*.mp3"), ("Все файлы", "*.*"))
        )
        if file_path:
            self.custom_sound_path.set(file_path)

    def validate_time_input(self, new_text):
        if not new_text:
            return True

        if re.fullmatch(r'^(\d{0,2}:?\d{0,2})$', new_text):
            if len(new_text) == 2 and ':' not in new_text:
                self.alarm_time.set(new_text + ':')
                self.time_entry.icursor(3)
            return True
        return False

    def format_time_input(self, time_str):
        digits = re.sub(r'[^\d]', '', time_str)

        if len(digits) < 4:
            digits = digits.zfill(4)

        return f"{digits[:2]}:{digits[2:4]}"

    def update_time(self):
        current_time = time.strftime("%H:%M:%S")
        current_weekday = ["Пн", "Вт", "Ср", "Чт", "Пт", "Сб", "Вс"][datetime.today().weekday()]
        self.time_label.config(text=f"Текущее время: {current_time}\nТекущий день: {current_weekday}")

        if self.alarm_active:
            try:
                alarm_time = self.format_time_input(self.alarm_time.get())
                current_time_no_sec = time.strftime("%H:%M")

                # Проверяем день недели (если выбраны дни)
                selected_days = [day for day, var in self.days_vars.items() if var.get()]
                day_check = (not selected_days) or (current_weekday in selected_days)

                if current_time_no_sec == alarm_time and day_check:
                    self.trigger_alarm()
            except:
                pass

        self.root.after(1000, self.update_time)

    def set_alarm(self):
        try:
            time_str = self.format_time_input(self.alarm_time.get())
            datetime.strptime(time_str, "%H:%M")
            self.alarm_active = True
            self.save_settings()
            messagebox.showinfo("Будильник", f"Будильник установлен на {time_str}")
        except ValueError:
            messagebox.showerror("Ошибка", "Пожалуйста, введите корректное время (ЧЧММ или ЧЧ:ММ)")

    def stop_alarm(self):
        self.alarm_active = False
        messagebox.showinfo("Будильник", "Будильник выключен")

    def trigger_alarm(self):
        self.alarm_active = False
        sound_thread = threading.Thread(target=self.play_sound)
        sound_thread.daemon = True
        sound_thread.start()

        messagebox.showinfo("Будильник", self.alarm_message.get())

    def play_sound(self):
        sound_type = self.alarm_sound.get()

        if sound_type == "стандартный":
            for _ in range(5):
                winsound.Beep(1000, 500)
                time.sleep(0.5)
        elif sound_type == "мелодия":
            tones = [659, 659, 659, 523, 659, 784, 392]
            for tone in tones:
                winsound.Beep(tone, 500)
        elif sound_type == "свой звук" and self.custom_sound_path.get():
            try:
                # Для WAV файлов
                if self.custom_sound_path.get().lower().endswith('.wav'):
                    winsound.PlaySound(self.custom_sound_path.get(), winsound.SND_FILENAME)
                # Для MP3 и других форматов потребуется дополнительная библиотека
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось воспроизвести файл: {e}")

    def save_settings(self):
        settings = {
            "alarm_time": self.alarm_time.get(),
            "alarm_sound": self.alarm_sound.get(),
            "custom_sound_path": self.custom_sound_path.get(),
            "alarm_message": self.alarm_message.get(),
            "days": {day: var.get() for day, var in self.days_vars.items()}
        }

        try:
            with open(self.settings_file, 'w') as f:
                json.dump(settings, f)
        except Exception as e:
            print(f"Ошибка сохранения настроек: {e}")

    def load_settings(self):
        if os.path.exists(self.settings_file):
            try:
                with open(self.settings_file, 'r') as f:
                    return json.load(f)
            except:
                pass
        return {}


if __name__ == "__main__":
    root = tk.Tk()
    app = AlarmClock(root)
    root.mainloop()