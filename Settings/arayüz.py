import os
import ctypes

try:
    # 2 = PROCESS_PER_MONITOR_DPI_AWARE (Ekran ölçeğine göre maksimum çözünürlük)
    ctypes.windll.shcore.SetProcessDpiAwareness(2)
except Exception:
    try:
        # Eski Windows sürümlerinde şansımızı deneyelim
        ctypes.windll.user32.SetProcessDPIAware()
    except Exception:
        pass

import tkinter as tk
from tkinterdnd2 import DND_FILES, TkinterDnD
from kasa import *
import json
import webbrowser
from settings import *


class AntigravityApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Antigravity")
        self.root.geometry("900x550")
        self.root.configure(bg="#FBFBFB")
        self.root.resizable(False, False)
        
        # Tema Ayarları
        self.settings_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "settings.json")
        self.current_theme_name = self.load_theme_preference()
        self.current_theme = THEMES.get(self.current_theme_name, THEMES["Light"])

        # Program kapatılırken otomatik kilitlenme protokolü
        self.root.protocol("WM_DELETE_WINDOW", self.on_app_close)

        # Başlık (Tema uygulanabilir)
        self.main_title = tk.Label(
            root,
            text="Personal Safe",
            font=("Segoe UI", 20, "bold"),
            bg=self.current_theme["bg"],
            fg=self.current_theme["fg"],
        )
        self.main_title.pack(side="top", fill="x", pady=(0, 0))
        self.main_title.configure(height=2) # Başlık alanını biraz genişletelim

        # Sol menü çerçevesi
        self.sidebar = tk.Frame(root, bg=self.current_theme["bg"], highlightthickness=0, bd=0)
        self.sidebar.pack(side="left", fill="y", padx=(30, 0), pady=20)

        # Menü butonları
        menu_items = ["Safe", "Settings", "GitHub", "Contact To Me"]
        self.current_view = "None" # Takip için

        self.status_label = None
        self.lock_btn = None
        self.locked_label = None
        self.safe_btn = None
        self.is_unlocked = False
        self.opened_safe_win = None
        self.last_password = None
        self.menu_buttons = [] # Temayı sonradan güncelleyebilmek için tutuyoruz

        for item in menu_items:
            # "Safe" butonu için ekstra widgetlar ekleyebileceğimiz bir çerçeve
            if item == "Safe":
                self.row_frame = tk.Frame(self.sidebar, bg=self.current_theme["bg"], highlightthickness=0, bd=0)
                self.row_frame.pack(fill="x", pady=2)
                
                self.safe_btn = tk.Label(
                    self.row_frame,
                    text=item,
                    font=("Segoe UI", 13),
                    bg=self.current_theme["bg"],
                    fg=self.current_theme["fg"],
                    cursor="hand2",
                    padx=18,
                    pady=8,
                    anchor="center",
                    width=16,
                    highlightthickness=0,
                    bd=0
                )
                self.safe_btn.pack(fill="x")
                self.menu_buttons.append(self.safe_btn)

                # "Safe is locked" etiketi (Sağda, butonun üstünde)
                self.locked_label = tk.Label(
                    self.row_frame,
                    text="safe is locked",
                    font=("Segoe UI", 9, "italic"),
                    bg=self.current_theme["bg"],
                    fg=self.current_theme["warn_fg"]
                )
                self.locked_label.place(relx=0.65, rely=0.5, anchor="w")
                self.locked_label.lift()

                # "Safe Opened" etiketi
                self.status_label = tk.Label(
                    self.row_frame,
                    text="Safe is Opened",
                    font=("Segoe UI", 10, "italic"),
                    bg=self.current_theme["bg"],
                    fg=self.current_theme["success_fg"]
                )
                
                # "Lock Safe" butonu
                self.lock_btn = tk.Label(
                    self.row_frame,
                    text="Lock Safe",
                    font=("Segoe UI", 10, "underline"),
                    bg=self.current_theme["bg"],
                    fg=self.current_theme["warn_fg"],
                    cursor="hand2"
                )
                self.lock_btn.bind("<Enter>", lambda e: self.lock_btn.configure(fg=self.current_theme["fg"]))
                self.lock_btn.bind("<Leave>", lambda e: self.lock_btn.configure(fg=self.current_theme["warn_fg"]))
                self.lock_btn.bind("<Button-1>", lambda e: self.handle_lock_click())

                self.safe_btn.bind("<Enter>", lambda e, b=self.safe_btn: self.on_menu_enter(b))
                self.safe_btn.bind("<Leave>", lambda e, b=self.safe_btn: self.on_menu_leave(b))
                self.safe_btn.bind("<Button-1>", lambda e: self.handle_safe_click())
            else:
                btn = tk.Label(
                    self.sidebar,
                    text=item,
                    font=("Segoe UI", 13),
                    bg=self.current_theme["bg"],
                    fg=self.current_theme["fg"],
                    cursor="hand2",
                    padx=18,
                    pady=8,
                    anchor="center",
                    width=16,
                    highlightthickness=0,
                    bd=0
                )
                btn.pack(fill="x", pady=2)
                self.menu_buttons.append(btn)

                if item == "Settings":
                    btn.bind("<Button-1>", lambda e: self.handle_settings_click())
                elif item == "GitHub":
                    btn.bind("<Button-1>", lambda e: webbrowser.open("https://github.com/demircagand"))
                elif item == "Contact To Me":
                    btn.bind("<Button-1>", lambda e: self.handle_contact_click())
                
                btn.bind("<Enter>", lambda e, b=btn: self.on_menu_enter(b))
                btn.bind("<Leave>", lambda e, b=btn: self.on_menu_leave(b))

        # Sağ taraf – içerik alanı
        self.content = tk.Frame(root, bg=self.current_theme["bg"])
        self.content.pack(side="left", fill="both", expand=True)

    def on_menu_enter(self, btn):
        btn.configure(bg=self.current_theme["hover"])

    def on_menu_leave(self, btn):
        btn.configure(bg=self.current_theme["bg"])

    def get_current_fg(self):
        return self.current_theme["fg"]


    def handle_safe_click(self):
        if self.is_unlocked:
            # Şifre sormadan doğrudan kasayı aç
            from kasa import open_safe_window
            # Eğer halihazırda açık bir pencere varsa odaklanalım ya da yenisini açalım
            if self.opened_safe_win and self.opened_safe_win.winfo_exists():
                self.opened_safe_win.lift()
            else:
                self.opened_safe_win = open_safe_window(self.root, self.current_theme)
        else:
            open_password_window(self.root, self.current_theme, on_success=self.set_unlocked_state)

    def handle_lock_click(self):
        if self.is_unlocked:
            open_lock_window(self.root, self.current_theme, on_success=self.set_locked_state)

    def handle_settings_click(self):
        self.current_view = "Settings"
        show_settings_view(self.content, self)

    def handle_contact_click(self):
        self.current_view = "Contact"
        show_contact_view(self.content, self)

    def apply_theme(self, theme_name):
        """Uygulamanın temasını değiştir."""
        if theme_name not in THEMES:
            return
        
        self.current_theme_name = theme_name
        self.current_theme = THEMES[theme_name]
        self.save_theme_preference(theme_name)

        # Görselleri güncelle
        self.root.configure(bg=self.current_theme["bg"])
        self.main_title.configure(bg=self.current_theme["bg"], fg=self.current_theme["fg"])
        self.sidebar.configure(bg=self.current_theme["bg"])
        self.content.configure(bg=self.current_theme["bg"])
        self.row_frame.configure(bg=self.current_theme["bg"])
        
        self.locked_label.configure(bg=self.current_theme["bg"])
        self.status_label.configure(bg=self.current_theme["bg"])
        self.lock_btn.configure(bg=self.current_theme["bg"])

        for btn in self.menu_buttons:
            btn.configure(bg=self.current_theme["bg"], fg=self.current_theme["fg"])

        # Görsel güncellemeyi zorla
        self.root.update_idletasks()

        # Ayarlar görünümünü yenile (içerik alanındaki yazılar için)
        if self.current_view == "Settings":
            show_settings_view(self.content, self)
        elif self.current_view == "Contact":
            show_contact_view(self.content, self)

    def load_theme_preference(self):
        if os.path.exists(self.settings_file):
            with open(self.settings_file, "r") as f:
                data = json.load(f)
                return data.get("theme", "Light")
        return "Light"

    def save_theme_preference(self, theme_name):
        with open(self.settings_file, "w") as f:
            json.dump({"theme": theme_name}, f)

    def set_unlocked_state(self, safe_win, password):
        self.is_unlocked = True
        self.last_password = password
        self.opened_safe_win = safe_win
        
        self.locked_label.place_forget()
        self.status_label.place(relx=0.65, rely=0.3, anchor="w")
        self.lock_btn.place(relx=0.65, rely=0.7, anchor="w")
        self.status_label.lift()
        self.lock_btn.lift()

    def set_locked_state(self):
        self.is_unlocked = False
        self.status_label.place_forget()
        self.lock_btn.place_forget()
        self.locked_label.place(relx=0.65, rely=0.5, anchor="w")
        self.locked_label.lift()

        if self.opened_safe_win and self.opened_safe_win.winfo_exists():
            self.opened_safe_win.destroy()
        self.opened_safe_win = None

    def on_app_close(self):
        """Program kapatılırken eğer kasa açıksa eski şifreyle kilitle."""
        if self.is_unlocked and self.last_password:
            from kasa import save_password
            save_password(self.last_password)
        self.root.destroy()

if __name__ == "__main__":
    root = TkinterDnD.Tk()
    app = AntigravityApp(root)
    root.mainloop()
