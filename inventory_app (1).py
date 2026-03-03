import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
import os

# ─────────────────────────────────────────────
#  CONSTANTS & THEME
# ─────────────────────────────────────────────
DB_FILE = "inventory.db"

COLORS = {
    "bg":         "#0F1117",
    "surface":    "#1A1D27",
    "card":       "#22263A",
    "border":     "#2E3250",
    "accent":     "#5B6EF5",
    "accent2":    "#7C3AED",
    "success":    "#10B981",
    "danger":     "#EF4444",
    "warning":    "#F59E0B",
    "text":       "#F1F5F9",
    "text_muted": "#94A3B8",
    "input_bg":   "#2D3149",
}

FONT_HEADING  = ("Segoe UI", 22, "bold")
FONT_SUBHEAD  = ("Segoe UI", 13, "bold")
FONT_BODY     = ("Segoe UI", 10)
FONT_SMALL    = ("Segoe UI", 9)
FONT_MONO     = ("Consolas", 10)

CREDENTIALS = {"admin": "admin123", "user": "user123"}

CATEGORIES = [
    {"label": "Elektronik",  "emoji": "⚡", "color": COLORS["accent"]},
    {"label": "Furniture",   "emoji": "🪑", "color": COLORS["accent2"]},
    {"label": "Peralatan",   "emoji": "🔧", "color": COLORS["warning"]},
]

# ─────────────────────────────────────────────
#  DATABASE HELPERS
# ─────────────────────────────────────────────
def get_db():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    with get_db() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS inventory (
                id       INTEGER PRIMARY KEY AUTOINCREMENT,
                nama     TEXT NOT NULL,
                stok     INTEGER NOT NULL,
                harga    TEXT NOT NULL,
                kategori TEXT NOT NULL
            )
        """)
        conn.commit()

def db_get_items(kategori):
    with get_db() as conn:
        rows = conn.execute(
            "SELECT * FROM inventory WHERE kategori=? ORDER BY id DESC", (kategori,)
        ).fetchall()
    return rows

def db_search_items(kategori, keyword):
    keyword = f"%{keyword}%"
    with get_db() as conn:
        rows = conn.execute(
            """SELECT * FROM inventory
               WHERE kategori=? AND (nama LIKE ? OR stok LIKE ? OR harga LIKE ?)
               ORDER BY id DESC""",
            (kategori, keyword, keyword, keyword)
        ).fetchall()
    return rows

def db_insert(nama, stok, harga, kategori):
    with get_db() as conn:
        conn.execute(
            "INSERT INTO inventory (nama, stok, harga, kategori) VALUES (?,?,?,?)",
            (nama, stok, harga, kategori)
        )
        conn.commit()

def db_update(item_id, nama, stok, harga):
    with get_db() as conn:
        conn.execute(
            "UPDATE inventory SET nama=?, stok=?, harga=? WHERE id=?",
            (nama, stok, harga, item_id)
        )
        conn.commit()

def db_delete(item_id):
    with get_db() as conn:
        conn.execute("DELETE FROM inventory WHERE id=?", (item_id,))
        conn.commit()

# ─────────────────────────────────────────────
#  UTILITY
# ─────────────────────────────────────────────
def format_rupiah(value: str) -> str:
    """Convert raw number string to Rp format."""
    digits = "".join(c for c in value if c.isdigit())
    if not digits:
        return ""
    return "Rp " + "{:,.0f}".format(int(digits)).replace(",", ".")

def parse_rupiah(value: str) -> str:
    """Strip Rp formatting back to digits only."""
    return "".join(c for c in value if c.isdigit())

# ─────────────────────────────────────────────
#  STYLED WIDGETS HELPERS
# ─────────────────────────────────────────────
def make_button(parent, text, command, color=None, width=14, **kw):
    bg = color or COLORS["accent"]
    btn = tk.Button(
        parent, text=text, command=command,
        bg=bg, fg=COLORS["text"],
        font=("Segoe UI", 10, "bold"),
        relief="flat", cursor="hand2",
        padx=12, pady=8,
        activebackground=bg, activeforeground=COLORS["text"],
        width=width, **kw
    )
    btn.bind("<Enter>", lambda e: btn.config(bg=_lighten(bg)))
    btn.bind("<Leave>", lambda e: btn.config(bg=bg))
    return btn

def _lighten(hex_color):
    """Slightly lighten a hex color."""
    hex_color = hex_color.lstrip("#")
    r, g, b = [int(hex_color[i:i+2], 16) for i in (0, 2, 4)]
    r, g, b = min(255, r+30), min(255, g+30), min(255, b+30)
    return f"#{r:02x}{g:02x}{b:02x}"

def make_entry(parent, textvariable=None, show=None, width=28):
    e = tk.Entry(
        parent,
        textvariable=textvariable,
        show=show,
        bg=COLORS["input_bg"],
        fg=COLORS["text"],
        insertbackground=COLORS["text"],
        relief="flat",
        font=FONT_BODY,
        width=width,
    )
    e.bind("<FocusIn>",  lambda ev: e.config(highlightthickness=2, highlightcolor=COLORS["accent"], highlightbackground=COLORS["accent"]))
    e.bind("<FocusOut>", lambda ev: e.config(highlightthickness=0))
    return e

def make_label(parent, text, font=FONT_BODY, color=None, **kw):
    return tk.Label(
        parent, text=text, font=font,
        bg=kw.pop("bg", COLORS["bg"]),
        fg=color or COLORS["text"], **kw
    )

# ─────────────────────────────────────────────
#  BASE PAGE
# ─────────────────────────────────────────────
class BasePage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg=COLORS["bg"])
        self.controller = controller

    def show(self):
        self.tkraise()

# ─────────────────────────────────────────────
#  LOGIN PAGE
# ─────────────────────────────────────────────
class LoginPage(BasePage):
    def __init__(self, parent, controller):
        super().__init__(parent, controller)

        # background gradient effect (canvas)
        canvas = tk.Canvas(self, bg=COLORS["bg"], highlightthickness=0)
        canvas.place(relwidth=1, relheight=1)
        self._draw_bg(canvas)

        # card
        card = tk.Frame(self, bg=COLORS["surface"], padx=48, pady=48)
        card.place(relx=0.5, rely=0.5, anchor="center")

        # logo / title
        tk.Label(card, text="📦", font=("Segoe UI", 38), bg=COLORS["surface"], fg=COLORS["accent"]).pack()
        tk.Label(card, text="Inventory System", font=("Segoe UI", 20, "bold"),
            bg=COLORS["surface"], fg=COLORS["text"]).pack(pady=(4, 2))
        tk.Label(card, text="Masuk ke akun Anda", font=FONT_SMALL,
            bg=COLORS["surface"], fg=COLORS["text_muted"]).pack(pady=(0, 28))

        # username
        tk.Label(card, text="Username", font=("Segoe UI", 9, "bold"),
            bg=COLORS["surface"], fg=COLORS["text_muted"]).pack(anchor="w")
        self.var_user = tk.StringVar()
        ue = make_entry(card, textvariable=self.var_user, width=30)
        ue.pack(ipady=7, fill="x", pady=(4, 16))

        # password
        tk.Label(card, text="Password", font=("Segoe UI", 9, "bold"),
            bg=COLORS["surface"], fg=COLORS["text_muted"]).pack(anchor="w")
        self.var_pass = tk.StringVar()
        self.pass_entry = make_entry(card, textvariable=self.var_pass, show="●", width=30)
        self.pass_entry.pack(ipady=7, fill="x", pady=(4, 8))

        # show/hide checkbox
        self.show_pass = tk.BooleanVar()
        chk = tk.Checkbutton(
            card, text="Tampilkan Password",
            variable=self.show_pass, command=self._toggle_pass,
            bg=COLORS["surface"], fg=COLORS["text_muted"],
            activebackground=COLORS["surface"], activeforeground=COLORS["text"],
            selectcolor=COLORS["input_bg"],
            font=FONT_SMALL, cursor="hand2"
        )
        chk.pack(anchor="w", pady=(0, 24))

        # login button
        btn = make_button(card, "  Masuk  →", self._login, color=COLORS["accent"], width=30)
        btn.pack(ipady=4, fill="x")

        # hint
        tk.Label(card, text="Demo: admin / admin123",
            font=FONT_SMALL, bg=COLORS["surface"], fg=COLORS["text_muted"]).pack(pady=(16, 0))

        ue.focus_set()
        self.bind_all("<Return>", lambda e: self._login())

    def _draw_bg(self, canvas):
        canvas.after(10, lambda: self._place_circles(canvas))

    def _place_circles(self, canvas):
        w = canvas.winfo_width() or 1920
        h = canvas.winfo_height() or 1080
        canvas.create_oval(-100, -100, 400, 400, fill="#1a1d35", outline="")
        canvas.create_oval(w-300, h-300, w+100, h+100, fill="#1a1d35", outline="")
        canvas.create_oval(w-200, 0, w+200, 400, fill="#16193a", outline="")

    def _toggle_pass(self):
        self.pass_entry.config(show="" if self.show_pass.get() else "●")

    def _login(self):
        u = self.var_user.get().strip()
        p = self.var_pass.get().strip()
        if CREDENTIALS.get(u) == p:
            self.var_user.set("")
            self.var_pass.set("")
            self.show_pass.set(False)
            self.pass_entry.config(show="●")
            self.controller.show_page("WelcomePage")
        else:
            messagebox.showerror("Login Gagal", "Username atau password salah.\nCoba: admin / admin123")

# ─────────────────────────────────────────────
#  WELCOME PAGE
# ─────────────────────────────────────────────
class WelcomePage(BasePage):
    def __init__(self, parent, controller):
        super().__init__(parent, controller)

        # top bar
        topbar = tk.Frame(self, bg=COLORS["surface"], pady=14)
        topbar.pack(fill="x")
        tk.Label(topbar, text="📦  Inventory System", font=("Segoe UI", 14, "bold"),
            bg=COLORS["surface"], fg=COLORS["text"]).pack(side="left", padx=24)
        make_button(topbar, "⏻  Logout", self._logout,
                    color=COLORS["danger"], width=10).pack(side="right", padx=20)

        # hero
        hero = tk.Frame(self, bg=COLORS["bg"])
        hero.pack(expand=True, fill="both")

        tk.Label(hero, text="Selamat Datang di", font=("Segoe UI", 16),
            bg=COLORS["bg"], fg=COLORS["text_muted"]).pack(pady=(60, 0))
        tk.Label(hero, text="Inventory System", font=("Segoe UI", 36, "bold"),
            bg=COLORS["bg"], fg=COLORS["text"]).pack()
        tk.Label(hero, text="Pilih kategori untuk mengelola data inventaris",
            font=("Segoe UI", 12), bg=COLORS["bg"], fg=COLORS["text_muted"]).pack(pady=(8, 48))

        # category cards
        cards_frame = tk.Frame(hero, bg=COLORS["bg"])
        cards_frame.pack()

        for cat in CATEGORIES:
            self._make_category_card(cards_frame, cat)

    def _make_category_card(self, parent, cat):
        frame = tk.Frame(parent, bg=COLORS["surface"], padx=32, pady=32,
            relief="flat", bd=0)
        frame.pack(side="left", padx=16, pady=8)

        # colored top stripe
        stripe = tk.Frame(frame, bg=cat["color"], height=4)
        stripe.pack(fill="x", pady=(0, 20))

        tk.Label(frame, text=cat["emoji"], font=("Segoe UI", 32),
            bg=COLORS["surface"]).pack()
        tk.Label(frame, text=cat["label"], font=("Segoe UI", 14, "bold"),
            bg=COLORS["surface"], fg=COLORS["text"]).pack(pady=(8, 20))

        btn = make_button(frame, f"Buka {cat['label']}",
                lambda c=cat["label"]: self._open_category(c),
                color=cat["color"], width=16)
        btn.pack()

        # hover effect on card
        def on_enter(e):
            frame.config(bg=COLORS["card"])
            for w in frame.winfo_children():
                if isinstance(w, (tk.Label, tk.Frame)):
                    try: w.config(bg=COLORS["card"])
                    except: pass
        def on_leave(e):
            frame.config(bg=COLORS["surface"])
            for w in frame.winfo_children():
                if isinstance(w, (tk.Label, tk.Frame)):
                    try:
                        if w == frame.winfo_children()[0]:
                            w.config(bg=cat["color"])
                        else:
                            w.config(bg=COLORS["surface"])
                    except: pass

        frame.bind("<Enter>", on_enter)
        frame.bind("<Leave>", on_leave)

    def _open_category(self, kategori):
        self.controller.frames["InventoryPage"].load_category(kategori)
        self.controller.show_page("InventoryPage")

    def _logout(self):
        self.controller.show_page("LoginPage")

# ─────────────────────────────────────────────
#  INVENTORY PAGE
# ─────────────────────────────────────────────
class InventoryPage(BasePage):
    def __init__(self, parent, controller):
        super().__init__(parent, controller)
        self.current_kategori = ""
        self.selected_id = None

        self._build_ui()

    def _build_ui(self):
        # ── TOP BAR ──────────────────────────────
        topbar = tk.Frame(self, bg=COLORS["surface"], pady=12)
        topbar.pack(fill="x")

        make_button(topbar, "← Kembali", lambda: self.controller.show_page("WelcomePage"),
                    color=COLORS["border"], width=12).pack(side="left", padx=20)

        self.title_label = tk.Label(topbar, text="", font=("Segoe UI", 15, "bold"),
                                    bg=COLORS["surface"], fg=COLORS["text"])
        self.title_label.pack(side="left", padx=12)

        # ── MAIN AREA ────────────────────────────
        main = tk.Frame(self, bg=COLORS["bg"])
        main.pack(fill="both", expand=True, padx=24, pady=20)

        # ── FORM PANEL ───────────────────────────
        form_panel = tk.Frame(main, bg=COLORS["surface"], padx=24, pady=24, width=300)
        form_panel.pack(side="left", fill="y", padx=(0, 16))
        form_panel.pack_propagate(False)

        tk.Label(form_panel, text="Form Input", font=FONT_SUBHEAD,
                 bg=COLORS["surface"], fg=COLORS["text"]).pack(anchor="w", pady=(0, 20))

        # nama barang
        tk.Label(form_panel, text="Nama Barang", font=("Segoe UI", 9, "bold"),
                 bg=COLORS["surface"], fg=COLORS["text_muted"]).pack(anchor="w")
        self.var_nama = tk.StringVar()
        self._styled_entry(form_panel, self.var_nama).pack(fill="x", ipady=7, pady=(4, 14))

        # stok
        tk.Label(form_panel, text="Stok", font=("Segoe UI", 9, "bold"),
                 bg=COLORS["surface"], fg=COLORS["text_muted"]).pack(anchor="w")
        self.var_stok = tk.StringVar()
        self._styled_entry(form_panel, self.var_stok).pack(fill="x", ipady=7, pady=(4, 14))

        # harga
        tk.Label(form_panel, text="Harga (Rupiah)", font=("Segoe UI", 9, "bold"),
                 bg=COLORS["surface"], fg=COLORS["text_muted"]).pack(anchor="w")
        self.var_harga = tk.StringVar()
        harga_entry = self._styled_entry(form_panel, self.var_harga)
        harga_entry.pack(fill="x", ipady=7, pady=(4, 4))
        self.var_harga.trace_add("write", self._format_harga)
        self._formatting = False

        tk.Label(form_panel, text="Contoh: 1500000 → Rp 1.500.000",
                 font=FONT_SMALL, bg=COLORS["surface"], fg=COLORS["text_muted"]).pack(anchor="w", pady=(0, 24))

        # buttons
        make_button(form_panel, "➕  Tambah", self._tambah,
                    color=COLORS["success"]).pack(fill="x", ipady=5, pady=(0, 8))
        make_button(form_panel, "✏️  Update", self._update,
                    color=COLORS["accent"]).pack(fill="x", ipady=5, pady=(0, 8))
        make_button(form_panel, "🗑️  Hapus", self._hapus,
                    color=COLORS["danger"]).pack(fill="x", ipady=5, pady=(0, 8))
        make_button(form_panel, "✖  Bersihkan", self._clear_form,
                    color=COLORS["border"]).pack(fill="x", ipady=5)

        # ── TABLE PANEL ──────────────────────────
        table_panel = tk.Frame(main, bg=COLORS["surface"])
        table_panel.pack(side="left", fill="both", expand=True)

        # header row 1: title + count
        header = tk.Frame(table_panel, bg=COLORS["surface"], pady=(14), padx=16)
        header.pack(fill="x")
        self.count_label = tk.Label(header, text="", font=FONT_SMALL,
                                    bg=COLORS["surface"], fg=COLORS["text_muted"])
        self.count_label.pack(side="right")
        tk.Label(header, text="Data Inventaris", font=FONT_SUBHEAD,
                 bg=COLORS["surface"], fg=COLORS["text"]).pack(side="left")

        # header row 2: search bar
        search_bar = tk.Frame(table_panel, bg=COLORS["surface"], padx=16, pady=(0))
        search_bar.pack(fill="x", pady=(0, 10))

        # search icon label
        tk.Label(search_bar, text="🔍", font=("Segoe UI", 11),
                 bg=COLORS["input_bg"], fg=COLORS["text_muted"]).pack(side="left", ipadx=8, ipady=6)

        self.var_search = tk.StringVar()
        self.var_search.trace_add("write", self._on_search_change)
        search_entry = tk.Entry(
            search_bar, textvariable=self.var_search,
            bg=COLORS["input_bg"], fg=COLORS["text"],
            insertbackground=COLORS["text"],
            relief="flat", font=FONT_BODY,
        )
        search_entry.pack(side="left", fill="x", expand=True, ipady=7)
        search_entry.bind("<FocusIn>",  lambda e: search_entry.config(
            highlightthickness=2, highlightcolor=COLORS["accent"], highlightbackground=COLORS["accent"]))
        search_entry.bind("<FocusOut>", lambda e: search_entry.config(highlightthickness=0))

        # placeholder
        self._search_placeholder = "Cari nama barang, stok, atau harga..."
        self._search_has_focus = False
        search_entry.insert(0, self._search_placeholder)
        search_entry.config(fg=COLORS["text_muted"])

        def on_focus_in(e):
            if search_entry.get() == self._search_placeholder:
                search_entry.delete(0, "end")
                search_entry.config(fg=COLORS["text"])
            search_entry.config(highlightthickness=2,
                highlightcolor=COLORS["accent"], highlightbackground=COLORS["accent"])

        def on_focus_out(e):
            if not search_entry.get():
                search_entry.insert(0, self._search_placeholder)
                search_entry.config(fg=COLORS["text_muted"])
            search_entry.config(highlightthickness=0)

        search_entry.bind("<FocusIn>",  on_focus_in)
        search_entry.bind("<FocusOut>", on_focus_out)
        self._search_entry = search_entry

        # clear search button
        self.btn_clear_search = tk.Button(
            search_bar, text="✕", command=self._clear_search,
            bg=COLORS["input_bg"], fg=COLORS["text_muted"],
            font=("Segoe UI", 10, "bold"),
            relief="flat", cursor="hand2",
            padx=10, pady=0,
            activebackground=COLORS["input_bg"], activeforeground=COLORS["danger"],
        )
        self.btn_clear_search.pack(side="left", ipady=6)

        # search status label
        self.search_status = tk.Label(table_panel, text="",
                                      font=FONT_SMALL, bg=COLORS["surface"],
                                      fg=COLORS["warning"])
        self.search_status.pack(anchor="w", padx=16, pady=(0, 6))

        # treeview
        self._build_treeview(table_panel)

    def _styled_entry(self, parent, textvariable):
        e = tk.Entry(
            parent, textvariable=textvariable,
            bg=COLORS["input_bg"], fg=COLORS["text"],
            insertbackground=COLORS["text"],
            relief="flat", font=FONT_BODY,
        )
        e.bind("<FocusIn>",  lambda ev: e.config(highlightthickness=2, highlightcolor=COLORS["accent"], highlightbackground=COLORS["accent"]))
        e.bind("<FocusOut>", lambda ev: e.config(highlightthickness=0))
        return e

    def _build_treeview(self, parent):
        style = ttk.Style()
        style.theme_use("default")
        style.configure("Dark.Treeview",
            background=COLORS["card"],
            foreground=COLORS["text"],
            fieldbackground=COLORS["card"],
            rowheight=36,
            font=FONT_BODY,
            borderwidth=0,
        )
        style.configure("Dark.Treeview.Heading",
            background=COLORS["border"],
            foreground=COLORS["text"],
            font=("Segoe UI", 10, "bold"),
            relief="flat",
        )
        style.map("Dark.Treeview",
            background=[("selected", COLORS["accent"])],
            foreground=[("selected", "#ffffff")],
        )

        cols = ("ID", "Nama Barang", "Stok", "Harga")
        frame = tk.Frame(parent, bg=COLORS["surface"])
        frame.pack(fill="both", expand=True, padx=16, pady=(0, 16))

        self.tree = ttk.Treeview(frame, columns=cols, show="headings",
                                  style="Dark.Treeview", selectmode="browse")
        widths = {"ID": 50, "Nama Barang": 220, "Stok": 80, "Harga": 150}
        for col in cols:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=widths[col], anchor="center" if col != "Nama Barang" else "w")

        vsb = ttk.Scrollbar(frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=vsb.set)
        vsb.pack(side="right", fill="y")
        self.tree.pack(fill="both", expand=True)

        self.tree.bind("<<TreeviewSelect>>", self._on_select)

    # ── RUPIAH FORMATTER ─────────────────────
    def _format_harga(self, *args):
        if self._formatting:
            return
        self._formatting = True
        raw = self.var_harga.get()
        digits = parse_rupiah(raw)
        if digits:
            formatted = format_rupiah(digits)
            self.var_harga.set(formatted)
        elif raw == "" or raw == "Rp ":
            self.var_harga.set("")
        self._formatting = False

    # ── CATEGORY LOADER ──────────────────────
    def load_category(self, kategori):
        self.current_kategori = kategori
        color = next((c["color"] for c in CATEGORIES if c["label"] == kategori), COLORS["accent"])
        emoji = next((c["emoji"] for c in CATEGORIES if c["label"] == kategori), "📦")
        self.title_label.config(text=f"{emoji}  Kategori: {kategori}", fg=color)
        self._clear_search()
        self._clear_form()
        self._refresh_table()

    # ── SEARCH HELPERS ───────────────────────
    def _get_search_keyword(self):
        val = self.var_search.get()
        if val == self._search_placeholder:
            return ""
        return val.strip()

    def _on_search_change(self, *args):
        self._refresh_table()

    def _clear_search(self):
        self.var_search.set("")
        self._search_entry.delete(0, "end")
        self._search_entry.insert(0, self._search_placeholder)
        self._search_entry.config(fg=COLORS["text_muted"])
        self._refresh_table()

    # ── CRUD OPERATIONS ──────────────────────
    def _tambah(self):
        nama, stok, harga = self._get_form()
        if not nama or not stok or not harga:
            messagebox.showwarning("Input Kosong", "Semua field harus diisi.")
            return
        if not stok.isdigit():
            messagebox.showwarning("Input Salah", "Stok harus berupa angka.")
            return
        db_insert(nama, int(stok), harga, self.current_kategori)
        self._clear_form()
        self._refresh_table()
        messagebox.showinfo("Sukses", f"Barang '{nama}' berhasil ditambahkan.")

    def _update(self):
        if self.selected_id is None:
            messagebox.showwarning("Pilih Data", "Pilih baris yang ingin diupdate.")
            return
        nama, stok, harga = self._get_form()
        if not nama or not stok or not harga:
            messagebox.showwarning("Input Kosong", "Semua field harus diisi.")
            return
        if not stok.isdigit():
            messagebox.showwarning("Input Salah", "Stok harus berupa angka.")
            return
        db_update(self.selected_id, nama, int(stok), harga)
        self._clear_form()
        self._refresh_table()
        messagebox.showinfo("Sukses", "Data berhasil diupdate.")

    def _hapus(self):
        if self.selected_id is None:
            messagebox.showwarning("Pilih Data", "Pilih baris yang ingin dihapus.")
            return
        if messagebox.askyesno("Konfirmasi", "Hapus data ini?"):
            db_delete(self.selected_id)
            self._clear_form()
            self._refresh_table()

    # ── HELPERS ──────────────────────────────
    def _get_form(self):
        return (
            self.var_nama.get().strip(),
            self.var_stok.get().strip(),
            self.var_harga.get().strip(),
        )

    def _clear_form(self):
        self.var_nama.set("")
        self.var_stok.set("")
        self.var_harga.set("")
        self.selected_id = None
        if self.tree.selection():
            self.tree.selection_remove(self.tree.selection())

    def _refresh_table(self):
        for row in self.tree.get_children():
            self.tree.delete(row)
        keyword = self._get_search_keyword()
        if keyword:
            items = db_search_items(self.current_kategori, keyword)
            total = db_get_items(self.current_kategori)
            self.search_status.config(
                text=f"🔍  Menampilkan {len(items)} dari {len(total)} item  —  kata kunci: \"{keyword}\"",
                fg=COLORS["warning"]
            )
        else:
            items = db_get_items(self.current_kategori)
            self.search_status.config(text="")
        for item in items:
            self.tree.insert("", "end", values=(item["id"], item["nama"], item["stok"], item["harga"]))
        self.count_label.config(text=f"{len(items)} item")

    def _on_select(self, event):
        sel = self.tree.selection()
        if not sel:
            return
        values = self.tree.item(sel[0], "values")
        self.selected_id = int(values[0])
        self.var_nama.set(values[1])
        self.var_stok.set(values[2])
        self.var_harga.set(values[3])

# ─────────────────────────────────────────────
#  MAIN APPLICATION
# ─────────────────────────────────────────────
class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Inventory Management System")
        self.state("zoomed")           # fullscreen on Windows
        try:
            self.attributes("-zoomed", True)   # Linux fallback
        except Exception:
            pass
        self.configure(bg=COLORS["bg"])
        self.resizable(True, True)

        init_db()

        container = tk.Frame(self, bg=COLORS["bg"])
        container.pack(fill="both", expand=True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        self.frames = {}
        for PageClass in (LoginPage, WelcomePage, InventoryPage):
            page = PageClass(container, self)
            self.frames[PageClass.__name__] = page
            page.grid(row=0, column=0, sticky="nsew")

        self.show_page("LoginPage")

    def show_page(self, name):
        self.frames[name].show()

# ─────────────────────────────────────────────
#  ENTRY POINT
# ─────────────────────────────────────────────
if __name__ == "__main__":
    app = App()
    app.mainloop()
