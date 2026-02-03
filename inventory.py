import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3

# ================= DARK MODE COLORS =================
BG_DARK = "#1e1e1e"
BG_FRAME = "#252526"
BG_ENTRY = "#2d2d2d"
FG_TEXT = "#ffffff"
BTN_PRIMARY = "#0e639c"
BTN_DANGER = "#c62828"
SELECT_COLOR = "#094771"

# ================= DATABASE =================
class Database:
    def __init__(self):
        self.conn = sqlite3.connect("inventory.db")
        self.cursor = self.conn.cursor()
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS barang (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nama TEXT,
                stok INTEGER,
                harga INTEGER
            )
        """)
        self.conn.commit()

    def get_all(self):
        self.cursor.execute("SELECT * FROM barang")
        return self.cursor.fetchall()

    def insert(self, nama, stok, harga):
        self.cursor.execute(
            "INSERT INTO barang (nama, stok, harga) VALUES (?, ?, ?)",
            (nama, stok, harga)
        )
        self.conn.commit()

    def update(self, id_, nama, stok, harga):
        self.cursor.execute(
            "UPDATE barang SET nama=?, stok=?, harga=? WHERE id=?",
            (nama, stok, harga, id_)
        )
        self.conn.commit()

    def delete(self, id_):
        self.cursor.execute("DELETE FROM barang WHERE id=?", (id_,))
        self.conn.commit()

    def search(self, keyword):
        self.cursor.execute(
            "SELECT * FROM barang WHERE nama LIKE ?",
            (f"%{keyword}%",)
        )
        return self.cursor.fetchall()


# ================= APP =================
class InventoryApp:
    def __init__(self, root):
        self.db = Database()
        self.selected_id = None
        self.root = root

        root.title("Inventory Barang")
        root.geometry("900x500")
        root.configure(bg=BG_DARK)

        self.set_style()
        self.build_ui()
        self.load_data()

    def set_style(self):
        style = ttk.Style()
        style.theme_use("default")

        style.configure(
            "Treeview",
            background=BG_ENTRY,
            foreground=FG_TEXT,
            rowheight=26,
            fieldbackground=BG_ENTRY
        )
        style.configure(
            "Treeview.Heading",
            background=BG_FRAME,
            foreground=FG_TEXT
        )
        style.map(
            "Treeview",
            background=[("selected", SELECT_COLOR)],
            foreground=[("selected", FG_TEXT)]
        )

    def build_ui(self):
        # ===== FRAME KIRI =====
        frame_left = tk.LabelFrame(
            self.root, text="Form Barang",
            bg=BG_FRAME, fg=FG_TEXT, padx=10, pady=10
        )
        frame_left.pack(side=tk.LEFT, fill=tk.Y, padx=10, pady=10)

        tk.Label(frame_left, text="Nama Barang", bg=BG_FRAME, fg=FG_TEXT).pack(anchor="w")
        self.nama = tk.Entry(frame_left, bg=BG_ENTRY, fg=FG_TEXT, insertbackground=FG_TEXT)
        self.nama.pack(fill=tk.X, pady=5)

        tk.Label(frame_left, text="Stok", bg=BG_FRAME, fg=FG_TEXT).pack(anchor="w")
        self.stok = tk.Entry(frame_left, bg=BG_ENTRY, fg=FG_TEXT, insertbackground=FG_TEXT)
        self.stok.pack(fill=tk.X, pady=5)

        tk.Label(frame_left, text="Harga", bg=BG_FRAME, fg=FG_TEXT).pack(anchor="w")
        self.harga = tk.Entry(frame_left, bg=BG_ENTRY, fg=FG_TEXT, insertbackground=FG_TEXT)
        self.harga.pack(fill=tk.X, pady=5)

        tk.Button(
            frame_left, text="Tambah", bg=BTN_PRIMARY, fg="white",
            relief="flat", command=self.add
        ).pack(fill=tk.X, pady=5)

        tk.Button(
            frame_left, text="Update", bg=BTN_PRIMARY, fg="white",
            relief="flat", command=self.update
        ).pack(fill=tk.X, pady=5)

        tk.Button(
            frame_left, text="Reset", bg="#444", fg="white",
            relief="flat", command=self.reset
        ).pack(fill=tk.X, pady=5)

        # ===== FRAME KANAN =====
        frame_right = tk.Frame(self.root, bg=BG_DARK)
        frame_right.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=10, pady=10)

        # SEARCH
        frame_search = tk.Frame(frame_right, bg=BG_DARK)
        frame_search.pack(fill=tk.X, pady=5)

        tk.Label(frame_search, text="Cari Barang:", bg=BG_DARK, fg=FG_TEXT).pack(side=tk.LEFT)
        self.search_entry = tk.Entry(
            frame_search, bg=BG_ENTRY, fg=FG_TEXT, insertbackground=FG_TEXT
        )
        self.search_entry.pack(side=tk.LEFT, padx=5)

        tk.Button(
            frame_search, text="Cari", bg=BTN_PRIMARY, fg="white",
            relief="flat", command=self.search
        ).pack(side=tk.LEFT)

        tk.Button(
            frame_search, text="Semua Data", bg="#555", fg="white",
            relief="flat", command=self.load_data
        ).pack(side=tk.LEFT, padx=5)

        # TABLE
        columns = ("id", "nama", "stok", "harga")
        self.table = ttk.Treeview(frame_right, columns=columns, show="headings")

        self.table.heading("id", text="ID")
        self.table.heading("nama", text="Nama Barang")
        self.table.heading("stok", text="Stok")
        self.table.heading("harga", text="Harga")

        self.table.column("id", width=50, anchor="center")
        self.table.column("nama", width=260)
        self.table.column("stok", width=80, anchor="center")
        self.table.column("harga", width=140, anchor="e")

        self.table.pack(fill=tk.BOTH, expand=True, pady=10)
        self.table.bind("<<TreeviewSelect>>", self.select_row)

        tk.Button(
            frame_right, text="Hapus Data Terpilih",
            bg=BTN_DANGER, fg="white", relief="flat",
            command=self.delete
        ).pack(anchor="e")

    # ================= LOGIC =================
    def format_rp(self, n):
        return f"Rp {n:,}".replace(",", ".")

    def load_data(self):
        self.table.delete(*self.table.get_children())
        for b in self.db.get_all():
            self.table.insert("", "end", values=(
                b[0], b[1], b[2], self.format_rp(b[3])
            ))

    def add(self):
        if not self.nama.get() or not self.stok.get().isdigit() or not self.harga.get().isdigit():
            messagebox.showwarning("Error", "Input tidak valid")
            return
        self.db.insert(self.nama.get(), int(self.stok.get()), int(self.harga.get()))
        self.load_data()
        self.reset()

    def update(self):
        if not self.selected_id:
            return
        self.db.update(
            self.selected_id,
            self.nama.get(),
            int(self.stok.get()),
            int(self.harga.get())
        )
        self.load_data()
        self.reset()

    def delete(self):
        if not self.selected_id:
            return
        self.db.delete(self.selected_id)
        self.load_data()
        self.reset()

    def search(self):
        self.table.delete(*self.table.get_children())
        for b in self.db.search(self.search_entry.get()):
            self.table.insert("", "end", values=(
                b[0], b[1], b[2], self.format_rp(b[3])
            ))

    def select_row(self, event):
        item = self.table.item(self.table.selection())
        if not item["values"]:
            return

        self.selected_id = item["values"][0]
        self.nama.delete(0, tk.END)
        self.nama.insert(0, item["values"][1])

        self.stok.delete(0, tk.END)
        self.stok.insert(0, item["values"][2])

        harga = item["values"][3].replace("Rp ", "").replace(".", "")
        self.harga.delete(0, tk.END)
        self.harga.insert(0, harga)

    def reset(self):
        self.selected_id = None
        self.nama.delete(0, tk.END)
        self.stok.delete(0, tk.END)
        self.harga.delete(0, tk.END)


# ================= RUN =================
if __name__ == "__main__":
    root = tk.Tk()
    InventoryApp(root)
    root.mainloop()
