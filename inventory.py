import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk

# ===================== DARK MODE COLORS =====================
BG_DARK = "#1e1e1e"
BG_FRAME = "#252526"
BG_ENTRY = "#2d2d2d"
FG_TEXT = "#ffffff"
BTN_PRIMARY = "#0e639c"
BTN_DANGER = "#c62828"
BTN_SECONDARY = "#3a3d41"
BTN_WARNING = "#f9a825"
SELECT_COLOR = "#094771"

# ===================== HARGA =====================
def format_rupiah(value):
    try:
        return f"Rp {int(value):,}".replace(",", ".")
    except:
        return "Rp 0"

# ===================== BASE PAGE =====================
class BasePage(tk.Frame):
    def __init__(self, master):
        super().__init__(master, bg=BG_DARK)
        self.pack(fill="both", expand=True)

        # TOP BAR
        # self.topbar = tk.Frame(self, bg="#181818", height=60)
        # self.topbar.pack(fill="x")

        # LOGO
        img = Image.open("ikile.png").resize((200, 120))
        self.logo_img = ImageTk.PhotoImage(img)
        tk.Label(self, image=self.logo_img, bg=BG_DARK).pack(anchor="nw", padx=10, pady=10)

# ===================== LOGIN PAGE =====================
class LoginPage(BasePage):
    def __init__(self, master, on_success):
        super().__init__(master)
        self.on_success = on_success

        box = tk.Frame(self, bg=BG_FRAME, padx=30, pady=30)
        box.place(relx=0.5, rely=0.5, anchor="center")

        tk.Label(box, text="LOGIN ADMIN", bg=BG_FRAME, fg=FG_TEXT,
                 font=("Segoe UI", 18, "bold")).pack(pady=15)

        self.username = tk.StringVar()
        self.password = tk.StringVar()
        self.show_pw = tk.BooleanVar()

        def entry(label, var, show=None):
            tk.Label(box, text=label, bg=BG_FRAME, fg=FG_TEXT).pack(anchor="w")
            e = tk.Entry(box, textvariable=var, show=show,
                         bg=BG_ENTRY, fg=FG_TEXT,
                         insertbackground=FG_TEXT, width=30)
            e.pack(pady=5)
            return e

        entry("Username", self.username)
        self.pw_entry = entry("Password", self.password, "*")

        tk.Checkbutton(
            box, text="Lihat Password",
            variable=self.show_pw,
            command=lambda: self.pw_entry.config(show="" if self.show_pw.get() else "*"),
            bg=BG_FRAME, fg=FG_TEXT,
            selectcolor=BG_FRAME
        ).pack(anchor="w", pady=5)

        tk.Button(box, text="Login",
                  bg=BTN_PRIMARY, fg="white",
                  relief="flat", width=30,
                  command=self.login).pack(pady=15)

    def login(self):
        if self.username.get() == "apis" and self.password.get() == "apiskerensigmaskibidi":
            self.on_success()
        else:
            messagebox.showerror("Error", "Username atau password salah")

# ===================== WELCOME PAGE =====================
class WelcomePage(BasePage):
    def __init__(self, master, open_category, logout):
        super().__init__(master)

        center = tk.Frame(self, bg=BG_DARK)
        center.place(relx=0.5, rely=0.5, anchor="center")

        tk.Label(center, text="Selamat Datang di IKILE Inventory",
                 bg=BG_DARK, fg=FG_TEXT,
                 font=("Segoe UI", 20, "bold")).pack(pady=20)

        for cat in ["Elektronik", "Furniture", "Peralatan"]:
            tk.Button(
                center, text=cat,
                bg=BTN_SECONDARY, fg="white",
                width=30, pady=10,
                relief="flat",
                command=lambda c=cat: open_category(c)
            ).pack(pady=5)

        tk.Button(center, text="Logout",
                  bg=BTN_DANGER, fg="white",
                  width=20, relief="flat",
                  command=logout).pack(pady=20)

# ===================== INVENTORY PAGE =====================
class InventoryPage(BasePage):
    def __init__(self, master, category, go_back):
        super().__init__(master)
        self.category = category
        self.go_back = go_back
        self.data = []
        self.selected_index = None

        # HEADER
        header = tk.Frame(self, bg=BG_DARK)
        header.pack(fill="x", pady=10)

        tk.Label(header, text=f"Inventory - {category}",
                 bg=BG_DARK, fg=FG_TEXT,
                 font=("Segoe UI", 16, "bold")).pack(side="left", padx=20)

        tk.Button(header, text="← Kembali",
                  bg=BTN_SECONDARY, fg="white",
                  relief="flat",
                  command=self.go_back).pack(side="right", padx=20)

        # FORM
        form = tk.Frame(self, bg=BG_FRAME, padx=15, pady=15)
        form.pack(fill="x", padx=20, pady=10)

        self.nama = tk.StringVar()
        self.stok = tk.StringVar()
        self.harga = tk.StringVar()

        for i, (label, var) in enumerate([
            ("Nama Barang", self.nama),
            ("Stok", self.stok),
            ("Harga", self.harga)
        ]):
            tk.Label(form, text=label, bg=BG_FRAME, fg=FG_TEXT).grid(row=0, column=i)
            tk.Entry(form, textvariable=var,
                     bg=BG_ENTRY, fg=FG_TEXT,
                     insertbackground=FG_TEXT,
                     width=25).grid(row=1, column=i, padx=5)

        tk.Button(form, text="Tambah",
                  bg=BTN_PRIMARY, fg="white",
                  relief="flat",
                  command=self.add).grid(row=1, column=3, padx=5)

        tk.Button(form, text="Update",
                  bg=BTN_WARNING, fg="black",
                  relief="flat",
                  command=self.update).grid(row=1, column=4, padx=5)

        # TABLE
        style = ttk.Style()
        style.theme_use("default")
        style.configure("Treeview", background=BG_ENTRY,
                        foreground=FG_TEXT, rowheight=28,
                        fieldbackground=BG_ENTRY)
        style.configure("Treeview.Heading",
                        background=BG_FRAME, foreground=FG_TEXT)
        style.map("Treeview", background=[("selected", SELECT_COLOR)])

        self.table = ttk.Treeview(self, columns=("Nama", "Stok", "Harga"), show="headings")
        for col in ("Nama", "Stok", "Harga"):
            self.table.heading(col, text=col)
            self.table.column(col, anchor="center")

        self.table.pack(fill="both", expand=True, padx=20, pady=10)
        self.table.bind("<<TreeviewSelect>>", self.select)

        tk.Button(self, text="Hapus Data Terpilih",
                  bg=BTN_DANGER, fg="white",
                  relief="flat",
                  command=self.delete).pack(pady=10)

    def refresh(self):
        self.table.delete(*self.table.get_children())
        for item in self.data:
            self.table.insert("", "end", values=item)

    def add(self):
        self.data.append((self.nama.get(), self.stok.get(), format_rupiah(self.harga.get())))
        self.refresh()
        self.clear()

    def select(self, _):
        selected = self.table.selection()
        if not selected:
            return
        self.selected_index = self.table.index(selected[0])
        nama, stok, harga = self.data[self.selected_index]
        self.nama.set(nama)
        self.stok.set(stok)
        self.harga.set(harga.replace("Rp ", "").replace(".", ""))

    def update(self):
        if self.selected_index is None:
            return
        self.data[self.selected_index] = (
            self.nama.get(),
            self.stok.get(),
            format_rupiah(self.harga.get())
        )
        self.refresh()
        self.clear()

    def delete(self):
        if self.selected_index is None:
            return
        self.data.pop(self.selected_index)
        self.refresh()
        self.clear()

    def clear(self):
        self.nama.set("")
        self.stok.set("")
        self.harga.set("")
        self.selected_index = None

# ===================== APP ROOT =====================
class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("IKILE Inventory System")
        self.configure(bg=BG_DARK)

        # FULLSCREEN
        self.state("zoomed")

        self.current = None
        self.show_login()

    def clear(self):
        if self.current:
            self.current.destroy()

    def show_login(self):
        self.clear()
        self.current = LoginPage(self, self.show_welcome)

    def show_welcome(self):
        self.clear()
        self.current = WelcomePage(self, self.show_inventory, self.show_login)

    def show_inventory(self, category):
        self.clear()
        self.current = InventoryPage(self, category, self.show_welcome)

if __name__ == "__main__":
    App().mainloop()
