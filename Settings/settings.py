import tkinter as tk

from kasa import *
THEMES = {
    "Fire": {
        "name": "Fire",
        "bg": "#F21707",
        "hover": "#F5564B",
        "fg": "#FFFFFF",
        "warn_fg": "#000000",
        "success_fg": "#FFFFFF"
    },
    "Dark": {
        "name": "Dark",
        "bg": "#1B1B1B",
        "hover": "#494949",
        "fg": "#FFFFFF",
        "warn_fg": "#FF3333",
        "success_fg": "#05F50D"
    },
    "Midnight Blue": {
        "name": "Midnight Blue",
        "bg": "#050D54",
        "hover": "#061385",
        "fg": "#FFFFFF",
        "warn_fg": "#FF5555",
        "success_fg": "#05F50D"
    },
    "Light": {
        "name": "Light",
        "bg": "#FBFBFE",
        "hover": "#DDDDDF",
        "fg": "#222222",
        "warn_fg": "#F50430",
        "success_fg": "#008800"
    }
}

def show_settings_view(parent_frame, app_instance):
    """Ayarlar görünümünü içerik alanına yükle."""
    # Eski içeriği temizle
    for widget in parent_frame.winfo_children():
        widget.destroy()

    title = tk.Label(
        parent_frame,
        text="Selection Theme",
        font=("Segoe UI", 20, "bold"),
        bg=parent_frame["bg"],
        fg=app_instance.get_current_fg(),
    )
    title.pack(pady=(40, 40))

    # Temaları yan yana dizeceğimiz çerçeve
    themes_container = tk.Frame(parent_frame, bg=parent_frame["bg"])
    themes_container.pack(pady=20)

    for name, colors in THEMES.items():
        theme_box_frame = tk.Frame(themes_container, bg=parent_frame["bg"], padx=15)
        theme_box_frame.pack(side="left")

        # Renk önizleme dikdörtgeni
        preview = tk.Frame(
            theme_box_frame,
            width=120,
            height=80,
            bg=colors["bg"],
            highlightbackground="#CCCCCC",
            highlightthickness=1,
            cursor="hand2"
        )
        preview.pack_propagate(False)
        preview.pack()

        # İsim etiketi
        label = tk.Label(
            theme_box_frame,
            text=name,
            font=("Segoe UI", 11),
            bg=parent_frame["bg"],
            fg=app_instance.get_current_fg(),
            pady=10,
            cursor="hand2"
        )
        label.pack()

        # Tıklama olayları
        def make_apply(n):
            return lambda e: app_instance.apply_theme(n)

        preview.bind("<Button-1>", make_apply(name))
        label.bind("<Button-1>", make_apply(name))
    
    # Delete All Files Button
    delete_frame = tk.Frame(parent_frame, bg=parent_frame["bg"])
    delete_frame.pack(pady=40)
    
    # Kırmızı veya karanlık temada siyah arka plan
    del_btn_bg = "#000000" if app_instance.current_theme["name"] == "Dark" else "#F50430"
    
    btn_delete_all = tk.Button(
        delete_frame,
        text="Delete all the files",
        font=("Segoe UI", 12, "bold"),
        bg=del_btn_bg,
        fg="#FFFFFF",
        relief="flat",
        cursor="hand2",
        padx=25,
        pady=10,
        command=lambda: handle_delete_all(parent_frame, app_instance),
        highlightthickness=0,
        bd=0
    )
    btn_delete_all.pack()


def handle_delete_all(parent_frame, app_instance):
    """Tüm dosyaları silme onayı penceresi."""
    theme = app_instance.current_theme
    
    confirm_win = tk.Toplevel(parent_frame)
    confirm_win.title("Do you approve?")
    confirm_win.geometry("400x180")
    confirm_win.configure(bg=theme["bg"])
    confirm_win.resizable(False, False)
    confirm_win.grab_set()
    
    msg_lbl = tk.Label(
        confirm_win,
        text="Do you approve deleting all files in the safe?",
        font=("Segoe UI", 12),
        bg=theme["bg"],
        fg=theme["fg"],
        wraplength=350,
        justify="center"
    )
    msg_lbl.pack(pady=(30, 20))
    
    btn_frame = tk.Frame(confirm_win, bg=theme["bg"])
    btn_frame.pack()
    
    def on_yes():
        delete_all_files_from_safe()
        if hasattr(app_instance, "opened_safe_win") and app_instance.opened_safe_win:
            if app_instance.opened_safe_win.winfo_exists():
                app_instance.opened_safe_win.destroy()
            app_instance.opened_safe_win = None
        confirm_win.destroy()
        
    def on_no():
        confirm_win.destroy()
        
    btn_yes = tk.Button(
        btn_frame,
        text="Yes",
        font=("Segoe UI", 10, "bold"),
        bg="#F50430",
        fg="#FFFFFF",
        relief="flat",
        width=10,
        cursor="hand2",
        command=on_yes,
        highlightthickness=0,
        bd=0
    )
    btn_yes.pack(side="left", padx=15)
    
    btn_no = tk.Button(
        btn_frame,
        text="No",
        font=("Segoe UI", 10, "bold"),
        bg=theme["fg"],
        fg=theme["bg"],
        relief="flat",
        width=10,
        cursor="hand2",
        command=on_no,
        highlightthickness=0,
        bd=0
    )
    btn_no.pack(side="left", padx=15)

def show_contact_view(parent_frame, app_instance):
    """İletişim bilgilerini içerik alanına yükle."""
    # Eski içeriği temizle
    for widget in parent_frame.winfo_children():
        widget.destroy()

    contact_text = (
        "Please contact me regarding any bugs you find.\n\n"
        "My e-mail: demircagand@gmail.com"
    )

    label = tk.Label(
        parent_frame,
        text=contact_text,
        font=("Segoe UI", 14),
        bg=parent_frame["bg"],
        fg=app_instance.get_current_fg(),
        justify="center",
        pady=100
    )
    label.pack(expand=True, fill="both")
