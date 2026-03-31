import tkinter as tk
from tkinter import ttk, filedialog
import os
import json
import shutil
from datetime import datetime
from tkinterdnd2 import DND_FILES

PASSWORD_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "safe_data.json")
SAFE_STORAGE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "safe_storage")
METADATA_FILE = os.path.join(SAFE_STORAGE_DIR, "metadata.json")

def init_storage():
    """Depolama dizinini ve metadata dosyasını hazırla."""
    if not os.path.exists(SAFE_STORAGE_DIR):
        os.makedirs(SAFE_STORAGE_DIR)
    if not os.path.exists(METADATA_FILE):
        with open(METADATA_FILE, "w", encoding="utf-8") as f:
            json.dump([], f)

def get_metadata():
    """Dosya listesini yükle."""
    init_storage()
    with open(METADATA_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_metadata(metadata):
    """Dosya listesini kaydet."""
    with open(METADATA_FILE, "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=4)

def format_size(size):
    """Bayt cinsinden boyutu okunabilir formata çevir."""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size < 1024:
            return f"{size:.1f} {unit}"
        size /= 1024
    return f"{size:.1f} TB"

def add_file_to_safe(file_path):
    """Dosyayı kasaya kopyala ve metadata ekle."""
    init_storage()
    filename = os.path.basename(file_path)
    dest_path = os.path.join(SAFE_STORAGE_DIR, filename)
    
    # Dosya isminde çakışma varsa benzersiz yap
    base, ext = os.path.splitext(filename)
    counter = 1
    while os.path.exists(dest_path):
        dest_path = os.path.join(SAFE_STORAGE_DIR, f"{base}_{counter}{ext}")
        counter += 1
    
    shutil.copy2(file_path, dest_path)
    
    stats = os.stat(file_path)
    metadata = get_metadata()
    metadata.append({
        "name": os.path.basename(dest_path),
        "created": datetime.fromtimestamp(stats.st_ctime).strftime("%Y-%m-%d %H:%M"),
        "size": format_size(stats.st_size),
        "uploaded": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    })
    save_metadata(metadata)
    return True

def delete_file_from_safe(filename):
    """Dosyayı kasadan ve diskten sil."""
    init_storage()
    file_path = os.path.join(SAFE_STORAGE_DIR, filename)
    
    # Dosyayı sil
    if os.path.exists(file_path):
        os.remove(file_path)
    
    # Metadata'dan sil
    metadata = get_metadata()
    metadata = [item for item in metadata if item["name"] != filename]
    save_metadata(metadata)
    return True


def load_password():
    """Kayitli şifreyi yükle. Yoksa None döndür."""
    if os.path.exists(PASSWORD_FILE):
        with open(PASSWORD_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            return data.get("password")
    return None


def save_password(password):
    """Şifreyi dosyaya kaydet."""
    with open(PASSWORD_FILE, "w", encoding="utf-8") as f:
        json.dump({"password": password}, f)


def delete_password():
    """Kayıtlı şifreyi sil."""
    if os.path.exists(PASSWORD_FILE):
        os.remove(PASSWORD_FILE)


def open_safe_window(parent, theme=None):
    """Şifre doğruysa açılan kasa penceresi."""
    if theme is None:
        theme = {"bg": "#FBFBFB", "fg": "#222222", "hover": "#E6E6E7"}

    safe_win = tk.Toplevel(parent)
    safe_win.title("Personal Safe")
    safe_win.geometry("800x600")
    safe_win.configure(bg=theme["bg"])
    safe_win.resizable(False, False)

    title = tk.Label(
        safe_win,
        text="Personal Safe - Documents",
        font=("Segoe UI", 18, "bold"),
        bg=theme["bg"],
        fg=theme["fg"],
    )
    title.pack(pady=(20, 10))

    # Treeview Styles
    style = ttk.Style()
    style.theme_use("clam")
    style.configure("Treeview", 
                    background="#FFFFFF", 
                    fieldbackground="#FFFFFF", 
                    foreground="#222222",
                    rowheight=35,
                    font=("Segoe UI", 10))
    style.map("Treeview", background=[('selected', theme["hover"])], foreground=[('selected', "#222222")])
    style.configure("Treeview.Heading", font=("Segoe UI", 10, "bold"), background=theme["bg"], foreground=theme["fg"], relief="flat")

    # Treeview Framework
    tree_frame = tk.Frame(safe_win, bg=theme["bg"], highlightthickness=0, bd=0)
    tree_frame.pack(fill="both", expand=True, padx=30, pady=10)

    columns = ("name", "created", "size", "uploaded")
    tree = ttk.Treeview(tree_frame, columns=columns, show="headings", height=10)
    
    tree.heading("name", text="File Name")
    tree.heading("created", text="Created Date")
    tree.heading("size", text="Size")
    tree.heading("uploaded", text="Upload Date")

    tree.column("name", width=300, anchor="w")
    tree.column("created", width=120, anchor="center")
    tree.column("size", width=80, anchor="center")
    tree.column("uploaded", width=140, anchor="center")

    tree.pack(fill="both", expand=True)

    def refresh_list():
        for item in tree.get_children():
            tree.delete(item)
        for data in get_metadata():
            tree.insert("", "end", values=(data["name"], data["created"], data["size"], data["uploaded"]))

    def handle_upload():
        files = filedialog.askopenfilenames(title="Select Documents")
        if files:
            for f in files:
                add_file_to_safe(f)
            refresh_list()

    def on_drop(event):
        # Sürüklenen dosya yollarını temizle
        files_str = event.data
        if files_str.startswith('{'):
            # Windows/Linux bracket format: {path1} {path2}
            import re
            files = re.findall(r'\{(.*?)\}', files_str)
        else:
            files = files_str.split()
            
        for f in files:
            if os.path.exists(f):
                add_file_to_safe(f)
        refresh_list()

    # Drag and Drop support for the treeview or window
    safe_win.drop_target_register(DND_FILES)
    safe_win.dnd_bind('<<Drop>>', on_drop)

    refresh_list()

    # Bottom Buttons Frame
    btn_frame = tk.Frame(safe_win, bg=theme["bg"], highlightthickness=0, bd=0)
    btn_frame.pack(pady=20)

    btn_upload = tk.Button(
        btn_frame,
        text="Upload Document",
        font=("Segoe UI", 10, "bold"),
        bg=theme["fg"],  # Zıt renk olsun diye fg'yi bg yaptık
        fg=theme["bg"],
        relief="flat",
        cursor="hand2",
        padx=20,
        pady=8,
        command=handle_upload,
        highlightthickness=0,
        bd=0
    )
    if theme["name"] == "Light": # Light temada zıtlık için tersi
        btn_upload.configure(bg="#E6E6E7", fg="#000000")
    elif theme["name"] == "Dark":
        btn_upload.configure(bg="#FBFBFB", fg="#222222")

    btn_upload.pack(side="left", padx=10)

    def handle_delete():
        selected = tree.selection()
        if not selected:
            return
        
        for item in selected:
            values = tree.item(item, "values")
            if values:
                filename = values[0]
                delete_file_from_safe(filename)
        refresh_list()

    btn_delete = tk.Button(
        btn_frame,
        text="Delete Document",
        font=("Segoe UI", 10, "bold"),
        bg="#F50430",
        fg="#FFFFFF" if theme["name"] != "Light" else "#000000",
        relief="flat",
        cursor="hand2",
        padx=20,
        pady=8,
        command=handle_delete,
        highlightthickness=0,
        bd=0
    )
    btn_delete.pack(side="left", padx=10)

    
    return safe_win


def open_password_window(parent, theme=None, on_success=None):
    """Safe butonuna basıldığında açılan şifre penceresi."""
    if theme is None:
        theme = {"bg": "#FBFBFB", "fg": "#222222", "hover": "#E6E6E7"}
        
    saved = load_password()
    is_first_time = saved is None

    win = tk.Toplevel(parent)
    win.title("Password")
    win.geometry("420x260")
    win.configure(bg=theme["bg"])
    win.resizable(False, False)
    win.grab_set()

    # Placeholder durumunu takip et
    is_placeholder = [True]

    # Yazı kutusu
    entry = tk.Entry(
        win,
        font=("Segoe UI", 13),
        width=30,
        relief="solid",
        bd=1,
    )
    entry.pack(pady=(40, 8))

    # Placeholder metni
    placeholder = (
        "Please choose your password."
        if is_first_time
        else "Please enter your password."
    )
    entry.insert(0, placeholder)
    entry.configure(fg="#AAAAAA" if theme["name"] != "Dark" else "#666666")

    # Show password checkbox
    show_var = tk.BooleanVar(value=False)

    def toggle_show_password():
        if is_placeholder[0]:
            return
        if show_var.get():
            entry.configure(show="")
        else:
            entry.configure(show="*")

    show_check = tk.Checkbutton(
        win,
        text="Show password",
        variable=show_var,
        command=toggle_show_password,
        font=("Segoe UI", 9),
        bg=theme["bg"],
        fg=theme["fg"],
        activebackground=theme["bg"],
        activeforeground=theme["fg"],
        cursor="hand2",
        highlightthickness=0,
        bd=0
    )
    show_check.pack(anchor="center", pady=(0, 4))

    def on_focus_in(event):
        if entry.get() == placeholder:
            entry.delete(0, tk.END)
            is_placeholder[0] = False
            entry.configure(fg="#222222")
            if not show_var.get():
                entry.configure(show="*")

    def on_focus_out(event):
        if entry.get() == "":
            is_placeholder[0] = True
            entry.configure(fg="#AAAAAA", show="")
            entry.insert(0, placeholder)

    entry.bind("<FocusIn>", on_focus_in)
    entry.bind("<FocusOut>", on_focus_out)

    # Mesaj etiketi
    msg_label = tk.Label(
        win,
        text="",
        font=("Segoe UI", 10),
        bg=theme["bg"],
    )
    msg_label.pack(pady=(4, 0))

    # Enter tuşuyla onaylama
    def on_submit(event=None):
        typed = entry.get().strip()
        if not typed or typed == placeholder:
            return

        if is_first_time:
            save_password(typed)
            msg_label.configure(
                text="Your password has been saved. Please close the window and log in again.",
                fg=theme["success_fg"],
            )
            entry.configure(state="disabled")
        else:
            if typed == saved:
                delete_password()  # Kasa açıldığında kayıtlı şifre sıfırlanır
                win.destroy()
                safe_win = open_safe_window(parent, theme)
                if on_success:
                    on_success(safe_win, typed) # Şifreyi de gönderiyoruz
            else:
                msg_label.configure(
                    text="The password you entered is incorrect.",
                    fg=theme["warn_fg"],
                )
                entry.delete(0, tk.END)
                entry.configure(show="*")
                entry.focus_set()

    entry.bind("<Return>", on_submit)

def open_lock_window(parent, theme=None, on_success=None):
    """Lock Safe butonuna basıldığında açılan yeni şifre belirleme penceresi."""
    if theme is None:
        theme = {"bg": "#FBFBFB", "fg": "#222222", "hover": "#E6E6E7"}

    win = tk.Toplevel(parent)
    win.title("Set New Password to Lock")
    win.geometry("420x260")
    win.configure(bg=theme["bg"])
    win.resizable(False, False)
    win.grab_set()

    is_placeholder = [True]

    entry = tk.Entry(
        win,
        font=("Segoe UI", 13),
        width=30,
        relief="solid",
        bd=1,
    )
    entry.pack(pady=(40, 8))

    placeholder = "Please choose your password."
    entry.insert(0, placeholder)
    entry.configure(fg="#AAAAAA" if theme["name"] != "Dark" else "#666666")

    show_var = tk.BooleanVar(value=False)

    def toggle_show_password():
        if is_placeholder[0]:
            return
        if show_var.get():
            entry.configure(show="")
        else:
            entry.configure(show="*")

    show_check = tk.Checkbutton(
        win,
        text="Show password",
        variable=show_var,
        command=toggle_show_password,
        font=("Segoe UI", 9),
        bg=theme["bg"],
        fg=theme["fg"],
        activebackground=theme["bg"],
        activeforeground=theme["fg"],
        cursor="hand2",
        highlightthickness=0,
        bd=0
    )
    show_check.pack(anchor="center", pady=(0, 4))

    def on_focus_in(event):
        if entry.get() == placeholder:
            entry.delete(0, tk.END)
            is_placeholder[0] = False
            entry.configure(fg="#222222")
            if not show_var.get():
                entry.configure(show="*")

    def on_focus_out(event):
        if entry.get() == "":
            is_placeholder[0] = True
            entry.configure(fg="#AAAAAA", show="")
            entry.insert(0, placeholder)

    entry.bind("<FocusIn>", on_focus_in)
    entry.bind("<FocusOut>", on_focus_out)

    msg_label = tk.Label(
        win,
        text="",
        font=("Segoe UI", 10),
        bg=theme["bg"],
    )
    msg_label.pack(pady=(4, 0))

    def on_submit(event=None):
        typed = entry.get().strip()
        if not typed or typed == placeholder:
            return

        save_password(typed)
        win.destroy() # Pencereyi hemen kapat
        if on_success:
            on_success() # Kasa kilitlensin

    entry.bind("<Return>", on_submit)
