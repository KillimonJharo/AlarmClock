import tkinter as tk
from tkinter import messagebox, filedialog
import time
import winsound
from datetime import datetime
import threading


class AlarmClock:
    def __init__(self, root):
        self.root = root
        self.root.title("Будильник")
        self.root.geometry("400x300")

        self.alarm_time = tk.StringVar()
        self.alarm_sound = tk.StringVar(value="стандартный")
        self.alarm_active = False

        self.create_widgets()

    def create_widgets(self):
        tk.Label(self.root, text="Установите время будильника (ЧЧ:ММ):").pack(pady=10)
        tk.Entry(self.root, textvariable=self.alarm_time, font=('Arial', 14)).pack()


        tk.Label(self.root, text="Выберите звук будильника:").pack(pady=10)
        sound_options = ["стандартный", "мелодия", "свой звук"]
        for option in sound_options:
            tk.Radiobutton(self.root, text=option, variable=self.alarm_sound, value=option).pack(anchor='w')


        tk.Button(self.root, text="Установить будильник", command=self.set_alarm).pack(pady=10)
        tk.Button(self.root, text="Выключить будильник", command=self.stop_alarm).pack(pady=5)


        self.time_label = tk.Label(self.root, text="", font=('Arial', 16))
        self.time_label.pack(pady=20)


        self.update_time()

    def update_time(self):
        current_time = time.strftime("%H:%M:%S")
        self.time_label.config(text=f"Текущее время: {current_time}")


        if self.alarm_active:
            try:
                alarm_time = self.alarm_time.get()
                current_time_no_sec = time.strftime("%H:%M")
                if current_time_no_sec == alarm_time:
                    self.trigger_alarm()
            except:
                pass


        self.root.after(1000, self.update_time)


    def set_alarm(self):
        alarm_time = self.alarm_time.get()
        try:
            datetime.strptime(alarm_time, "%H:%M")
            self.alarm_active = True
            messagebox.showinfo("Будильник", f"Будильник установлен на {alarm_time}")
        except ValueError:
            messagebox.showerror("Ошибка", "Пожалуйста, введите время в формате ЧЧ:ММ")


    def stop_alarm(self):
        self.alarm_active = False
        messagebox.showinfo("Будильник", "Будильник выключен")


    def trigger_alarm(self):
        self.alarm_active = False

        sound_thread = threading.Thread(target=self.play_sound)
        sound_thread.daemon = True
        sound_thread.start()

        messagebox.showinfo("Будильник", "Пора вставать!")


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
        elif sound_type == "свой звук":
            for _ in range(3):
                winsound.Beep(880, 500)
                winsound.Beep(440, 500)


if __name__ == "__main__":
    root = tk.Tk()
    app = AlarmClock(root)
    root.mainloop()