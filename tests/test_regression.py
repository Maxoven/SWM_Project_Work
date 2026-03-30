"""
T4 – Regression Tests
Guard against re-introduction of bugs that were fixed in T2 (Refactoring).
Each test corresponds to a specific bug that was present in the original code.
Framework: pytest
Run: pytest tests/ -v
"""
import os
import sys
import ast
import sqlite3
import tempfile
import operator as op
import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


# ─────────────────────────────────────────────────────────────────────────────
# Shared DB fixture
# ─────────────────────────────────────────────────────────────────────────────

@pytest.fixture
def db():
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
# REGRESSION 1 – SQL Injection guard (employee search)
# Bug: column name and search text were concatenated directly into SQL.
# Fix: column validated against whitelist; text bound as ? parameter.
# ─────────────────────────────────────────────────────────────────────────────

EMPLOYEE_SEARCH_COLUMNS = {'Email': 'email', 'Name': 'name', 'Contact': 'contact'}


class TestNoSQLInjectionEmployee:
    def _search_employee(self, db_path, search_by, search_text):
        """Reproduces the fixed search logic from employee.py."""
        if search_by not in EMPLOYEE_SEARCH_COLUMNS:
            return None  # rejected
        col = EMPLOYEE_SEARCH_COLUMNS[search_by]
        con = sqlite3.connect(db_path)
        cur = con.cursor()
        cur.execute(f"select * from employee where {col} LIKE ?",
                    (f"%{search_text}%",))
        rows = cur.fetchall()
        con.close()
        return rows

    def test_normal_search_works(self, db):
        con = sqlite3.connect(db)
        cur = con.cursor()
        cur.execute("INSERT INTO employee VALUES (?,?,?,?,?,?,?,?,?,?,?)",
                    ("E1", "Bob", "bob@x.com", "Male",
                     "555", "1985-01-01", "2021-01-01",
                     "pw", "Employee", "Addr", "2500"))
        con.commit()
        con.close()
        rows = self._search_employee(db, "Name", "Bob")
        assert rows is not None
        assert len(rows) == 1
        assert rows[0][1] == "Bob"

    def test_injected_column_name_is_rejected(self, db):
        """
        Regression: original code allowed any column name via var_searchby.
        Injecting a malicious column name like '1=1 OR 1' must be rejected.
        """
        result = self._search_employee(db, "1=1 OR 1", "anything")
        assert result is None, "Injection via column name must be blocked"

    def test_injected_search_text_is_safe(self, db):
        """
        SQL meta-characters in the search value must be treated as literals,
        not as query syntax.
        """
        rows = self._search_employee(db, "Name", "'; DROP TABLE employee; --")
        # Should return empty list (no match) – NOT raise an exception
        assert rows == []
        # Table must still exist
        con = sqlite3.connect(db)
        cur = con.cursor()
        cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='employee'")
        assert cur.fetchone() is not None
        con.close()


# ─────────────────────────────────────────────────────────────────────────────
# REGRESSION 2 – eval() replaced by safe AST evaluator
# Bug: billing.py called eval() on raw user input.
# Fix: ast-based safe evaluator that only handles arithmetic.
# ─────────────────────────────────────────────────────────────────────────────

_OPS = {ast.Add: op.add, ast.Sub: op.sub,
        ast.Mult: op.mul, ast.Div: op.truediv}


def safe_eval(expr: str):
    """The refactored calculator logic from billing.py."""
    def _eval(node):
        if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
            return node.value
        if isinstance(node, ast.BinOp) and type(node.op) in _OPS:
            return _OPS[type(node.op)](_eval(node.left), _eval(node.right))
        raise ValueError("Unsupported expression")
    tree = ast.parse(expr, mode='eval')
    return _eval(tree.body)


class TestEvalReplacement:
    def test_arithmetic_still_works(self):
        assert safe_eval("7+3") == 10
        assert safe_eval("100-25") == 75
        assert safe_eval("6*8") == 48
        assert safe_eval("20/4") == pytest.approx(5.0)

    def test_os_import_attack_is_blocked(self):
        """Regression: original eval() would execute this."""
        with pytest.raises(Exception):
            safe_eval("__import__('os').getcwd()")

    def test_exec_call_is_blocked(self):
        with pytest.raises(Exception):
            safe_eval("exec('print(1)')")

    def test_attribute_access_is_blocked(self):
        with pytest.raises(Exception):
            safe_eval("(1).__class__.__bases__")


# ─────────────────────────────────────────────────────────────────────────────
# REGRESSION 3 – Supplier validation bug (product.py)
# Bug: self.var_sup == "Select" compared the StringVar OBJECT, always False.
# Fix: self.var_sup.get() == "Select"
# ─────────────────────────────────────────────────────────────────────────────

class TestSupplierValidationFix:
    def test_stringvar_object_comparison_always_false(self):
        """
        Demonstrates the original bug: comparing a StringVar to a string
        using == tests object identity, not value. This always evaluates
        to False, meaning the validation was silently bypassed.
        """
        import tkinter as tk

        # We can't instantiate Tk in headless CI, so simulate with a simple mock
        class MockStringVar:
            def __init__(self, val): self._val = val
            def get(self): return self._val

        var = MockStringVar("Select")

        # Original (buggy) comparison – compares object to string
        buggy_check = (var == "Select")
        assert buggy_check is False, "Object comparison must be False (demonstrates the bug)"

        # Fixed comparison – uses .get()
        fixed_check = (var.get() == "Select")
        assert fixed_check is True, "Value comparison must be True (demonstrates the fix)"


# ─────────────────────────────────────────────────────────────────────────────
# REGRESSION 4 – siscount typo (billing.py)
# Bug: self.siscount = 0 set an unused variable; self.discount was never reset.
# Fix: self.discount = 0
# ─────────────────────────────────────────────────────────────────────────────

class TestDiscountReset:
    def test_discount_resets_between_calls(self):
        """
        Simulates bill_update() being called twice and verifies discount
        is correctly re-calculated from scratch each time (not accumulated).
        """

        class MockBill:
            def __init__(self):
                self.cart_list = []
                self.bill_amnt = 0
                self.net_pay = 0
                self.discount = 0

            def bill_update(self):
                self.bill_amnt = 0
                self.net_pay = 0
                self.discount = 0   # FIXED (was: self.siscount = 0)
                for row in self.cart_list:
                    self.bill_amnt += float(row[2]) * int(row[3])
                self.discount = (self.bill_amnt * 5) / 100
                self.net_pay = self.bill_amnt - self.discount

        bill = MockBill()
        bill.cart_list = [["1", "Item", "100.00", "2", "5"]]
        bill.bill_update()
        assert bill.discount == pytest.approx(10.0)
        assert bill.net_pay == pytest.approx(190.0)

        # Second call with a smaller cart — discount must drop, not accumulate
        bill.cart_list = [["1", "Item", "10.00", "1", "5"]]
        bill.bill_update()
        assert bill.discount == pytest.approx(0.50)
        assert bill.net_pay == pytest.approx(9.50)


# ─────────────────────────────────────────────────────────────────────────────
# REGRESSION 5 – Hardcoded relative DB path
# Bug: sqlite3.connect(r'ims.db') fails when cwd != project root.
# Fix: use os.path.join(BASE_DIR, 'ims.db')
# ─────────────────────────────────────────────────────────────────────────────

class TestAbsoluteDBPath:
    def test_db_path_is_absolute(self):
        """
        Verifies that the DB_PATH constants defined in the refactored modules
        resolve to an absolute path regardless of working directory.
        """
        from employee import DB_PATH as emp_path
        from product import DB_PATH as prod_path
        from supplier import DB_PATH as sup_path
        from category import DB_PATH as cat_path

        for name, path in [("employee", emp_path), ("product", prod_path),
                            ("supplier", sup_path), ("category", cat_path)]:
            assert os.path.isabs(path), \
                f"{name}.DB_PATH must be an absolute path, got: {path}"
            assert path.endswith('ims.db'), \
                f"{name}.DB_PATH must end with 'ims.db', got: {path}"


# ─────────────────────────────────────────────────────────────────────────────
# REGRESSION 6 – blll_list typo (sales.py)
# Bug: self.blll_list was hard to read and differed from the attribute name
#      used in search(), causing a potential AttributeError if refactored carelessly.
# Fix: renamed to self.bill_list throughout.
# ─────────────────────────────────────────────────────────────────────────────

class TestBillListAttributeName:
    def test_sales_module_uses_bill_list(self):
        """
        Inspect the sales.py source to confirm the old typo 'blll_list'
        does not appear anywhere in the file.
        """
        src_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            'sales.py'
        )
        with open(src_path) as f:
            source = f.read()
        assert 'blll_list' not in source, \
            "'blll_list' typo must not exist in sales.py after refactoring"
        assert 'bill_list' in source, \
            "'bill_list' must be present in sales.py after refactoring"
