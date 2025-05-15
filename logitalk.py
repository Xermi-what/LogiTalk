import threading
from socket import *
from customtkinter import *


class MainWindow(CTk):
    def __init__(self):
        super().__init__()
        self.geometry('600x400')
        self.title("CTk Chat")
        set_appearance_mode("dark")
        set_default_color_theme("green")

        self.username = 'Myroslav'
        self.is_show_menu = False
        self.speed_animate_menu = -5
        self.label = None
        self.menu_frame = CTkFrame(self, width=30, height=400, fg_color="gray20", corner_radius=0)
        self.menu_frame.pack_propagate(False)
        self.menu_frame.place(x=0, y=0)
        self.btn = CTkButton(self, text='▶️', command=self.toggle_show_menu, width=30)
        self.btn.place(x=0, y=0)
        self.chat_field = CTkTextbox(self, font=('Segoe UI', 13), state='disabled', wrap='word', corner_radius=10)
        self.chat_field.place(x=40, y=0)
        self.message_entry = CTkEntry(self, placeholder_text='Введіть повідомлення...', height=40, corner_radius=10)
        self.message_entry.place(x=40, y=360)
        self.send_button = CTkButton(self, text='Надіслати', width=80, height=40,command=self.send_message, corner_radius=10)
        self.send_button.place(x=520, y=360)

        try:
            self.sock = socket(AF_INET, SOCK_STREAM)
            self.sock.connect(('localhost', 8080))
            hello = f"TEXT@{self.username}@[SYSTEM] {self.username} приєднався(лась) до чату!\n"
            self.sock.send(hello.encode('utf-8'))
            threading.Thread(target=self.recv_message, daemon=True).start()
        except Exception as e:
            self.add_message(f"[ERROR] Не вдалося підключитися до сервера: {e}")

        self.adaptive_ui()

    def toggle_show_menu(self):
        if self.is_show_menu:
            self.is_show_menu = False
            self.speed_animate_menu *= -1
            self.btn.configure(text='▶️')
            self.show_menu()
        else:
            self.is_show_menu = True
            self.speed_animate_menu *= -1
            self.btn.configure(text='◀️')
            self.show_menu()
            self.label = CTkLabel(self.menu_frame, text='Імʼя', font=('Segoe UI', 14))
            self.label.pack(pady=20)
            self.entry = CTkEntry(self.menu_frame)
            self.entry.pack(pady=10)

    def show_menu(self):
        self.menu_frame.configure(width=self.menu_frame.winfo_width() + self.speed_animate_menu)
        if not self.menu_frame.winfo_width() >= 200 and self.is_show_menu:
            self.after(10, self.show_menu)
        elif self.menu_frame.winfo_width() >= 40 and not self.is_show_menu:
            self.after(10, self.show_menu)
            if self.label and self.entry:
                self.label.destroy()
                self.entry.destroy()

    def adaptive_ui(self):
        self.menu_frame.configure(height=self.winfo_height())
        self.chat_field.place(x=self.menu_frame.winfo_width(), y=0)
        self.chat_field.configure(width=self.winfo_width() - self.menu_frame.winfo_width() - 10,
                                  height=self.winfo_height() - 50)
        self.send_button.place(x=self.winfo_width() - 90, y=self.winfo_height() - 45)
        self.message_entry.place(x=self.menu_frame.winfo_width() + 10, y=self.send_button.winfo_y())
        self.message_entry.configure(
            width=self.winfo_width() - self.menu_frame.winfo_width() - self.send_button.winfo_width() - 20)

        self.after(100, self.adaptive_ui)

    def add_message(self, text):
        self.chat_field.configure(state='normal')
        self.chat_field.insert(END, text + '\n')
        self.chat_field.configure(state='disabled')
        self.chat_field.see(END)

    def send_message(self):
        message = self.message_entry.get()
        if message:
            self.add_message(f"Я: {message}")
            data = f"TEXT@{self.username}@{message}\n"
            try:
                self.sock.sendall(data.encode())
            except:
                self.add_message("[ERROR] Повідомлення не вдалося надіслати")
        self.message_entry.delete(0, END)

    def recv_message(self):
        buffer = ""
        while True:
            try:
                chunk = self.sock.recv(4096)
                if not chunk:
                    break
                buffer += chunk.decode()

                while "\n" in buffer:
                    line, buffer = buffer.split("\n", 1)
                    self.handle_line(line.strip())
            except:
                break
        self.sock.close()

    def handle_line(self, line):
        if not line:
            return
        parts = line.split("@", 3)
        msg_type = parts[0]

        if msg_type == "TEXT" and len(parts) >= 3:
            author = parts[1]
            message = parts[2]
            if author != self.username:
                self.add_message(f"{author}: {message}")
        elif msg_type == "IMAGE" and len(parts) >= 4:
            author = parts[1]
            filename = parts[2]
            self.add_message(f"{author} надіслав(ла) зображення: {filename}")
        else:
            self.add_message(line)


if __name__ == "__main__":
    win = MainWindow()
    win.mainloop()