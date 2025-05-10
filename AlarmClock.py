import tkinter as tk
from tkinter import messagebox, filedialog, ttk
import time
import winsound
from datetime import datetime, timedelta
import threading
import re
import os
import json


class AlarmClock:
    def __init__(self, root):
        self.root = root
        self.root.title("Продвинутый будильник")
        self.root.geometry("700x750")

        # Загрузка сохраненных настроек
        self.settings_file = "alarm_settings.json"
        self.settings = self.load_settings()

        # Переменные
        self.alarms = self.settings.get("alarms", [])
        self.alarm_time = tk.StringVar(value="")
        self.alarm_sound = tk.StringVar(value=self.settings.get("default_sound", "стандартный"))
        self.custom_sound_path = tk.StringVar(value=self.settings.get("custom_sound_path", ""))
        self.alarm_message = tk.StringVar(value=self.settings.get("default_message", "Пора вставать!"))
        self.repeat_count = tk.IntVar(value=self.settings.get("repeat_count", 1))
        self.snooze_time = tk.IntVar(value=self.settings.get("snooze_time", 5))

        # Дни недели
        self.days_vars = {
            "Пн": tk.BooleanVar(value=False),
            "Вт": tk.BooleanVar(value=False),
            "Ср": tk.BooleanVar(value=False),
            "Чт": tk.BooleanVar(value=False),
            "Пт": tk.BooleanVar(value=False),
            "Сб": tk.BooleanVar(value=False),
            "Вс": tk.BooleanVar(value=False)
        }

        # Создание интерфейса
        self.create_widgets()

    def create_widgets(self):
        # Вкладки
        tab_control = ttk.Notebook(self.root)

        # Основная вкладка (теперь содержит все настройки)
        main_tab = ttk.Frame(tab_control)
        tab_control.add(main_tab, text="Настройки будильника")

        # Вкладка списка будильников
        alarms_tab = ttk.Frame(tab_control)
        tab_control.add(alarms_tab, text="Мои будильники")

        tab_control.pack(expand=1, fill="both")

        # Основные настройки (вкладка 1)
        main_frame = ttk.Frame(main_tab)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Левая колонка - основные параметры
        left_frame = ttk.Frame(main_frame)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Правая колонка - дни недели и доп. настройки
        right_frame = ttk.Frame(main_frame)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        # Левая колонка: Основные параметры
        tk.Label(left_frame, text="Установите время будильника (ЧЧ:ММ):").pack(pady=5)

        vcmd = (self.root.register(self.validate_time_input), '%P')
        self.time_entry = tk.Entry(left_frame, textvariable=self.alarm_time,
                                   font=('Arial', 14), validate='key', validatecommand=vcmd)
        self.time_entry.pack()
        tk.Label(left_frame, text="Пример: 07:30").pack()

        # Поле для сообщения
        tk.Label(left_frame, text="Сообщение будильника:").pack(pady=5)
        tk.Entry(left_frame, textvariable=self.alarm_message, font=('Arial', 12)).pack()

        # Выбор звука
        tk.Label(left_frame, text="Выберите звук будильника:").pack(pady=5)

        sound_frame = tk.Frame(left_frame)
        sound_frame.pack()

        sound_options = ["стандартный", "мелодия", "свой звук"]
        for i, option in enumerate(sound_options):
            tk.Radiobutton(sound_frame, text=option, variable=self.alarm_sound,
                           value=option, command=self.update_sound_options).grid(row=0, column=i, padx=5)

        # Кнопка выбора файла
        self.sound_file_btn = tk.Button(left_frame, text="Выбрать файл",
                                        command=self.choose_sound_file, state='disabled')
        self.sound_file_btn.pack(pady=5)

        if self.alarm_sound.get() == "свой звук" and self.custom_sound_path.get():
            self.sound_file_btn.config(state='normal')
            tk.Label(left_frame, text=f"Выбран: {os.path.basename(self.custom_sound_path.get())}").pack()

        # Кнопки управления
        btn_frame = tk.Frame(left_frame)
        btn_frame.pack(pady=10)

        tk.Button(btn_frame, text="Добавить будильник", command=self.add_alarm).pack(side='left', padx=5)
        tk.Button(btn_frame, text="Остановить все", command=self.stop_all_alarms).pack(side='left', padx=5)

        # Правая колонка: Дни недели
        days_group = ttk.LabelFrame(right_frame, text="Дни срабатывания", padding=10)
        days_group.pack(fill=tk.BOTH, pady=5)

        for i, (day, var) in enumerate(self.days_vars.items()):
            tk.Checkbutton(days_group, text=day, variable=var).grid(row=i // 4, column=i % 4, padx=10, pady=5,
                                                                    sticky='w')

        # Дополнительные настройки
        settings_group = ttk.LabelFrame(right_frame, text="Дополнительные настройки", padding=10)
        settings_group.pack(fill=tk.BOTH, pady=5)

        # Количество повторений
        tk.Label(settings_group, text="Количество повторений сигнала:").pack(anchor='w')
        tk.Spinbox(settings_group, from_=1, to=10, textvariable=self.repeat_count).pack(fill=tk.X, pady=5)

        # Время откладывания
        tk.Label(settings_group, text="Время откладывания (мин):").pack(anchor='w')
        tk.Spinbox(settings_group, from_=1, to=30, textvariable=self.snooze_time).pack(fill=tk.X, pady=5)

        # Текущее время (внизу основной вкладки)
        self.time_label = tk.Label(main_tab, text="", font=('Arial', 16))
        self.time_label.pack(pady=10)

        # Список будильников (вкладка 2)
        self.alarms_listbox = tk.Listbox(alarms_tab, height=15, font=('Arial', 12))
        self.alarms_listbox.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        btn_frame_alarms = tk.Frame(alarms_tab)
        btn_frame_alarms.pack(pady=5)

        tk.Button(btn_frame_alarms, text="Удалить", command=self.remove_alarm).pack(side='left', padx=5)
        tk.Button(btn_frame_alarms, text="Остановить", command=self.stop_selected_alarm).pack(side='left', padx=5)
        tk.Button(btn_frame_alarms, text="Отложить", command=self.snooze_alarm).pack(side='left', padx=5)

        self.update_alarms_list()
        self.update_time()


    def update_sound_options(self):
        if self.alarm_sound.get() == "свой звук":
            self.sound_file_btn.config(state='normal')
        else:
            self.sound_file_btn.config(state='disabled')

    def choose_sound_file(self):
        try:
            file_path = filedialog.askopenfilename(
                title="Выберите звуковой файл",
                filetypes=(("WAV файлы", "*.wav"), ("MP3 файлы", "*.mp3"), ("Все файлы", "*.*"))
            )
            if file_path:
                if os.path.getsize(file_path) > 5 * 1024 * 1024:
                    messagebox.showerror("Ошибка", "Файл слишком большой (максимум 5MB)")
                    return

                self.custom_sound_path.set(file_path)
                messagebox.showinfo("Успешно", f"Выбран файл: {os.path.basename(file_path)}")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось загрузить файл: {str(e)}")

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
        try:
            digits = re.sub(r'[^\d]', '', time_str)

            if len(digits) < 4:
                digits = digits.zfill(4)

            hours = int(digits[:2])
            minutes = int(digits[2:4])

            if hours > 23 or minutes > 59:
                raise ValueError("Некорректное время")

            return f"{hours:02d}:{minutes:02d}"
        except Exception as e:
            messagebox.showerror("Ошибка", f"Некорректный формат времени: {str(e)}")
            return None

    def update_time(self):
        try:
            current_time = time.strftime("%H:%M:%S")
            current_weekday = ["Пн", "Вт", "Ср", "Чт", "Пт", "Сб", "Вс"][datetime.today().weekday()]
            self.time_label.config(text=f"Текущее время: {current_time}\nТекущий день: {current_weekday}")

            current_time_no_sec = time.strftime("%H:%M")
            for alarm in self.alarms:
                if alarm.get('active', False):
                    try:
                        selected_days = alarm.get('days', [])
                        day_check = (not selected_days) or (current_weekday in selected_days)

                        if current_time_no_sec == alarm['time'] and day_check:
                            self.trigger_alarm(alarm)
                    except Exception as e:
                        print(f"Ошибка при проверке будильника: {str(e)}")
        except Exception as e:
            print(f"Ошибка при обновлении времени: {str(e)}")

        self.root.after(1000, self.update_time)

    def add_alarm(self):
        try:
            time_str = self.format_time_input(self.alarm_time.get())
            if not time_str:
                return

            datetime.strptime(time_str, "%H:%M")

            selected_days = [day for day, var in self.days_vars.items() if var.get()]

            new_alarm = {
                'time': time_str,
                'sound': self.alarm_sound.get(),
                'custom_sound': self.custom_sound_path.get(),
                'message': self.alarm_message.get(),
                'days': selected_days,
                'active': True,
                'repeat': self.repeat_count.get(),
                'snooze_time': self.snooze_time.get()
            }

            for alarm in self.alarms:
                if alarm['time'] == time_str and set(alarm['days']) == set(selected_days):
                    messagebox.showwarning("Предупреждение", "Такой будильник уже существует!")
                    return

            self.alarms.append(new_alarm)
            self.save_settings()
            self.update_alarms_list()
            messagebox.showinfo("Будильник", f"Будильник на {time_str} добавлен")

            self.alarm_time.set("")
            for var in self.days_vars.values():
                var.set(False)

        except ValueError as ve:
            messagebox.showerror("Ошибка", f"Некорректное время: {str(ve)}")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось добавить будильник: {str(e)}")

    def stop_all_alarms(self):
        try:
            for alarm in self.alarms:
                alarm['active'] = False
            self.save_settings()
            self.update_alarms_list()
            messagebox.showinfo("Будильник", "Все будильники остановлены")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось остановить будильники: {str(e)}")

    def stop_selected_alarm(self):
        try:
            selection = self.alarms_listbox.curselection()
            if selection:
                index = selection[0]
                self.alarms[index]['active'] = False
                self.save_settings()
                self.update_alarms_list()
                messagebox.showinfo("Будильник", "Выбранный будильник остановлен")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось остановить будильник: {str(e)}")

    def remove_alarm(self):
        try:
            selection = self.alarms_listbox.curselection()
            if selection:
                index = selection[0]
                del self.alarms[index]
                self.save_settings()
                self.update_alarms_list()
                messagebox.showinfo("Будильник", "Будильник удален")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось удалить будильник: {str(e)}")

    def snooze_alarm(self):
        try:
            selection = self.alarms_listbox.curselection()
            if selection:
                index = selection[0]
                alarm = self.alarms[index]

                now = datetime.now()
                snooze_minutes = alarm.get('snooze_time', 5)
                new_time = (now + timedelta(minutes=snooze_minutes)).strftime("%H:%M")

                alarm['time'] = new_time
                alarm['active'] = True

                self.save_settings()
                self.update_alarms_list()
                messagebox.showinfo("Будильник",
                                    f"Будильник отложен на {snooze_minutes} минут. Новое время: {new_time}")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось отложить будильник: {str(e)}")

    def update_alarms_list(self):
        try:
            self.alarms_listbox.delete(0, tk.END)
            for alarm in sorted(self.alarms, key=lambda x: x['time']):
                days = ', '.join(alarm['days']) if alarm['days'] else 'каждый день'
                status = "Активен" if alarm.get('active', False) else "Не активен"
                repeat = f" | Повторов: {alarm.get('repeat', 1)}" if alarm.get('repeat', 1) > 1 else ""
                self.alarms_listbox.insert(tk.END, f"{alarm['time']} | {days} | {alarm['message']} | {status}{repeat}")
        except Exception as e:
            print(f"Ошибка при обновлении списка будильников: {str(e)}")

    def trigger_alarm(self, alarm):
        try:
            if alarm.get('repeat', 1) <= 1:
                alarm['active'] = False
            else:
                alarm['repeat'] -= 1

            self.save_settings()
            self.update_alarms_list()

            sound_thread = threading.Thread(target=self.play_sound, args=(alarm,))
            sound_thread.daemon = True
            sound_thread.start()

            messagebox.showinfo("Будильник", alarm['message'])
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось запустить будильник: {str(e)}")

    def play_sound(self, alarm):
        try:
            sound_type = alarm['sound']
            repeat = alarm.get('repeat', 1)

            if sound_type == "стандартный":
                for _ in range(repeat):
                    winsound.Beep(1000, 500)
                    time.sleep(0.5)
            elif sound_type == "мелодия":
                tones = [659, 659, 659, 523, 659, 784, 392]
                for _ in range(repeat):
                    for tone in tones:
                        winsound.Beep(tone, 500)
            elif sound_type == "свой звук" and alarm.get('custom_sound'):
                file_path = alarm['custom_sound']
                if file_path.lower().endswith('.wav'):
                    for _ in range(repeat):
                        winsound.PlaySound(file_path, winsound.SND_FILENAME)
                        time.sleep(1)
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось воспроизвести звук: {str(e)}")

    def save_default_settings(self):
        try:
            self.settings['default_sound'] = self.alarm_sound.get()
            self.settings['custom_sound_path'] = self.custom_sound_path.get()
            self.settings['default_message'] = self.alarm_message.get()
            self.settings['repeat_count'] = self.repeat_count.get()
            self.settings['snooze_time'] = self.snooze_time.get()

            self.save_settings()
            messagebox.showinfo("Настройки", "Настройки по умолчанию сохранены")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось сохранить настройки: {str(e)}")

    def save_settings(self):
        settings = {
            "alarms": self.alarms,
            "default_sound": self.alarm_sound.get(),
            "custom_sound_path": self.custom_sound_path.get(),
            "default_message": self.alarm_message.get(),
            "repeat_count": self.repeat_count.get(),
            "snooze_time": self.snooze_time.get()
        }

        try:
            with open(self.settings_file, 'w') as f:
                json.dump(settings, f, indent=2, ensure_ascii=False)
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось сохранить настройки: {str(e)}")

    def load_settings(self):
        try:
            if os.path.exists(self.settings_file):
                with open(self.settings_file, 'r') as f:
                    return json.load(f)
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось загрузить настройки: {str(e)}")
        return {}


if __name__ == "__main__":
    root = tk.Tk()
    try:
        app = AlarmClock(root)
        root.mainloop()
    except Exception as e:
        messagebox.showerror("Критическая ошибка", f"Программа завершилась с ошибкой: {str(e)}")