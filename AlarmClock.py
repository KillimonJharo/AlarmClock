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
        self.root.geometry("600x650")

        # Загрузка сохраненных настроек
        self.settings_file = "alarm_settings.json"
        self.settings = self.load_settings()

        # Переменные
        self.alarms = self.settings.get("alarms", [])  # Список активных будильников
        self.current_alarm = {}  # Текущие настройки для нового будильника
        self.alarm_time = tk.StringVar(value="")
        self.alarm_sound = tk.StringVar(value="стандартный")
        self.custom_sound_path = tk.StringVar(value="")
        self.alarm_message = tk.StringVar(value="Пора вставать!")
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

        # Основная вкладка
        main_tab = ttk.Frame(tab_control)
        tab_control.add(main_tab, text="Основные настройки")

        # Вкладка дней недели
        days_tab = ttk.Frame(tab_control)
        tab_control.add(days_tab, text="Дни недели")

        # Вкладка списка будильников
        alarms_tab = ttk.Frame(tab_control)
        tab_control.add(alarms_tab, text="Мои будильники")

        tab_control.pack(expand=1, fill="both")

        # Основные настройки (вкладка 1)
        tk.Label(main_tab, text="Установите время будильника (ЧЧ:ММ):").pack(pady=5)

        vcmd = (self.root.register(self.validate_time_input), '%P')
        self.time_entry = tk.Entry(main_tab, textvariable=self.alarm_time,
                                   font=('Arial', 14), validate='key', validatecommand=vcmd)
        self.time_entry.pack()
        tk.Label(main_tab, text="Пример: 07:30").pack()

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

        tk.Button(btn_frame, text="Добавить будильник", command=self.add_alarm).pack(side='left', padx=5)
        tk.Button(btn_frame, text="Остановить все", command=self.stop_all_alarms).pack(side='left', padx=5)

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

        # Список будильников (вкладка 3)
        self.alarms_listbox = tk.Listbox(alarms_tab, height=15, font=('Arial', 12))
        self.alarms_listbox.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        btn_frame_alarms = tk.Frame(alarms_tab)
        btn_frame_alarms.pack(pady=5)

        tk.Button(btn_frame_alarms, text="Удалить", command=self.remove_alarm).pack(side='left', padx=5)
        tk.Button(btn_frame_alarms, text="Остановить", command=self.stop_selected_alarm).pack(side='left', padx=5)

        self.update_alarms_list()

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

        # Проверяем все активные будильники
        current_time_no_sec = time.strftime("%H:%M")
        for alarm in self.alarms:
            if alarm.get('active', False):
                try:
                    # Проверяем день недели (если выбраны дни)
                    selected_days = alarm.get('days', [])
                    day_check = (not selected_days) or (current_weekday in selected_days)

                    if current_time_no_sec == alarm['time'] and day_check:
                        self.trigger_alarm(alarm)
                except:
                    pass

        self.root.after(1000, self.update_time)

    def add_alarm(self):
        try:
            time_str = self.format_time_input(self.alarm_time.get())
            datetime.strptime(time_str, "%H:%M")

            # Собираем выбранные дни
            selected_days = [day for day, var in self.days_vars.items() if var.get()]

            new_alarm = {
                'time': time_str,
                'sound': self.alarm_sound.get(),
                'custom_sound': self.custom_sound_path.get(),
                'message': self.alarm_message.get(),
                'days': selected_days,
                'active': True
            }

            self.alarms.append(new_alarm)
            self.save_settings()
            self.update_alarms_list()
            messagebox.showinfo("Будильник", f"Будильник на {time_str} добавлен")

            # Сбрасываем поля ввода
            self.alarm_time.set("")
            for var in self.days_vars.values():
                var.set(False)

        except ValueError:
            messagebox.showerror("Ошибка", "Пожалуйста, введите корректное время (ЧЧ:ММ)")

    def stop_all_alarms(self):
        for alarm in self.alarms:
            alarm['active'] = False
        self.save_settings()
        messagebox.showinfo("Будильник", "Все будильники остановлены")

    def stop_selected_alarm(self):
        selection = self.alarms_listbox.curselection()
        if selection:
            index = selection[0]
            self.alarms[index]['active'] = False
            self.save_settings()
            self.update_alarms_list()
            messagebox.showinfo("Будильник", "Выбранный будильник остановлен")

    def remove_alarm(self):
        selection = self.alarms_listbox.curselection()
        if selection:
            index = selection[0]
            del self.alarms[index]
            self.save_settings()
            self.update_alarms_list()
            messagebox.showinfo("Будильник", "Будильник удален")

    def update_alarms_list(self):
        self.alarms_listbox.delete(0, tk.END)
        for alarm in self.alarms:
            days = ', '.join(alarm['days']) if alarm['days'] else 'каждый день'
            status = "Активен" if alarm.get('active', False) else "Не активен"
            self.alarms_listbox.insert(tk.END,
                                       f"{alarm['time']} | {days} | {alarm['message']} | {status}")

    def trigger_alarm(self, alarm):
        # Помечаем будильник как неактивный, чтобы не срабатывал повторно
        alarm['active'] = False
        self.save_settings()
        self.update_alarms_list()

        sound_thread = threading.Thread(target=self.play_sound, args=(alarm,))
        sound_thread.daemon = True
        sound_thread.start()

        messagebox.showinfo("Будильник", alarm['message'])

    def play_sound(self, alarm):
        sound_type = alarm['sound']

        if sound_type == "стандартный":
            for _ in range(5):
                winsound.Beep(1000, 500)
                time.sleep(0.5)
        elif sound_type == "мелодия":
            tones = [659, 659, 659, 523, 659, 784, 392]
            for tone in tones:
                winsound.Beep(tone, 500)
        elif sound_type == "свой звук" and alarm.get('custom_sound'):
            try:
                # Для WAV файлов
                if alarm['custom_sound'].lower().endswith('.wav'):
                    winsound.PlaySound(alarm['custom_sound'], winsound.SND_FILENAME)
                # Для MP3 и других форматов потребуется дополнительная библиотека
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось воспроизвести файл: {e}")

    def save_settings(self):
        settings = {
            "alarms": self.alarms
        }

        try:
            with open(self.settings_file, 'w') as f:
                json.dump(settings, f, indent=2)
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