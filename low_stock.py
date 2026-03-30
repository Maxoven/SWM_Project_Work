from tkinter import *
from tkinter import ttk, messagebox, filedialog
import sqlite3
import os
import time

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, 'ims.db')

DEFAULT_THRESHOLD = 5


class LowStockClass:
    def __init__(self, root):
        self.root = root
        self.root.title("Low-Stock Alert Report")
        self.root.geometry("900x560+250+150")
        self.root.config(bg="white")
        self.root.resizable(False, False)
        self.root.focus_force()

        self.var_threshold = StringVar(value=str(DEFAULT_THRESHOLD))

        # ── Title ──────────────────────────────────────────────────────────
        Label(
            self.root,
            text="Low-Stock Alert Report",
            font=("goudy old style", 22, "bold"),
            bg="#c0392b", fg="white", bd=3, relief=RIDGE
        ).pack(side=TOP, fill=X, padx=8, pady=(10, 4))

        # ── Controls ───────────────────────────────────────────────────────
        ctrl_frame = Frame(self.root, bg="white", bd=2, relief=RIDGE)
        ctrl_frame.pack(fill=X, padx=8, pady=4)

        Label(ctrl_frame, text="Alert Threshold (qty ≤):",
              font=("times new roman", 14), bg="white").pack(side=LEFT, padx=10, pady=6)

        Entry(ctrl_frame, textvariable=self.var_threshold,
              font=("times new roman", 14), bg="lightyellow", width=6
              ).pack(side=LEFT, padx=4)

        Button(ctrl_frame, text="Refresh", command=self.show,
               font=("times new roman", 13, "bold"),
               bg="#2980b9", fg="white", cursor="hand2"
               ).pack(side=LEFT, padx=8)

        Button(ctrl_frame, text="Export Report", command=self.export,
               font=("times new roman", 13, "bold"),
               bg="#27ae60", fg="white", cursor="hand2"
               ).pack(side=LEFT, padx=4)

        self.lbl_count = Label(ctrl_frame, text="",
                               font=("times new roman", 13, "bold"),
                               bg="white", fg="#c0392b")
        self.lbl_count.pack(side=RIGHT, padx=14)

        # ── Table ──────────────────────────────────────────────────────────
        table_frame = Frame(self.root, bd=3, relief=RIDGE)
        table_frame.pack(fill=BOTH, expand=True, padx=8, pady=8)

        scrolly = Scrollbar(table_frame, orient=VERTICAL)
        scrollx = Scrollbar(table_frame, orient=HORIZONTAL)

        self.tree = ttk.Treeview(
            table_frame,
            columns=("pid", "name", "category", "supplier", "price", "qty", "status"),
            yscrollcommand=scrolly.set,
            xscrollcommand=scrollx.set
        )
        scrollx.pack(side=BOTTOM, fill=X)
        scrolly.pack(side=RIGHT, fill=Y)
        scrollx.config(command=self.tree.xview)
        scrolly.config(command=self.tree.yview)

        self.tree.heading("pid",      text="P ID")
        self.tree.heading("name",     text="Product Name")
        self.tree.heading("category", text="Category")
        self.tree.heading("supplier", text="Supplier")
        self.tree.heading("price",    text="Price")
        self.tree.heading("qty",      text="Quantity")
        self.tree.heading("status",   text="Status")
        self.tree["show"] = "headings"

        self.tree.column("pid",      width=55,  anchor=CENTER)
        self.tree.column("name",     width=200)
        self.tree.column("category", width=130)
        self.tree.column("supplier", width=130)
        self.tree.column("price",    width=90,  anchor=CENTER)
        self.tree.column("qty",      width=80,  anchor=CENTER)
        self.tree.column("status",   width=90,  anchor=CENTER)

        # Highlight rows with qty == 0 in red
        self.tree.tag_configure("out_of_stock", background="#f5b7b1")
        self.tree.tag_configure("low_stock",    background="#fdebd0")

        self.tree.pack(fill=BOTH, expand=True)

        self.show()

    # ─────────────────────────────────────────────────────────────────────
    def _get_threshold(self):
        try:
            t = int(self.var_threshold.get())
            if t < 0:
                raise ValueError
            return t
        except ValueError:
            messagebox.showerror("Error",
                                 "Threshold must be a non-negative integer.",
                                 parent=self.root)
            return None

    def show(self):
        threshold = self._get_threshold()
        if threshold is None:
            return
        con = sqlite3.connect(database=DB_PATH)
        cur = con.cursor()
        try:
            cur.execute(
                "SELECT pid, name, Category, Supplier, price, qty, status "
                "FROM product WHERE qty <= ? ORDER BY qty ASC",
                (threshold,)
            )
            rows = cur.fetchall()
            self.tree.delete(*self.tree.get_children())
            for row in rows:
                tag = "out_of_stock" if int(row[5]) == 0 else "low_stock"
                self.tree.insert('', END, values=row, tags=(tag,))
            count = len(rows)
            self.lbl_count.config(
                text=f"{count} product{'s' if count != 1 else ''} at or below threshold"
            )
        except Exception as ex:
            messagebox.showerror("Error", f"Error: {str(ex)}", parent=self.root)
        finally:
            con.close()

    def export(self):
        threshold = self._get_threshold()
        if threshold is None:
            return
        rows = [self.tree.item(iid)['values'] for iid in self.tree.get_children()]
        if not rows:
            messagebox.showinfo("Export",
                                "No low-stock items to export.", parent=self.root)
            return

        save_path = filedialog.asksaveasfilename(
            parent=self.root,
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")],
            initialfile=f"low_stock_report_{time.strftime('%Y%m%d_%H%M%S')}.txt"
        )
        if not save_path:
            return

        header = (
            f"Low-Stock Alert Report\n"
            f"Generated : {time.strftime('%d/%m/%Y  %H:%M:%S')}\n"
            f"Threshold : qty <= {threshold}\n"
            f"{'=' * 70}\n"
            f"{'PID':<6}{'Name':<22}{'Category':<16}{'Supplier':<16}"
            f"{'Price':>8}{'Qty':>6}  {'Status'}\n"
            f"{'=' * 70}\n"
        )
        lines = []
        for r in rows:
            lines.append(
                f"{str(r[0]):<6}{str(r[1]):<22}{str(r[2]):<16}{str(r[3]):<16}"
                f"{str(r[4]):>8}{str(r[5]):>6}  {str(r[6])}"
            )
        content = header + "\n".join(lines) + f"\n{'=' * 70}\nTotal: {len(lines)} item(s)\n"

        try:
            with open(save_path, 'w') as f:
                f.write(content)
            messagebox.showinfo("Export",
                                f"Report saved to:\n{save_path}", parent=self.root)
        except Exception as ex:
            messagebox.showerror("Error",
                                 f"Could not save file: {str(ex)}", parent=self.root)


if __name__ == "__main__":
    root = Tk()
    obj = LowStockClass(root)
    root.mainloop()
