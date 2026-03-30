"""
T4 – Unit Tests
Tests for individual methods that can run without the Tkinter GUI.
Framework: pytest  (pip install pytest)
Run: pytest tests/ -v
"""
import os
import sys
import sqlite3
import tempfile
import pytest

# Ensure project root is on the path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


# ─────────────────────────────────────────────────────────────────────────────
# Helpers / fixtures
# ─────────────────────────────────────────────────────────────────────────────

@pytest.fixture
def temp_db():
    """Create a fresh in-memory (or temp-file) SQLite database for each test."""
    fd, path = tempfile.mkstemp(suffix='.db')
    os.close(fd)
    con = sqlite3.connect(path)
    cur = con.cursor()
    cur.executescript("""
        CREATE TABLE employee (
            eid TEXT PRIMARY KEY, name TEXT, email TEXT, gender TEXT,
            contact TEXT, dob TEXT, doj TEXT, pass TEXT,
            utype TEXT, address TEXT, salary TEXT
        );
        CREATE TABLE supplier (
            invoice TEXT PRIMARY KEY, name TEXT, contact TEXT, desc TEXT
        );
        CREATE TABLE category (
            cid INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT UNIQUE
        );
        CREATE TABLE product (
            pid INTEGER PRIMARY KEY AUTOINCREMENT,
            Category TEXT, Supplier TEXT, name TEXT,
            price REAL, qty INTEGER, status TEXT
        );
    """)
    con.commit()
    con.close()
    yield path
    os.unlink(path)


# ─────────────────────────────────────────────────────────────────────────────
# Unit Test 1 – low_stock._get_threshold logic
# ─────────────────────────────────────────────────────────────────────────────

class TestGetThreshold:
    """
    Tests the threshold validation logic extracted from LowStockClass.
    We test the pure conversion function without spawning a Tkinter window.
    """

    def _validate(self, value):
        """Mirror of the validation logic in LowStockClass._get_threshold."""
        try:
            t = int(value)
            if t < 0:
                raise ValueError
            return t
        except ValueError:
            return None

    def test_valid_threshold_zero(self):
        assert self._validate("0") == 0

    def test_valid_threshold_positive(self):
        assert self._validate("10") == 10

    def test_negative_threshold_returns_none(self):
        assert self._validate("-1") is None

    def test_non_integer_threshold_returns_none(self):
        assert self._validate("abc") is None

    def test_float_string_returns_none(self):
        assert self._validate("3.5") is None


# ─────────────────────────────────────────────────────────────────────────────
# Unit Test 2 – safe calculator eval logic (billing.py – perform_cal)
# ─────────────────────────────────────────────────────────────────────────────

import ast
import operator as op

_OPS = {ast.Add: op.add, ast.Sub: op.sub,
        ast.Mult: op.mul, ast.Div: op.truediv}

def safe_eval(expr: str):
    """Extracted safe-eval logic from billing.py – perform_cal."""
    def _eval(node):
        if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
            return node.value
        if isinstance(node, ast.BinOp) and type(node.op) in _OPS:
            return _OPS[type(node.op)](_eval(node.left), _eval(node.right))
        raise ValueError("Unsupported")
    tree = ast.parse(expr, mode='eval')
    return _eval(tree.body)


class TestSafeEval:
    def test_addition(self):
        assert safe_eval("3+4") == 7

    def test_subtraction(self):
        assert safe_eval("10-3") == 7

    def test_multiplication(self):
        assert safe_eval("6*7") == 42

    def test_division(self):
        assert safe_eval("10/4") == pytest.approx(2.5)

    def test_chained_operations(self):
        assert safe_eval("2+3*4") == pytest.approx(14)

    def test_rejects_function_call(self):
        with pytest.raises((ValueError, AttributeError)):
            safe_eval("__import__('os').system('ls')")

    def test_rejects_string_literal(self):
        with pytest.raises((ValueError, AttributeError)):
            safe_eval("'hello'+'world'")

    def test_division_by_zero(self):
        with pytest.raises(ZeroDivisionError):
            safe_eval("1/0")


# ─────────────────────────────────────────────────────────────────────────────
# Unit Test 3 – DB: category CRUD (no GUI)
# ─────────────────────────────────────────────────────────────────────────────

class TestCategoryDB:
    def test_insert_category(self, temp_db):
        con = sqlite3.connect(temp_db)
        cur = con.cursor()
        cur.execute("INSERT INTO category(name) VALUES (?)", ("Electronics",))
        con.commit()
        cur.execute("SELECT name FROM category WHERE name=?", ("Electronics",))
        row = cur.fetchone()
        con.close()
        assert row is not None
        assert row[0] == "Electronics"

    def test_duplicate_category_raises(self, temp_db):
        con = sqlite3.connect(temp_db)
        cur = con.cursor()
        cur.execute("INSERT INTO category(name) VALUES (?)", ("Clothing",))
        con.commit()
        with pytest.raises(sqlite3.IntegrityError):
            cur.execute("INSERT INTO category(name) VALUES (?)", ("Clothing",))
            con.commit()
        con.close()

    def test_delete_category(self, temp_db):
        con = sqlite3.connect(temp_db)
        cur = con.cursor()
        cur.execute("INSERT INTO category(name) VALUES (?)", ("Furniture",))
        con.commit()
        cur.execute("SELECT cid FROM category WHERE name=?", ("Furniture",))
        cid = cur.fetchone()[0]
        cur.execute("DELETE FROM category WHERE cid=?", (cid,))
        con.commit()
        cur.execute("SELECT * FROM category WHERE cid=?", (cid,))
        assert cur.fetchone() is None
        con.close()


# ─────────────────────────────────────────────────────────────────────────────
# Unit Test 4 – DB: product stock status after sale
# ─────────────────────────────────────────────────────────────────────────────

class TestProductDB:
    def _seed_product(self, db_path, name, qty):
        con = sqlite3.connect(db_path)
        cur = con.cursor()
        cur.execute(
            "INSERT INTO product(Category,Supplier,name,price,qty,status) VALUES(?,?,?,?,?,?)",
            ("Cat", "Sup", name, 9.99, qty, "Active")
        )
        con.commit()
        pid = cur.lastrowid
        con.close()
        return pid

    def test_qty_decrements_correctly(self, temp_db):
        pid = self._seed_product(temp_db, "Widget", 10)
        con = sqlite3.connect(temp_db)
        cur = con.cursor()
        sold = 3
        new_qty = 10 - sold
        cur.execute("UPDATE product SET qty=? WHERE pid=?", (new_qty, pid))
        con.commit()
        cur.execute("SELECT qty FROM product WHERE pid=?", (pid,))
        assert cur.fetchone()[0] == 7
        con.close()

    def test_status_becomes_inactive_at_zero_qty(self, temp_db):
        pid = self._seed_product(temp_db, "LastItem", 1)
        con = sqlite3.connect(temp_db)
        cur = con.cursor()
        cur.execute("UPDATE product SET qty=0, status='Inactive' WHERE pid=?", (pid,))
        con.commit()
        cur.execute("SELECT qty, status FROM product WHERE pid=?", (pid,))
        row = cur.fetchone()
        assert row[0] == 0
        assert row[1] == "Inactive"
        con.close()

    def test_low_stock_query(self, temp_db):
        """Products with qty <= threshold appear in low-stock query."""
        for name, qty in [("A", 0), ("B", 3), ("C", 10), ("D", 5)]:
            self._seed_product(temp_db, name, qty)
        con = sqlite3.connect(temp_db)
        cur = con.cursor()
        cur.execute(
            "SELECT name FROM product WHERE qty <= ? ORDER BY qty ASC",
            (5,)
        )
        names = {r[0] for r in cur.fetchall()}
        con.close()
        assert names == {"A", "B", "D"}
        assert "C" not in names


# ─────────────────────────────────────────────────────────────────────────────
# Unit Test 5 – bill amount calculation logic
# ─────────────────────────────────────────────────────────────────────────────

class TestBillCalculation:
    """Mirrors the bill_update() arithmetic in billClass."""

    def _calculate(self, cart):
        """cart: list of [pid, name, price_str, qty_str, stock_str]"""
        bill_amnt = sum(float(row[2]) * int(row[3]) for row in cart)
        discount = (bill_amnt * 5) / 100
        net_pay = bill_amnt - discount
        return bill_amnt, discount, net_pay

    def test_single_item(self):
        cart = [["1", "Apple", "2.00", "3", "10"]]
        amnt, disc, net = self._calculate(cart)
        assert amnt == pytest.approx(6.00)
        assert disc == pytest.approx(0.30)
        assert net == pytest.approx(5.70)

    def test_multiple_items(self):
        cart = [
            ["1", "A", "10.00", "2", "5"],
            ["2", "B", "5.00",  "4", "8"],
        ]
        amnt, disc, net = self._calculate(cart)
        assert amnt == pytest.approx(40.00)
        assert disc == pytest.approx(2.00)
        assert net == pytest.approx(38.00)

    def test_empty_cart(self):
        amnt, disc, net = self._calculate([])
        assert amnt == 0
        assert disc == 0
        assert net == 0


# ─────────────────────────────────────────────────────────────────────────────
# Unit Test 6 – supplier search (parameterized query, no injection possible)
# ─────────────────────────────────────────────────────────────────────────────

class TestSupplierSearch:
    def test_search_by_invoice_found(self, temp_db):
        con = sqlite3.connect(temp_db)
        cur = con.cursor()
        cur.execute("INSERT INTO supplier VALUES (?,?,?,?)",
                    ("INV001", "ACME Corp", "555-1234", "General goods"))
        con.commit()
        cur.execute("SELECT * FROM supplier WHERE invoice=?", ("INV001",))
        row = cur.fetchone()
        con.close()
        assert row is not None
        assert row[1] == "ACME Corp"

    def test_search_by_invoice_not_found(self, temp_db):
        con = sqlite3.connect(temp_db)
        cur = con.cursor()
        cur.execute("SELECT * FROM supplier WHERE invoice=?", ("NOTEXIST",))
        row = cur.fetchone()
        con.close()
        assert row is None
